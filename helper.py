from collections import Counter
from nltk.tokenize import word_tokenize
import string
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import dateparser
from datetime import datetime
import time
import dateparser
import nltk
from nltk.corpus import stopwords


from datetime import datetime
import re
import logging
from dateutil.parser import parse  # Requires python-dateutil


# Only needed once, during app start
nltk.download("punkt")
nltk.download("stopwords")


from flask import request, jsonify
from collections import defaultdict
from psycopg2.extras import RealDictCursor
import requests

# List of known titles to strip
TITLE_PREFIXES = {"President", "Dr", "Mr", "Mrs", "Ms", "Sir", "Madam", "Lord"}
# Optional whitelist of single-word famous people to keep
SINGLE_NAME_WHITELIST = {"Trump", "Putin", "Madonna", "Biden", "Zelenskyy"}

def clean_name(name):
    """Normalize name by removing common titles and capitalizing properly."""
    tokens = name.split()
    filtered = [t for t in tokens if t not in TITLE_PREFIXES]
    return " ".join([w.capitalize() for w in filtered])

def enrich_with_wikipedia(name):
    """Enrich entity data with Wikipedia summary and link."""
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name.replace(' ', '_')}"
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            return {
                "description": data.get("extract", ""),
                "wikilink": data.get("content_urls", {}).get("desktop", {}).get("page")
            }
    except Exception as e:
        logger.warning(f"Wikipedia fetch failed for {name}: {e}")
    return None



def fetch_with_retries(url, retries=3, backoff=5):
    for attempt in range(retries):
        try:
            return requests.get(url, timeout=15)
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
            else:
                raise e


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
        return date_string

    if not date_string or not isinstance(date_string, str):
        return None

    dt = dateparser.parse(date_string, languages=['fr'])
    if dt:
        return dt.date()  # Return date only, remove `.date()` if you want datetime
    return None

def extract_sur7cd_date(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.content, 'html.parser')

        date_tag = soup.select_one('span.date-display-single') or \
                   soup.select_one('span.submitted') or \
                   soup.select_one('time')

        raw_date = date_tag.get('content') if date_tag and date_tag.has_attr('content') else (
            date_tag.text.strip() if date_tag else None
        )

        date = convert_date(raw_date) if raw_date else datetime.now()
        return date
    except Exception as e:
        print(f"❌ in helper.py Failed to fetch date from {url} — {e}")
        return datetime.now()


def testSoup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup



def parse_date(date_str, lang="fr"):
    return dateparser.parse(date_str, languages=[lang])


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


def extract_keywords_cloud(titles, top_n=30):
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


def ensure_nltk_data():
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

# Call this at startup
ensure_nltk_data()

def extract_keywords(titles):
    try:
        # Ensure stopwords are loaded
        stop_words = set(stopwords.words('english')).union(set(stopwords.words('french')))
        # Rest of your keyword extraction logic
    except Exception as e:
        logger.error(f"Keyword extraction failed: {str(e)}")
        return []  # Return empty list as fallback


# Set up logger at module level
logger = logging.getLogger(__name__)


def process_article_date(url=None, soup=None, raw_date=None, publication_id=None):
    """
    Unified date processor for all publications
    Args:
        url: Article URL (for URL-based extraction)
        soup: BeautifulSoup object (for DOM-based extraction)
        raw_date: Direct date string to parse
        publication_id: Used for special cases (e.g., 'sur7cd')
    """
    try:
        # 1. Special Case: 7sur7.cd (date from URL)
        if publication_id == 'sur7cd' and url:
            if '/20' in url:  # Check for YYYY/MM/DD pattern
                date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
                if date_match:
                    return f"{date_match[1]}-{date_match[2]}-{date_match[3]}"

        # 2. DOM-based extraction (if soup provided)
        if soup:
            date_tag = (soup.select_one('span.date-display-single') or 
                       soup.select_one('span.submitted') or
                       soup.select_one('time') or
                       soup.select_one('span.color1') or  # Actualite.cd
                       soup.select_one('span.date'))     # Common alternative
            
            if date_tag:
                raw_date = date_tag.get('content', date_tag.text.strip())

        # 3. Fallback to raw_date if provided
        if raw_date:
            return convert_date(raw_date)  # Your existing date converter

        # 4. Final fallback
        return datetime.now().isoformat()

    except Exception as e:
        print(f"⚠️ Date processing failed: {str(e)}")
        return datetime.now().isoformat()