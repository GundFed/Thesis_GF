from pathlib import Path
import pandas as pd
import stanza
from collections import Counter, defaultdict
import re

##### Setup Stanza #####
stanza.download('lv', verbose=False)
nlp = stanza.Pipeline("lv", processors="tokenize,pos,lemma", use_gpu=False, tokenize_no_ssplit=True, verbose=False)


input_path = Path(r"C:\Users\JurisFedotovs\Desktop\RTU\MASTER\Āgenskalna_klīnika_sarunas\EXPERIMENT\CODE_BASE\DATA\04_lv_sarunas_cleaned.csv")
TEXT_COL = "content"

##### Target lemma #####
TARGET_LEMMA = "vakcinēt"  # or "potēt" or "vakcinēt"

TOP_N = 10

##### Load data #####
print(f" Reading: {input_path}")
df = pd.read_csv(input_path, encoding="utf-8-sig")
if TEXT_COL not in df.columns:
    raise SystemExit(f"Column '{TEXT_COL}' not found!")

##### Lemmatization + Trigram extraction #####
def lemmatize_text(text):
    if not isinstance(text, str) or not text.strip():
        return []
    doc = nlp(text)
    return [word.lemma.lower() for sent in doc.sentences for word in sent.words]

def extract_trigrams_with_target(lemmas, target):
    return [
        f"{lemmas[i-1]} {lemmas[i]} {lemmas[i+1]}"
        for i in range(1, len(lemmas) - 1)
        if lemmas[i] == target
    ]

##### Main #####
print(f"Extracting trigrams with target in middle: {TARGET_LEMMA}")
trigram_counter = Counter()
trigram_to_rows = defaultdict(list)

for idx, text in df[TEXT_COL].fillna("").items():
    lemmas = lemmatize_text(text)
    trigrams = extract_trigrams_with_target(lemmas, TARGET_LEMMA)
    trigram_counter.update(trigrams)
    for trigram in trigrams:
        trigram_to_rows[trigram].append(text)

##### Output #####
print(f"\nTarget lemma: {TARGET_LEMMA.upper()}")
top_trigrams = trigram_counter.most_common(TOP_N)

if not top_trigrams:
    print(" No trigrams found.")
else:
    for trigram, count in top_trigrams:
        print(f"  {trigram:<40} {count}")

    print("\n Full original comments for top 5 trigrams:\n")
    for trigram, _ in top_trigrams[:5]:
        print(f"{trigram.upper()}")
        for i, comment in enumerate(trigram_to_rows[trigram][:3], start=1):
            print(f"  {i}. {comment}")
        print()

print("DONE")
