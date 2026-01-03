Telegram Data Analysis Pipelines – Āgenskalna klīnika
====================================================

This repository contains two Python-based pipelines for processing and analyzing Telegram chat data exported from the
Āgenskalna klīnika channel. Both pipelines start from Telegram HTML export files and produce cleaned datasets and
analysis outputs (frequencies, collocations, topic modeling, and more).

⚠️ DATA PRIVACY NOTE
-------------------
Telegram export files for Āgenskalna klīnika sarunas (e.g., MESSAGES/messages.html, messages2.html, etc.) are NOT included in this repository.
You must export the chat data yourself and place it into the correct folder structure before running the scripts.

What’s inside
-------------
The repo includes TWO pipelines:

1) Āgenskalna klīnika (Pipeline A)
   - Main end-to-end analysis pipeline.
   - Includes: HTML → CSV extraction, language split (LV/EN/RU/DE), Latvian cleaning + lemmatization,
     frequency analysis + wordcloud, collocations (trigrams), LDA topic modeling, and close-reading dataset export.
   - Best for: complete workflow from raw export to topic modeling + close reading.

   ➜ Read more in: README.txt in CODE_BASE_MAIN folder

2) Āgenskalna klīnika sarunas (Pipeline B)
   - Conversation-focused pipeline with additional preprocessing steps.
   - Includes: anonymization workflow, duplicate removal, then language split, cleaning, lemmatization,
     frequencies, collocations, and LDA topic modeling (plus multilingual frequency analysis).
   - Best for: cleaner + privacy-safer datasets (anonymized and deduplicated).

   ➜ Read more in: README.txt in CODE_BASE_SARUNAS folder


Recommended Folder Structure
----------------------------
/MESSAGES     - Telegram HTML export files (NOT included in Āgenskalna klīnika sarunas)
/DATA         - Output datasets and intermediate CSV files
/scripts      - Pipeline scripts (or scripts may be in the root)
/docs         - Optional documentation

Requirements 
------------
Programs / Tools used
---------------------
- Visual Studio Code (VS Code) – development environment (IDE)
- Python 3.x – running the scripts

Libraries used
--------------
Core data processing:
- pandas           (CSV processing, dataframes)
- numpy            (numerical helpers)

Telegram export parsing:
- beautifulsoup4   (parsing Telegram HTML export)
- lxml             (HTML parser backend)

Text processing & NLP:
- stanza           (tokenization + lemmatization)
- nltk             (n-grams / collocations / token utilities)
- gensim           (LDA topic modeling)
- scikit-learn     (optional utilities for text/vectorization)

Visualization:
- matplotlib       (plots)
- wordcloud        (word cloud generation)
- pyLDAvis         (interactive LDA visualization)

Utilities:
- tqdm             (progress bars, optional)
- re (built-in)    (regex cleaning and language detection)

Quick Start
-----------
1) Export Telegram chat history (HTML format).
2) Place export files into:
   MESSAGES/messages.html
   MESSAGES/messages2.html
   ...

3) Choose your pipeline and follow its README:
   - Pipeline A: README_Agenskalna_klinika.txt
   - Pipeline B: README_Agenskalna_klinika_sarunas.txt


Author
------
Gundega Fedotova
Date: December 2025

License
-------
MIT License (see LICENSE file).