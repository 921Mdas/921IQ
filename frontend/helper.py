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


# Add this helper function to avoid code duplication
def build_where_clause(request):
    """Extracts filters from request and builds SQL WHERE clause"""
    and_keywords = request.args.getlist("and")
    or_keywords = request.args.getlist("or")
    not_keywords = request.args.getlist("not")

    conditions = []
    params = []

    for kw in and_keywords:
        conditions.append("LOWER(title) LIKE %s")
        params.append(f"%{kw.lower()}%")

    if or_keywords:
        or_clause = " OR ".join(["LOWER(title) LIKE %s" for _ in or_keywords])
        conditions.append(f"({or_clause})")
        params.extend([f"%{kw.lower()}%" for kw in or_keywords])

    for kw in not_keywords:
        conditions.append("LOWER(title) NOT LIKE %s")
        params.append(f"%{kw.lower()}%")

    where_clause = " AND ".join(conditions) if conditions else "TRUE"
    
    return where_clause, params