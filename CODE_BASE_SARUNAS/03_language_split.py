
from pathlib import Path
import pandas as pd
import re


input_path = Path(r"C:\Users\JurisFedotovs\Desktop\RTU\MASTER\Āgenskalna_klīnika_sarunas\EXPERIMENT\CODE_BASE\DATA\02_delete_dubicates.csv")
out_lv = input_path.parent / "03_lv_sarunas.csv"
out_en = input_path.parent / "03_eng_sarunas.csv"
out_ru = input_path.parent / "03_ru_sarunas.csv"
out_de = input_path.parent / "03_de_sarunas.csv"


print(f"Reading: {input_path}")
df = pd.read_csv(input_path, encoding="utf-8-sig")

if "content" not in df.columns:
    raise SystemExit("Column 'content' not found in the input file!")

df = df[df["content"].notna()]
df = df[df["content"].str.strip().astype(bool)]
df = df[~df["content"].str.strip().str.match(r"^In reply to this message$", case=False)]
df = df[~df["content"].str.strip().isin(["Photo", "Video", "Voice message", "Sticker", "Contact", "Audio", "File", "Call"])]

##### Regular expressions patterns #####
re_cyrillic = re.compile(r"[\u0400-\u04FF]")
re_lv_diacritics = re.compile(r"[āčēģīķļņšūžĀČĒĢĪĶĻŅŠŪŽ]")
re_words = re.compile(r"\b[a-zA-Zāčēģīķļņšūž]+\b", re.IGNORECASE)

##### Funkcion words in each language #####
LV_FUN = {
    "un","ir","vai","bet","kad","ka","par","ar","no","uz","pie","kā","tiek","bija",
    "es","tu","viņš","viņa","mēs","jūs","viņi","tā","te","tur","šodien","vakar","rīt",
    "ne","tas","tikai","šis","arī","nekā","vēl","tik","būs","nav","lai","šajā","tajā",
    "tādēļ","tāpēc","jo","visi","visu","man","tev","mūsu","jūsu","tekošs"
}

EN_FUN = {
    "the","and","or","but","that","this","is","are","was","were","to","of","in","on",
    "for","with","as","it","be","by","at","from","i","you","he","she","we","they","not",
    "have","has","do","does","did","can","would","should","will","a","an","if"
}

DE_FUN = {
    "und","oder","aber","dass","dies","ist","sind","war","waren","zu","von","in","auf",
    "für","mit","als","es","sein","bei","aus","dem","der","die","das","ein","eine",
    "nicht","habe","hat","tun","wird","würde","sollte","wenn","man","wir","sie","ihr"
}

##### Clean links #####
def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""

    t = text.strip()
    if not t:
        return ""

    t = re.sub(r"(https?|ftp|www)\S+", "", t)
    t = re.sub(r"\S*(?:\.com|\.org|\.net|\.info|\.biz|\.tv|\.lv|\.ru|\.us|\.de|\.uk|\.eu|\.gov|\.edu)\S*", "", t)

    return t.strip()

##### Detect language #####
def detect_lang(text: str):
    """Stronger Latvian detection, prevents LV text from being classified as EN."""
    if not isinstance(text, str) or len(text.strip()) < 3:
        return "lv", 0.3

    text_clean = clean_text(text)

    ###### Russian: Cyrillic check #####
    cyr = len(re.findall(re_cyrillic, text_clean))
    total = len(re.findall(r"[A-Za-zĀ-ž\u0400-\u04FF]", text_clean))
    if total > 0 and cyr / total > 0.5:
        return "ru", 0.98

    tokens = [w.lower() for w in re_words.findall(text_clean)]
    if not tokens:
        return "lv", 0.3

    lv_hits = sum(w in LV_FUN for w in tokens)
    en_hits = sum(w in EN_FUN for w in tokens)
    de_hits = sum(w in DE_FUN for w in tokens)

    lv_ratio = lv_hits / len(tokens)
    en_ratio = en_hits / len(tokens)
    de_ratio = de_hits / len(tokens)

    lv_diacritic_count = len(re.findall(re_lv_diacritics, text_clean))

    ###### Rules for Latvian priority ######

 
    if lv_diacritic_count > 0:
        return "lv", 0.99
    if lv_hits > 0 and lv_ratio >= en_ratio:
        return "lv", 0.9

    ###### English detection ######
    if en_ratio > 0.25 and en_ratio > lv_ratio * 1.5:
        return "en", 0.95

    ###### German detection ######
    if de_ratio > 0.25 and de_ratio > max(en_ratio, lv_ratio):
        return "de", 0.95

    ###### Short text fallback ######
    if len(tokens) < 10:
        return "lv", 0.7
    if lv_hits >= max(en_hits, de_hits):
        return "lv", 0.8
    if en_hits >= max(lv_hits, de_hits):
        return "en", 0.85
    if de_hits >= max(lv_hits, en_hits):
        return "de", 0.85

    return "lv", 0.6


print("Detecting languages…")
df["lang"], df["lang_conf"] = zip(*df["content"].map(detect_lang))

##### Split by language #####
df_lv = df[df["lang"] == "lv"].copy()
df_en = df[df["lang"] == "en"].copy()
df_ru = df[df["lang"] == "ru"].copy()
df_de = df[df["lang"] == "de"].copy()

for subset, path in [
    (df_lv, out_lv), (df_en, out_en), (df_ru, out_ru), (df_de, out_de)
]:
    subset.drop(columns=["lang", "lang_conf"], inplace=True)
    subset["content"] = subset["content"].map(clean_text)
    subset.to_csv(path, index=False, encoding="utf-8-sig")

##### Output #####
print("\nLanguage distribution (counts and %):")
counts = df["lang"].value_counts()
percent = df["lang"].value_counts(normalize=True) * 100
summary = pd.DataFrame({"count": counts, "percent": percent.map("{:.1f}%".format)})
print(summary)
print()
print(f"\nLatvian (lv): {len(df_lv)} rows → {out_lv}")
print(f"English (en): {len(df_en)} rows → {out_en}")
print(f"Russian (ru): {len(df_ru)} rows → {out_ru}")
print(f"German  (de): {len(df_de)} rows → {out_de}")
print()
print("DONE")