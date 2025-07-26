import logging
import re
import string
import time
from collections import Counter, defaultdict
from datetime import datetime
import psycopg2
import os
import wikipedia
from textblob import TextBlob
from keybert import KeyBERT
from sklearn.metrics.pairwise import cosine_similarity
import dateparser
import nltk
import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from flask import request, jsonify
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from psycopg2.extras import RealDictCursor
from functools import lru_cache

# Initialize logger
logger = logging.getLogger(__name__)
os.environ["TOKENIZERS_PARALLELISM"] = "false"


# Constants
TITLE_PREFIXES = {"President", "Dr", "Mr", "Mrs", "Ms", "Sir", "Madam", "Lord"}
SINGLE_NAME_WHITELIST = {"Trump", "Putin", "Madonna", "Biden", "Zelenskyy"}
month_translation = {
    'janvier': 'January', 'février': 'February', 'mars': 'March', 'avril': 'April',
    'mai': 'May', 'juin': 'June', 'juillet': 'July', 'août': 'August',
    'septembre': 'September', 'octobre': 'October', 'novembre': 'November', 'décembre': 'December'
}

# Lazy-loaded globals
_mode = os.getenv("MODE")
_kw_model = None
_nltk_initialized = False

# Initialize NLTK data once
def _init_nltk():
    global _nltk_initialized
    if not _nltk_initialized:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        _nltk_initialized = True

_init_nltk()

# Lazy-loaded KeyBERT model
def _get_kw_model():
    global _kw_model
    if _kw_model is None:
        _kw_model = KeyBERT()
    return _kw_model

# Database connection helper
def get_db_connection():
    try:
        if _mode == "production":
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

# --- Date & Time Functions ---
def parse_date(date_str, lang="fr"):
    return dateparser.parse(date_str, languages=[lang])

def convert_date(date_string):
    if isinstance(date_string, datetime):
        return date_string
    if not date_string or not isinstance(date_string, str):
        return None
    dt = dateparser.parse(date_string, languages=['fr'])
    return dt.date() if dt else None

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
        logger.warning(f"Date processing failed: {str(e)}")
        return datetime.now().isoformat()

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
        logger.warning(f"Failed to fetch date from {url} — {e}")
        return datetime.now()

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

# --- Text Processing Functions ---
def extract_keywords_cloud(titles, top_n=30):
    stop_words = set(stopwords.words('english')) | set(stopwords.words('french'))
    all_words = []

    for title in titles:
        tokens = word_tokenize(title.lower())
        words = [word for word in tokens if word.isalpha() and word not in stop_words]
        all_words.extend(words)

    freq = Counter(all_words)
    return [{"text": word.title(), "size": count} for word, count in freq.most_common(top_n)]

@lru_cache(maxsize=1000)
def _analyze_sentiment(text):
    return TextBlob(text).sentiment.polarity

def extract_sentiment(titles):
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    total_score = 0

    for title in titles:
        polarity = _analyze_sentiment(title)
        total_score += polarity

        if polarity > 0.1:
            sentiment_counts["positive"] += 1
        elif polarity < -0.1:
            sentiment_counts["negative"] += 1
        else:
            sentiment_counts["neutral"] += 1

    sentiment_counts["overall_score"] = round(total_score / len(titles), 2) if titles else 0
    return sentiment_counts

def extract_top_topics(titles, top_n=5, diversity_threshold=0.75):
    combined_text = ". ".join(set(titles))
    if not combined_text.strip():
        return []

    model = _get_kw_model()
    candidates = model.extract_keywords(
        combined_text,
        keyphrase_ngram_range=(1, 3),
        stop_words='english',
        use_maxsum=True,
        top_n=top_n * 3
    )

    unique_keywords = []
    vectors = []

    for kw, score in candidates:
        vector = model.model.embed([kw])[0]
        if all(cosine_similarity([vector], [v])[0][0] < diversity_threshold for v in vectors):
            unique_keywords.append((kw, score))
            vectors.append(vector)
        if len(unique_keywords) >= top_n:
            break

    return [kw for kw, _ in unique_keywords]

# --- Name Processing ---
def clean_name(name):
    tokens = name.split()
    filtered = [t for t in tokens if t not in TITLE_PREFIXES]
    return " ".join([w.capitalize() for w in filtered])

@lru_cache(maxsize=100)
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

# --- HTML Processing ---
def testSoup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

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

    return list({id(tag): tag for tag in ad_elements}.values())

# --- Database Utilities ---
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

# --- Network Utilities ---
def fetch_with_retries(url, retries=3, backoff=5):
    for attempt in range(retries):
        try:
            return requests.get(url, timeout=15)
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
            else:
                raise e

@lru_cache(maxsize=100)
def get_wikipedia_summary(entity_name):
    try:
        page = wikipedia.page(entity_name, auto_suggest=False)
        summary = wikipedia.summary(entity_name, sentences=2, auto_suggest=False)
        
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

# --- Entity Analysis ---
def extract_co_mentions(titles, target_name):
    pattern = re.compile(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b')
    co_mentions = Counter()
    for title in titles:
        candidates = pattern.findall(title)
        filtered = [c for c in candidates if c != target_name and target_name not in c]
        co_mentions.update(filtered)
    return [c for c, _ in co_mentions.most_common(5)]

def extract_quotes(titles, person_name):
    quote_pattern = re.compile(rf'([\w\s]*{re.escape(person_name)}[\w\s]*?said[^.]*\.)', re.IGNORECASE)
    quotes = []
    for title in titles:
        matches = quote_pattern.findall(title)
        quotes.extend(matches)
    return quotes[:5]