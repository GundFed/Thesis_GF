from pathlib import Path
import pandas as pd
from collections import Counter
import stanza
import sys
import matplotlib.pyplot as plt
from wordcloud import WordCloud


##### Manual stopword lists (EN, DE, RU) - no extra libraries #####


STOPWORDS = {
    "en" : {
    "a","about","above","across","after","afterwards","again","against",
    "almost","alone","along","already","also","always","am","among",
    "amongst","amoungst","amount","an","and","another","any","anyhow",
    "anyway","anywhere","are","around","as","at","back","be","became",
    "become","becomes","becoming","been","before","beforehand","behind",
    "being","below","beside","besides","between","beyond","both","bottom",
    "but","by","call","can","cannot","cant","co","con","could","couldnt",
    "cry","de","describe","detail","do","done","down","due","during",
    "each","eg","eight","either","eleven","else","elsewhere","empty",
    "enough","etc","even","ever","every","everywhere","except","few",
    "fifteen","fify","fill","find","fire","first","five","for","former",
    "formerly","forty","found","four","from","front","full","further",
    "get","give","go","had","has","hasnt","have","he","her","here",
    "hereafter","hereby","herein","hereupon","hers","herself","him",
    "himself","his","however","hundred","ie","if","in","inc","indeed",
    "interest","into","is","it","its","itself","keep","last","latter",
    "latterly","least","less","ltd","made","may","me","meanwhile",
    "might","mill","mine","moreover","mostly","move","much","must",
    "my","myself","name","namely","neither","never","nevertheless",
    "next","nine","no","nobody","none","noone","nor","not","nothing",
    "now","nowhere","of","off","often","on","once","one","only","onto",
    "or","other","others","otherwise","our","ours","ourselves","out",
    "over","own","part","per","perhaps","please","put","rather","re",
    "same","see","seem","seemed","seeming","seems","serious","several",
    "she","should","show","side","since","sincere","six","sixty","so",
    "some","somehow","sometime","sometimes","somewhere","still","such",
    "system","take","ten","than","that","the","their","them",
    "themselves","then","thence","there","thereafter","thereby",
    "therein","thereupon","these","they","thickv","thin","third",
    "this","those","three","through","throughout","thru","thus","to",
    "together","too","top","toward","towards","twelve","twenty","two",
    "un","under","until","up","upon","us","very","via","was","we",
    "well","were","which","while","whitehr","whom","whose","will",
    "with","within","without","would"
},

    "de" : {
    "a","ab","aber","ach","acht","achte","achten","achter","achtes",
    "alle","allem","allen","aller","alles","als","also","am","an","andere",
    "anderen","andern","anders","auch","auf","aus","ausser","außer",
    "ausserdem","außerdem","bald","bei","beide","beiden","beim","bekannt",
    "bereits","besonders","besser","besten","bin","bis","bisher","bist",
    "da","dabei","dadurch","dagegen","daher","dahin","dahinter","damals",
    "damit","danach","daneben","dann","daran","darauf","daraus","darf",
    "darfst","darin","darüber","darum","darunter","das","dass","daß",
    "dasselbe","davon","davor","dazu","dazwischen","dein","deine",
    "deinem","deiner","dem","demgegenüber","demgemäss","demgemäß",
    "demselben","demzufolge","den","denen","denn","denselben","der",
    "deren","derjenige","derjenigen","derselbe","derselben","des",
    "desselben","dessen","deswegen","d.h","dich","die","diejenige",
    "diejenigen","dies","diese","dieselbe","dieselben","diesem","diesen",
    "dieser","dieses","dir","doch","dort","drei","drin","dritte","dritten",
    "dritter","drittes","du","durch","durchaus","dürfen","dürft","durfte",
    "durften","eben","ebenso","ehrlich","eigen","eigene","eigenen","eigener",
    "eigenes","ein","einander","eine","einem","einen","einer","eines",
    "einige","einigen","einiger","einiges","einmal","eins","elf","en",
    "ende","endlich","entweder","er","erst","erste","ersten","erster",
    "erstes","es","etwa","etwas","euch","f","früher","für","g","gab","ganz",
    "ganze","ganzen","ganzer","ganzes","gar","gegen","gegenüber","gehabt",
    "gehen","geht","gekannt","gekonnt","gemacht","gemocht","gemusst",
    "genug","gerade","gern","gesagt","gewesen","gewollt","geworden","gibt",
    "ging","gleich","gross","groß","grosse","große","grossen","großen",
    "grosser","großer","grosses","großes","gut","gute","guter","gutes",
    "h","habe","haben","habt","hast","hat","hatte","hätte","hatten",
    "hätten","heisst","her","heute","hier","hin","hinter","hoch",
    "ich","ihm","ihn","ihnen","ihr","ihre","ihrem","ihren","ihrer","ihres",
    "im","immer","in","indem","ins","irgend","ist","ja","jahr","jahre",
    "jahren","je","jede","jedem","jeden","jeder","jedermann","jedermanns",
    "jedoch",
    "jemand","jemandem","jemanden","jene","jenem","jenen","jener","jenes","jetzt",
    "kam","kann","kannst","kaum","kein","keine","keinem","keinen",
    "keiner","kleine","kleinen","kleiner","kleines","kommen","kommt",
    "können","könnt","konnte","könnte","konnten","kurz","lang","lange",
    "leicht","lieber","los","machen","macht","machte","mag","magst",
    "man","manche","manchem","manchen","mancher","manches","mehr","mein",
    "meine","meinem","meinen","meiner","meines","mensch","menschen",
    "mich","mir","mit","mittel","mochte","möchte","mochten","mögen",
    "möglich","mögt","morgen","muss","muß","müssen","musst","müsst",
    "musste","mussten","n","na","nach","nachdem","nahm","natürlich",
    "neben","nein","neue","neuen","neun","nicht","nichts","nie",
    "niemand","niemandem","niemanden","noch","nun","nur","ob","oben",
    "oder","offen","oft","ohne","Ordnung","recht","rechte","rechten",
    "rechter","rechtes","richtig","rund","s","sa","sache","sagt","sagte",
    "sah","satt","schlecht","Schluss","schon","sechs","sechste","sechsten",
    "sechster","sechstes","sehr","sei","seid","seien","sein","seine",
    "seinem","seinen","seiner","seines","seit","seitdem","selbst",
    "sich","sie","sieben","siebente","siebenten","siebenter","siebentes",
    "sind","so","solang","solche","solchem","solchen","solcher","solches",
    "soll","sollen","sollte","sollten","sondern","sonst","sowie","später",
    "statt","tag","tage","tagen","tat","teil","tritt","trotzdem","tun",
    "über","überhaupt","übrigens","uhr","um","und","uns","unser","unsere",
    "unserer","unter","vergangenen","viel","viele","vielem","vielen",
    "vier","vierte","vierten","vierter","viertes","vom","von","vor",
    "während","währenddem","währenddessen","war","wäre","waren","wart",
    "wegen","weit","weiter","weitere","weiteren","weiteres","welche",
    "welchem","welchen","welcher","welches","wem","wen","wenig","wenige",
    "weniger","weniges","wenigstens","wenn","werde","werden","werdet",
    "wessen","wieder","will","willst","wir","wird","wirklich","wirst",
    "wohl","wollen","wollt","wollte","wollten","worden","wurde","würde",
    "wurden","würden","z.b","zehn","zehnte","zehnten","zehnter","zehntes",
    "zeit","zu","zuerst","zugleich","zum","zunächst","zur","zurück",
    "zusammen","zwar","zwei","zweite","zweiten","zweiter","zweites",
    "zwischen","zwölf"
}, 


  "ru": {
    "а","е","и","ж","м","о",
    "на","не","ни","об","но",
    "он","мне","мои","она","они","оно",
    "мной","мною","мой","моя","моё","мое","мои",
    "мож","мог","могут","можно","может","можхо",
    "над","нее","нам","нем","нами","ними",
    "немного","менее","меньше","мало",
    "надо","назад","наиболее","недавно","недалеко",
    "между","нам","нам","нибудь","нельзя",
    "наконец","никогда","никуда","нас","наш","наша","наше","наши",
    "нею","неё","них","начала","нередко",
    "несколько","обычно","опять","около","ну","от","отовсюду",
    "особенно","нужно","очень","отсюда","в","во","вон",
    "вниз","внизу","вокруг","вот","вверх","вам","вами",
    "важное","важная","важные","важный","вдали","везде",
    "ведь","вас","ваш","ваша","ваше","ваши",
    "впрочем","второй","всем","всеми","всему",
    "всего","всегда","всех","всею","всю",
    "вся","всё","всюду","год","года","году",
    "да","ее","за","из","ли","же","им",
    "до","по","ими","под","иногда","довольно",
    "именно","долго","позже","более","должно",
    "пожалуйста","значит","иметь","больше","пока","ему","имя",
    "пор","пора","потом","потому","после","почти",
    "посреди","ей","два","две","двенадцать",
    "двенадцатый","двадцать","двадцатый","двух","его","дел",
    "или","без","день","занят","занята","занято","заняты",
    "действительно","давно","девятнадцать","девятнадцатый",
    "девять","девятый","даже","алло","далеко","близко",
    "здесь","дальше","для","лет","зато","даром",
    "первый","перед","затем","лишь",
    "десять","десятый","ею","её","их","бы","еще",
    "при","был","про","процентов","против",
    "просто","бывает","бывь","если","была","были","было",
    "будем","будет","будете","будешь","прекрасно","буду",
    "будь","будто","будут","ещё","пятнадцать","пятнадцатый",
    "другое","другой","другие","другая","других",
    "есть","пять","быть","лучше","пятый","к","ком",
    "конечно","кому","кого","кроме",
    "кругом","с","со","то","том","снова","тому","совсем",
    "того","тогда","тоже","собой","тобой","собою","тобою",
    "сначала","только","уметь","тот","тою","хорошо",
    "хоть","хотя","свое","свои","твой","своей","своего",
    "своих","свою","твоя","твоё","раз","уже","сам",
    "там","тем","чем","сама","сами","теми","само",
    "самом","самому","самой","самого","семнадцать",
    "семнадцатый","самим","самими","самих","саму",
    "семь","чему","раньше","сейчас",
    "себе","тебе","сеаой","разве","теперь",
    "себя","тебя","седьмой","слишком","так",
    "такое","такой","такие","также",
    "такая","сих","тех","чаще","четвертый",
    "часто","шестой","шестнадцать","шестнадцатый",
    "шесть","четыре","четырнадцать","четырнадцатый",
    "сколько","ты","три","эта","эти",
    "что","это","чтоб","этом","этому","этой","этого",
    "чтобы","этот","туда","этим","этими","этих",
    "тут","эту","суть","чуть","тысяч"
}
}


#####  Input files ##### 
INPUT_FILES = {
    "ru": Path(__file__).parent / "DATA" / "02_ru_main.csv",
    "de": Path(__file__).parent / "DATA" / "02_de_main.csv",
    "en": Path(__file__).parent / "DATA" / "02_eng_main.csv",
}

LANG_NAMES = {"ru": "Russian", "de": "German", "en": "English"}

TOP_N = 10
WORDCLOUD_N = 30


#####  Init Stanza pipelines #####

for lang in INPUT_FILES:
    stanza.download(lang, processors="tokenize,pos,lemma", verbose=False)

pipelines = {
    lang: stanza.Pipeline(
        lang,
        processors="tokenize,pos,lemma",
        tokenize_no_ssplit=True,
        verbose=False,
        use_gpu=False
    )
    for lang in INPUT_FILES
}


#####  Lemmatizer #####

def stanza_lemmatize(text, lang):
    if pd.isna(text):
        return []

    doc = pipelines[lang](str(text))

    lemmas = []
    for sent in doc.sentences:
        for w in sent.words:
            lemma = w.lemma.lower()
            if lemma.isalpha(): 
                lemmas.append(lemma)

    return lemmas


#####  Word cloud #####

def make_wordcloud(freqs, lang):
    wc = WordCloud(
        width=1200,
        height=600,
        background_color="white",
        max_words=WORDCLOUD_N,
    ).generate_from_frequencies(freqs)

    plt.figure(figsize=(12, 6))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.title(f"Word Cloud – {LANG_NAMES[lang]}", fontsize=18)
    plt.tight_layout()
    plt.show()


##### MAIN LOOP #####

def main():
    for lang, file_path in INPUT_FILES.items():

        print(f"\n===============================================")
        print(f"Processing {LANG_NAMES[lang]}:\n{file_path}")
        print("===============================================")

        df = pd.read_csv(file_path, encoding="utf-8-sig")

        if "content" not in df.columns:
            print("❌ Missing 'content' column")
            continue

        all_lemmas = []

        for text in df["content"]:
            all_lemmas.extend(stanza_lemmatize(text, lang))

        print(f"Lemmas BEFORE stopword removal: {len(all_lemmas):,}")

        #####  STOPWORD REMOVAL #####
        stopset = STOPWORDS[lang]
        filtered = [lemma for lemma in all_lemmas if lemma not in stopset]

        print(f"Lemmas AFTER stopword removal: {len(filtered):,}")

        #####  Frequency count #####
        counts = Counter(filtered)

        #####  Print top N #####
        print(f"\nTop {TOP_N} lemmas ({LANG_NAMES[lang]}):")
        for lemma, cnt in counts.most_common(TOP_N):
            print(f"{lemma:15} {cnt}")

        #####  Word Cloud #####
        wc_data = dict(counts.most_common(WORDCLOUD_N))
        if wc_data:
            make_wordcloud(wc_data, lang)


if __name__ == "__main__":
    main()

print("DONE")
