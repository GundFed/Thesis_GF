if __name__ == "__main__":
    from pathlib import Path
    import pandas as pd
    import re
    from gensim import corpora
    from gensim.models import LdaModel, CoherenceModel
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    from collections import Counter

    import stanza
    import pyLDAvis.gensim_models as gensimvis
    import pyLDAvis

   
    INPUT_PATH = Path(__file__).parent / "DATA" / "03_lv_main_cleaned.csv"

    OUTPUT_PATH = INPUT_PATH.with_name("06_LDA_topic_vizualization.csv")
    HTML_OUTPUT = Path(__file__).parent / "DATA" / "06_lda_5topics_cleaned.html"    



    TEXT_COL = "content"

    #### Improved hyperparameters #####
    NUM_TOPICS = 3
    MIN_WORDS = 3
    MIN_TERM_DF = 11
    MAX_TERM_DF = 0.5
    PASSES = 20
    RANDOM_STATE = 42

    print(f"Using NUM_TOPICS = {NUM_TOPICS}")

    
    if not INPUT_PATH.exists():
        raise SystemExit(f"File not found: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
    if TEXT_COL not in df.columns:
        raise SystemExit(f"Column '{TEXT_COL}' not found. Available: {df.columns.tolist()}")

    print(f"Loaded {len(df)} rows from {INPUT_PATH}")

    ##### Preprocessing #####
    df = df.drop_duplicates(subset=[TEXT_COL])
    df[TEXT_COL] = df[TEXT_COL].astype(str).str.strip()
    df = df[df[TEXT_COL].str.len() > 0]
    df = df[df[TEXT_COL].str.split().str.len() >= MIN_WORDS]

    ##### Initialize Stanza #####
    print("Loading Stanza Latvian NLP pipeline...")
    stanza.download("lv")
    nlp = stanza.Pipeline(lang="lv", processors="tokenize,pos,lemma", use_gpu=False)

    ##### Lemmatization #####
    def lemmatize(text):
        doc = nlp(text)
        return [word.lemma.lower() for sent in doc.sentences for word in sent.words]

    print("Lemmatizing content (this may take time)...")
    tokenized_docs = df[TEXT_COL].map(lemmatize).tolist()

    ##### No stopword removal #####
    filtered_docs = tokenized_docs

    ##### Show frequent lemmas #####
    all_words = [w for doc in filtered_docs for w in doc]
    print("\nTop 20 lemmatized words:")
    print(Counter(all_words).most_common(20))

    ##### Dictionary and corpus #####
    dictionary = corpora.Dictionary(filtered_docs)
    dictionary.filter_extremes(no_below=MIN_TERM_DF, no_above=MAX_TERM_DF)
    corpus = [dictionary.doc2bow(text) for text in filtered_docs]

    ##### Train LDA Model #####
    print("\nTraining LDA model...")
    lda_model = LdaModel(
        corpus=corpus,
        num_topics=NUM_TOPICS,
        id2word=dictionary,
        passes=PASSES,
        random_state=RANDOM_STATE
    )

    print(f"Model trained with {lda_model.num_topics} topics.")

    ##### Coherence score #####
    print("Calculating coherence score...")
    coherence_model = CoherenceModel(model=lda_model, texts=filtered_docs, dictionary=dictionary, coherence='c_v')
    coherence_score = coherence_model.get_coherence()
    print(f"Coherence Score (c_v): {coherence_score:.4f}")

    ##### Print topics #####
    topics = lda_model.print_topics(num_words=10)
    print("\n📚 Top Topics:")
    for topic in topics:
        print(f"• Topic {topic[0]}: {topic[1]}")

    ##### Bar Chart Plot #####
    fig, axs = plt.subplots(NUM_TOPICS, 1, figsize=(10, 2.5 * NUM_TOPICS), constrained_layout=True)
    colors = list(mcolors.TABLEAU_COLORS.values())

    for i, topic in enumerate(topics):
        topic_words = re.findall(r'"([^"]+)"', topic[1])
        weights = [float(w) for w in re.findall(r'([\d.]+)\*"', topic[1])]
        axs[i].barh(topic_words[::-1], weights[::-1], color=colors[i % len(colors)])
        axs[i].set_title(f"Topic #{i+1}")
        axs[i].set_xlim(0, max(weights) * 1.2)

    plt.suptitle("Top 10 Words in Each LDA Topic (Lemmatized)", fontsize=14)
    plt.show()

    ##### Interactive pyLDAvis HTML #####
    print("Generating interactive visualization...")
    vis_data = gensimvis.prepare(lda_model, corpus, dictionary)
    pyLDAvis.save_html(vis_data, str(HTML_OUTPUT))
    print(f"Saved interactive topic visualization to: {HTML_OUTPUT}")

    ##### Assign dominant topic to each comment #####
    def get_dominant_topic(bow):
        topics = lda_model.get_document_topics(bow)
        if not topics:
            return None
        return max(topics, key=lambda x: x[1])[0]

    df["topic"] = [get_dominant_topic(bow) for bow in corpus]

    ##### Save topic-labeled comments to CSV #####
    df_out = df[[TEXT_COL, "topic"]]
    df_out.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"Saved topic-labeled comments to: {OUTPUT_PATH}")
    print("DONE")
