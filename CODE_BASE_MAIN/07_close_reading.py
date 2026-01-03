from pathlib import Path
import pandas as pd
import stanza

 
input_path = Path(__file__).parent / "DATA" / "01_Telegram-Āgenskalna_klīnika-main.csv"
output_path = Path(__file__).parent / "DATA" / "07_close_reading.csv"


df = pd.read_csv(input_path, encoding="utf-8")

required_cols = {"message_id", "timestamp", "sender", "fwd", "reply", "content"}
if not required_cols.issubset(df.columns):
    raise ValueError(f"CSV must contain columns: {required_cols}")

print("CSV loaded successfully:", len(df), "rows")


##### Initialize Latvian NLP #####
stanza.download("lv")  # run once, then comment out on next runs
nlp = stanza.Pipeline("lv", processors="tokenize,pos,lemma")

##### Target lemma list for Latvian vaccine-related expressions #####
TARGET_LEMMAS = {
    "vakcinēt", "potēt",
    "vakcinācija", "potēšana"
}

##### Check if any lemma in a text matches TARGET_LEMMAS #####
def has_target_lemma(text: str) -> bool:
    if not isinstance(text, str) or not text.strip():
        return False

    doc = nlp(text)

    for sent in doc.sentences:
        for word in sent.words:
            lemma = word.lemma.lower() if word.lemma else ""
            if lemma in TARGET_LEMMAS:
                return True

    return False

##### Filter rows #####
print("Processing… this may take a few minutes…")

df["match"] = df["content"].apply(has_target_lemma)
filtered_df = df[df["match"] == True].copy()
filtered_df.drop(columns=["match"], inplace=True)

print("Matched rows:", len(filtered_df))

##### Save as CSV #####
filtered_df.to_csv(output_path, index=False, encoding="utf-8-sig")
print("Output saved to:", output_path)
print("DONE")
