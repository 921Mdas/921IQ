from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import string
from datetime import datetime
import requests
from bs4 import BeautifulSoup

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




month_translation = {
    'janvier': 'January', 'février': 'February', 'mars': 'March', 'avril': 'April',
    'mai': 'May', 'juin': 'June', 'juillet': 'July', 'août': 'August',
    'septembre': 'September', 'octobre': 'October', 'novembre': 'November', 'décembre': 'December'
}

def convert_date(date_string):
    if isinstance(date_string, datetime):
        return date_string.date()

    if not date_string or not isinstance(date_string, str):
        return None

    date_string = date_string.strip().lower()

    # Try RFI format: '20/05/2025'
    try:
        return datetime.strptime(date_string, "%d/%m/%Y").date()
    except ValueError:
        pass

    # Try Actu format: '20 mai 2025'
    try:
        parts = date_string.split()
        if len(parts) != 3:
            return None

        day, month, year = parts
        english_month = month_translation.get(month, month)
        date_string_english = f"{day} {english_month} {year}"
        return datetime.strptime(date_string_english, "%d %B %Y").date()
    except Exception:
        return None


def testSoup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup



def find_ads(soup):
    ad_elements = []

    # Keywords typically used in ads
    ad_keywords = ['ad', 'ads', 'advert', 'sponsor', 'promo', 'banner', 'bannière', 'pub', 'publicité']

    # Common banner sizes
    banner_sizes = {
        (728, 90), (300, 250), (336, 280), (160, 600),
        (300, 600), (970, 250), (1200, 200)
    }

    def contains_ad_keyword(text):
        if not text:
            return False
        text = text.lower()
        return any(kw in text for kw in ad_keywords)

    # 1. Lazy-loaded images likely to be ads
    for img in soup.find_all("img"):
        if img.get("loading") != "lazy":
            continue

        alt_text = img.get("alt", "")
        src = img.get("src", "")
        try:
            width = int(img.get("width", 0))
            height = int(img.get("height", 0))
        except ValueError:
            width = height = 0

        matches_size = (width, height) in banner_sizes or (width >= 728 and 90 <= height <= 300)
        has_keyword = contains_ad_keyword(alt_text) or contains_ad_keyword(src)

        if matches_size or has_keyword:
            ad_elements.append(img)

    # 2. <a> tags with ad-related keywords in attributes
    for a in soup.find_all("a"):
        for attr in ['href', 'class', 'id', 'aria-label', 'title']:
            value = a.get(attr, "")
            if isinstance(value, list):
                value = " ".join(value)
            if contains_ad_keyword(value):
                ad_elements.append(a)
                break

    # Deduplicate
    unique_ads = list({id(tag): tag for tag in ad_elements}.values())
    print(unique_ads)
    return unique_ads