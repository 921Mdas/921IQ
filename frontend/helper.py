from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import string

# Only needed once, during app start
nltk.download("punkt")
nltk.download("stopwords")

def extract_keywords(titles, top_n=30):
    stop_words = set(stopwords.words('english')) | set(stopwords.words('french'))
    all_words = []

    for title in titles:
        tokens = word_tokenize(title.lower())
        words = [
            word for word in tokens
            if word.isalpha() and word not in stop_words
        ]
        all_words.extend(words)

    freq = Counter(all_words)
    return [{"text": word.title(), "size": count} for word, count in freq.most_common(top_n)]
