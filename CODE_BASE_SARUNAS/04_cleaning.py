from pathlib import Path
import re
import unicodedata
import pandas as pd

try:
    import stanza
except ImportError:
    raise SystemExit("Please install stanza first: pip install stanza")

stanza.download('lv', processors='tokenize', verbose=False)
nlp = stanza.Pipeline('lv', processors='tokenize', use_gpu=False, tokenize_no_ssplit=True, verbose=False)


input_path = Path(r"C:\Users\JurisFedotovs\Desktop\RTU\MASTER\Āgenskalna_klīnika_sarunas\EXPERIMENT\CODE_BASE\DATA\03_lv_sarunas.csv")
stopword_file = Path(r"C:\Users\JurisFedotovs\Desktop\RTU\MASTER\Āgenskalna_klīnika_sarunas\EXPERIMENT\CODE_BASE\DATA\stop_words_latvian.txt")
output_path = Path(r"C:\Users\JurisFedotovs\Desktop\RTU\MASTER\Āgenskalna_klīnika_sarunas\EXPERIMENT\CODE_BASE\DATA\04_lv_sarunas_cleaned.csv")

if not input_path.exists():
    raise SystemExit(f"Input file not found: {input_path}")
if not stopword_file.exists():
    raise SystemExit(f"Stopword file not found: {stopword_file}")

###### Stopwords ######
with stopword_file.open("r", encoding="utf-8-sig") as f:
    stopwords = {line.strip().lower() for line in f if line.strip()}

print(f"Loaded {len(stopwords)} stopwords from file")
print(stopwords)
###### Regular expression patterns ######
regex = {
    "url": re.compile(r"http\S+|www\.\S+", re.IGNORECASE),

    ##### Emoji clean #####
    "emoji": re.compile(r"[\U00010000-\U0010FFFF]"),

    "artifacts": re.compile(
        r"(?i)^reply this message$|^forwarded from.*$|^sent from my iphone$|^view in telegram$"
    ),
    "newline_artifact": re.compile(r"^n[ a-zāčēģīķļņšūž]", re.IGNORECASE),
    "collapse_ws": re.compile(r"\s+"),
}

###### Character maps ######
SMART_QUOTES = dict.fromkeys(map(ord, "“”„«»‚‘’`´ˮ"), " ")
DASHES_BULLETS = dict.fromkeys(map(ord, "–—−•·•…"), " ")

###### Cleaning ######
def clean_text(text: str) -> str:
    if pd.isna(text) or not text.strip():
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = text.translate(SMART_QUOTES).translate(DASHES_BULLETS)
    text = text.replace("\\n", " ").replace("\\t", " ").replace("\xa0", " ")

    text = regex["url"].sub(" ", text)
    text = regex["emoji"].sub(" ", text)
    text = regex["artifacts"].sub(" ", text)
    text = re.sub(r"[#/]", " ", text)

    ##### Tokenize #####
    tokens = [t.text for sent in nlp(text).sentences for t in sent.tokens]

    ##### Filter stopwords #####
    tokens_cleaned = [
        tok for tok in tokens
        if tok.lower() not in stopwords
        and not regex["newline_artifact"].match(tok.lower())
    ]

    if not tokens_cleaned:
        return ""

    result = " ".join(tokens_cleaned)
    result = regex["collapse_ws"].sub(" ", result).strip()
    result = re.sub(r"[^\w\sĀ-ž]", "", result)
    result = regex["collapse_ws"].sub(" ", result).lower().strip()

    return result

###### Main ######
print(f" Reading: {input_path}")
df = pd.read_csv(input_path, encoding="utf-8-sig")

if "content" not in df.columns:
    raise SystemExit(f"Column 'content' not found. Available columns: {list(df.columns)}")

print("Cleaning 'content' column…")
df["content"] = df["content"].apply(clean_text)
df["content"] = df["content"].str.strip()
df = df[df["content"].astype(bool)].copy()

###### Save cleaned file ######
df.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f" Cleaned file saved to:\n{output_path}")
print(f" Remaining rows after cleaning: {len(df)}")
print()
print("DONE")