from pathlib import Path
import pandas as pd
from collections import Counter
import stanza
import re
import sys
import matplotlib.pyplot as plt
from wordcloud import WordCloud


INPUT_FILE = Path(__file__).parent / "DATA" / "03_lv_main_cleaned.csv"

OUTPUT_FILE = INPUT_FILE.with_name("04_lv_freaquencies.csv")
WORDCLOUD_PNG = INPUT_FILE.with_name("04_lv_wordcloud.png")

##### base parameters #####
TOP_N_PRINT = 20
TOP_N_WC = 100
FREQ_DECIMALS = 3

##### Init Latvian Stanza lemmatizer #####
stanza.download("lv", processors="tokenize,pos,lemma", verbose=False)
nlp = stanza.Pipeline(
    "lv",
    processors="tokenize,pos,lemma",
    tokenize_no_ssplit=True,
    use_gpu=False,
    verbose=False
)

##### Tokenizer #####
LATVIAN_WORD_RE = re.compile(r"\b[a-zāčēģīķļņšūž]{2,}\b", re.IGNORECASE)

def simple_tokenize(text):
    
    if pd.isna(text):
        return []
    return LATVIAN_WORD_RE.findall(str(text).lower())

def lemmatize_words(words):
    
    if not words:
        return []

    text = " ".join(words)
    doc = nlp(text)

    lemmas = []
    for sent in doc.sentences:
        for w in sent.words:
            lemma = w.lemma.lower()
            if lemma:
                lemmas.append(lemma)
    return lemmas

##### Main #####
def main():
    if not INPUT_FILE.exists():
        print(f"File not found:\n{INPUT_FILE}")
        sys.exit(1)

    ###### Read CSV #####
    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")
    if "content" not in df.columns:
        print("Column 'content' not found in the CSV.")
        sys.exit(1)

    ###### Collect tokens #####
    raw_tokens = []
    for t in df["content"]:
        raw_tokens.extend(simple_tokenize(t))

    if not raw_tokens:
        print("No tokens found in text.")
        sys.exit(0)

    print(f"Raw tokens (pre-lemmatization): {len(raw_tokens):,}")

    ##### Lemmatize #####
    lemmas = lemmatize_words(raw_tokens)
    total_tokens = len(lemmas)

    print(f"Lemmatized tokens: {total_tokens:,}")

    ##### Count lemma frequencies #####
    counts = Counter(lemmas)

    ##### Build output DataFrame #####
    out = pd.DataFrame(counts.most_common(), columns=["lemma", "count"])
    out["freq"] = out["count"] / total_tokens
    out["freq_per_1000"] = (out["freq"] * 1000).round(FREQ_DECIMALS)

    ###### Save output CSV ######
    out.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"\nTotal lemma tokens: {total_tokens:,}")
    print(f"Saved to: {OUTPUT_FILE}")

    ##### Print top 20 words #####
    most_common_20 = counts.most_common(TOP_N_PRINT)

    print("\n🔝 Top 20 Most Frequent Latvian Lemmas (per 1,000 words):\n")
    print(f"{'Rank':<5} {'Lemma':<20} {'Count':<8} {'Freq':<10} {'Per1K':<10}")
    print("-" * 65)

    for i, (word, count) in enumerate(most_common_20, start=1):
        freq = round(count / total_tokens, FREQ_DECIMALS)
        per_1000 = round(freq * 1000, FREQ_DECIMALS)
        print(f"{i:<5} {word:<20} {count:<8} {freq:<10} {per_1000:<10}")

   ##### Visualizations #####

    ##### Bar chart #####
    top20_df = pd.DataFrame(most_common_20, columns=["lemma", "count"])

    plt.figure(figsize=(10, 6))
    plt.barh(top20_df["lemma"], top20_df["count"])
    plt.gca().invert_yaxis()
    plt.title("Top 20 Lemmatized Latvian Words (Āgenskalna klīnika sarunas)", fontsize=13)
    plt.xlabel("Count")
    plt.ylabel("Lemma")
    plt.tight_layout()
    plt.show()

    ##### Word cloud #####
    most_common_wc = counts.most_common(TOP_N_WC)
    wc_dict = dict(most_common_wc)

    if not wc_dict:
        print("Word cloud skipped: no tokens.")
    else:
        font_path = r"C:\Windows\Fonts\segoeui.ttf"
        wc = WordCloud(
            width=1200,
            height=600,
            background_color="white",
            colormap="viridis",
            max_words=TOP_N_WC,
            font_path=font_path,
        ).generate_from_frequencies(wc_dict)

        plt.figure(figsize=(12, 6))
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.title(f"Word Cloud (Top {TOP_N_WC} Lemmas)", fontsize=14)
        plt.tight_layout()
        plt.show()



if __name__ == "__main__":
    main()
print("DONE")