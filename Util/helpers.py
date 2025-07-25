import logging
import re
import string
import time
from collections import Counter, defaultdict
from datetime import datetime
import psycopg2
import os
import wikipedia


import dateparser
import nltk
import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse  # For general date parsing
from flask import request, jsonify
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from psycopg2.extras import RealDictCursor

# Download NLTK data if not already available
nltk.download("punkt")
nltk.download("stopwords")

mode = os.getenv("MODE")

# Logger configuration
logger = logging.getLogger(__name__)

# Constants
TITLE_PREFIXES = {"President", "Dr", "Mr", "Mrs", "Ms", "Sir", "Madam", "Lord"}
SINGLE_NAME_WHITELIST = {"Trump", "Putin", "Madonna", "Biden", "Zelenskyy"}
month_translation = {
    'janvier': 'January', 'février': 'February', 'mars': 'March', 'avril': 'April',
    'mai': 'May', 'juin': 'June', 'juillet': 'July', 'août': 'August',
    'septembre': 'September', 'octobre': 'October', 'novembre': 'November', 'décembre': 'December'
}



#get database connection helper

def get_db_connection():
    try:
        if mode == "production":
            conn = psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB_PROD"),
                user=os.getenv("POSTGRES_USER_PROD"),
                password=os.getenv("POSTGRES_PASSWORD_PROD"),
                host=os.getenv("POSTGRES_HOST_PROD"),
                port=os.getenv("POSTGRES_PORT_PROD"),
            )
        else:
            conn = psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host=os.getenv("POSTGRES_HOST"),
                port=os.getenv("POSTGRES_PORT"),
            )
        return conn
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise




# Ensures NLTK stopwords are available (only called once)
def ensure_nltk_data():
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')


# Call this at startup
ensure_nltk_data()


# --- Date & Time Functions ---

# Parses a date string using `dateparser` with French locale.
def parse_date(date_str, lang="fr"):
    return dateparser.parse(date_str, languages=[lang])


# Converts a string or datetime input into a `datetime.date` object.
def convert_date(date_string):
    if isinstance(date_string, datetime):
        return date_string
    if not date_string or not isinstance(date_string, str):
        return None
    dt = dateparser.parse(date_string, languages=['fr'])
    return dt.date() if dt else None


# Unified date extractor supporting various fallback strategies.
def process_article_date(url=None, soup=None, raw_date=None, publication_id=None):
    try:
        if publication_id == 'sur7cd' and url:
            if '/20' in url:
                match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
                if match:
                    return f"{match[1]}-{match[2]}-{match[3]}"
        if soup:
            date_tag = (soup.select_one('span.date-display-single') or 
                        soup.select_one('span.submitted') or 
                        soup.select_one('time') or 
                        soup.select_one('span.color1') or 
                        soup.select_one('span.date'))
            if date_tag:
                raw_date = date_tag.get('content', date_tag.text.strip())
        if raw_date:
            return convert_date(raw_date)
        return datetime.now().isoformat()
    except Exception as e:
        print(f"⚠️ Date processing failed: {str(e)}")
        return datetime.now().isoformat()


# Attempts to extract publication date from a sur7.cd article using DOM or fallback.
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
        return convert_date(raw_date) if raw_date else datetime.now()
    except Exception as e:
        print(f"❌ in helper.py Failed to fetch date from {url} — {e}")
        return datetime.now()


# Extracts and counts frequency of dates to help plot trend data.
def process_trend_data(dates):
    date_objs = []
    for date in dates:
        try:
            if isinstance(date, str):
                date_objs.append(datetime.fromisoformat(date))
            elif isinstance(date, datetime):
                date_objs.append(date)
        except Exception:
            continue

    if not date_objs:
        return {"labels": [], "data": []}

    formatted_dates = [date.strftime('%b %d') for date in date_objs]
    date_counts = Counter(formatted_dates)
    unique_dates = sorted(set(date_objs))
    sorted_labels = [date.strftime('%b %d') for date in unique_dates]

    return {
        "labels": sorted_labels,
        "data": [date_counts[label] for label in sorted_labels]
    }


# --- Keyword and Text Processing ---

# Extracts keyword frequency from titles to generate a tag cloud.
def extract_keywords_cloud(titles, top_n=30):
    stop_words = set(stopwords.words('english')) | set(stopwords.words('french'))
    all_words = []

    for title in titles:
        tokens = word_tokenize(title.lower())
        words = [word for word in tokens if word.isalpha() and word not in stop_words]
        all_words.extend(words)

    freq = Counter(all_words)
    return [{"text": word.title(), "size": count} for word, count in freq.most_common(top_n)]


# Lightweight keyword extraction with error logging.
def extract_keywords(titles):
    try:
        stop_words = set(stopwords.words('english')).union(set(stopwords.words('french')))
        # Further keyword extraction logic would go here...
    except Exception as e:
        logger.error(f"Keyword extraction failed: {str(e)}")
        return []


# --- Name Cleaning & Wikipedia Enrichment ---

# Removes titles (Mr, Dr, etc.) and capitalizes each word of the name.
def clean_name(name):
    tokens = name.split()
    filtered = [t for t in tokens if t not in TITLE_PREFIXES]
    return " ".join([w.capitalize() for w in filtered])


# Fetches a short Wikipedia summary and link for a given person/entity.
def enrich_with_wikipedia(name):
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


# --- HTML Parsing and Filtering ---

# Extracts soup object from URL.
def testSoup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


# Detects ad-like elements in an HTML document based on attributes and size.
def find_ads(soup):
    ad_elements = []
    ad_keywords = ['ad', 'ads', 'advert', 'sponsor', 'promo', 'banner', 'bannière', 'pub', 'publicité']
    banner_sizes = {
        (728, 90), (300, 250), (336, 280), (160, 600), (300, 600), (970, 250), (1200, 200)
    }

    def contains_ad_keyword(text):
        if not text:
            return False
        text = text.lower()
        return any(kw in text for kw in ad_keywords)

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

    for a in soup.find_all("a"):
        for attr in ['href', 'class', 'id', 'aria-label', 'title']:
            value = a.get(attr, "")
            if isinstance(value, list):
                value = " ".join(value)
            if contains_ad_keyword(value):
                ad_elements.append(a)
                break

    unique_ads = list({id(tag): tag for tag in ad_elements}.values())
    print(unique_ads)
    return unique_ads


# --- SQL Filter Builder ---

# Builds a WHERE clause and parameter list for keyword + source filters.
def build_where_clause(and_keywords, or_keywords, not_keywords, sources):
    conditions = []
    params = []

    for kw in and_keywords:
        if kw:
            conditions.append("LOWER(title) LIKE %s")
            params.append(f"%{kw.lower()}%")

    if or_keywords:
        or_conditions = []
        for kw in or_keywords:
            if kw:
                or_conditions.append("LOWER(title) LIKE %s")
                params.append(f"%{kw.lower()}%")
        if or_conditions:
            conditions.append(f"({' OR '.join(or_conditions)})")

    for kw in not_keywords:
        if kw:
            conditions.append("LOWER(title) NOT LIKE %s")
            params.append(f"%{kw.lower()}%")

    if sources:
        filter_sources = sources[1:] if len(sources) > 1 else sources
        placeholders = ",".join(["%s"] * len(filter_sources))
        conditions.append(f"source_name IN ({placeholders})")
        params.extend(filter_sources)

    where_clause = " AND ".join(conditions) if conditions else "TRUE"
    return where_clause, params


# --- Retry Helpers ---

# Attempts a GET request with retries and exponential backoff.
def fetch_with_retries(url, retries=3, backoff=5):
    for attempt in range(retries):
        try:
            return requests.get(url, timeout=15)
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
            else:
                raise e


def get_wikipedia_summary(entity_name):
    """Fetch Wikipedia summary for an entity"""
    try:
        page = wikipedia.page(entity_name, auto_suggest=False)
        summary = wikipedia.summary(entity_name, sentences=2, auto_suggest=False)
        
        # Find first suitable image
        image_url = next(
            (img for img in page.images 
             if any(ext in img.lower() for ext in [".jpg", ".jpeg", ".png"]) 
             and "logo" not in img.lower()),
            ""
        )

        return {
            "summary": summary,
            "url": page.url,
            "image": image_url
        }

    except (wikipedia.DisambiguationError, wikipedia.PageError, wikipedia.HTTPTimeoutError):
        return {
            "summary": "No Wikipedia summary available.",
            "url": "",
            "image": ""
        }

#sentiment analysis for entities
def extract_sentiment(titles):
    """Analyze sentiment of given titles"""
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    total_score = 0

    for title in titles:
        blob = TextBlob(title)
        polarity = blob.sentiment.polarity
        total_score += polarity

        if polarity > 0.1:
            sentiment_counts["positive"] += 1
        elif polarity < -0.1:
            sentiment_counts["negative"] += 1
        else:
            sentiment_counts["neutral"] += 1

    sentiment_counts["overall_score"] = round(total_score / len(titles), 2) if titles else 0
    return sentiment_counts

#top_topics for entities
def extract_top_topics(titles, top_n=5, diversity_threshold=0.75):
    """Extract diverse topics from titles"""
    combined_text = ". ".join(set(titles))
    if not combined_text.strip():
        return []

    candidates = kw_model.extract_keywords(
        combined_text,
        keyphrase_ngram_range=(1, 3),
        stop_words='english',
        use_maxsum=True,
        top_n=top_n * 3
    )

    unique_keywords = []
    vectors = []

    for kw, score in candidates:
        vector = kw_model.model.embed([kw])[0]
        if all(cosine_similarity([vector], [v])[0][0] < diversity_threshold for v in vectors):
            unique_keywords.append((kw, score))
            vectors.append(vector)
        if len(unique_keywords) >= top_n:
            break

    return [kw for kw, _ in unique_keywords]

#other mentions for entities
def extract_co_mentions(titles, target_name):
    """Extract co-mentioned names"""
    pattern = re.compile(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b')
    co_mentions = Counter()
    for title in titles:
        candidates = pattern.findall(title)
        filtered = [c for c in candidates if c != target_name and target_name not in c]
        co_mentions.update(filtered)
    return [c for c, _ in co_mentions.most_common(5)]

#quotes for entities
def extract_quotes(titles, person_name):
    """Extract quotes mentioning a person"""
    quote_pattern = re.compile(rf'([\w\s]*{re.escape(person_name)}[\w\s]*?said[^.]*\.)', re.IGNORECASE)
    quotes = []
    for title in titles:
        matches = quote_pattern.findall(title)
        quotes.extend(matches)
    return quotes[:5]
