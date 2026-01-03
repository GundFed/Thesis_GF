
# Read Me: Telegram Data Analysis Pipeline

This project processes and analyzes Telegram chat data from the "Āgenskalna klīnika" channel. The pipeline consists of several Python scripts, each responsible for a specific stage of data extraction, cleaning, analysis, and visualization. Below is an overview of each script and its purpose.

## Pipeline Overview

### 1. 01-html-csv.py
- **Purpose:** Extracts messages from Telegram HTML export files and saves them as a CSV file.
- **Input:** `MESSAGES/messages.html`, `MESSAGES/messages2.html`, ... (not included in repo due to data sensitivity)
- **Output:** `DATA/01_anonymized_messages.csv`
- **Details:** Filters messages by sender (e.g., "Āgenskalna klīnika").

### 2. 02_delete_dublicates.py
- **Purpose:** Removes duplicate entries from the main CSV file.
- **Input:** `DATA/01_anonymized_messages.csv`
- **Output:** `DATA/02_delete_dubicates.csv`
- **Details:** Ensures data quality by removing repeated messages or records.

### 3. 03_language_split.py
- **Purpose:** Splits the main CSV into separate files by language (Latvian, English, Russian).
- **Input:** `DATA/02_delete_dubicates.csv`
- **Output:**
  - `DATA/03_lv_sarunas.csv`
  - `DATA/03_eng_sarunas.csv`
  - `DATA/03_ru_sarunas.csv`
- **Details:** Uses regex and function word lists to detect language.

### 4. 04_cleaning.py
- **Purpose:** Cleans the Latvian messages (removes stopwords, URLs, emojis, artifacts, etc.).
- **Input:** `DATA/03_lv_sarunas.csv`, `DATA/stop_words_latvian.txt`
- **Output:** `DATA/04_lv_sarunas_cleaned.csv`
- **Details:** Uses Stanza for tokenization. Prepares data for linguistic analysis.

### 5. 05_sarunas_freaquencies.py
- **Purpose:** Calculates word frequencies for Latvian messages.
- **Input:** `DATA/04_lv_sarunas_cleaned.csv`
- **Output:** `DATA/05_lv_freaquencies.csv`
- **Details:** Lemmatizes words using Stanza, useful for frequency analysis.

### 6. 06_target_collocations_main.py
- **Purpose:** Extracts collocations (e.g., trigrams) containing target lemmas (e.g., "potēt", "vakcinēt").
- **Input:** `DATA/04_lv_sarunas_cleaned.csv`
- **Output:** Console output of top collocations and their counts.
- **Details:** Useful for collocation and context analysis.

### 7. 07_LDA_topic.py
- **Purpose:** Performs topic modeling (LDA) on the cleaned Latvian messages.
- **Input:** `DATA/04_lv_sarunas_cleaned.csv`
- **Output:** `DATA/07_lda_5topics_cleaned.html`
- **Details:** Uses Gensim and Stanza for lemmatization and topic modeling. Visualizes topics with pyLDAvis.

### 08_language_frequencies.py
- **Purpose:** Performs multilingual lemmatization and frequency analysis for English, German, and Russian text corpora and generates frequency-based visualizations.
- **Input:**
  - `DATA/02_eng_main.csv`
  - `DATA/02_de_main.csv`
  - `DATA/02_ru_main.csv`
- **Output:** Console output of - Total lemma count before and after stopword removal, Top 10 most frequent lemmas per language
- **Details:** The script processes each language separately using Stanza lemmatization, applies manually curated stopword lists, and produces comparable frequency statistics and word cloud visualizations for cross-linguistic analysis.

## Achievements
- Automated extraction and cleaning of Telegram chat data.
- Language detection and separation for multilingual analysis.
- Advanced text cleaning and lemmatization for Latvian.
- Frequency analysis, collocation extraction, and topic modeling.
- Visualization of word frequencies and topics.
- Focused filtering for close reading of vaccine-related discussions.
- Lemmatization and frequency analysis for foreign-language corpora (EN/DE/RU) with custom stopwords and word clouds.

## Requirements
- Python 3.x
- pandas, stanza, gensim, matplotlib, wordcloud, pyLDAvis
- Download Latvian models for Stanza (done automatically in scripts)

## Usage
Run each script in order for a full pipeline, or use individual scripts for specific tasks. Adjust file paths as needed for your environment.

---
Author: Gundega Fedotova
Date: November 2025

