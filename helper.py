from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
from bs4 import BeautifulSoup

month_translation = {
    'janvier': 'January', 'février': 'February', 'mars': 'March', 'avril': 'April',
    'mai': 'May', 'juin': 'June', 'juillet': 'July', 'août': 'August',
    'septembre': 'September', 'octobre': 'October', 'novembre': 'November', 'décembre': 'December'
}

def convert_date(date_string):
    if isinstance(date_string, datetime):
        return date_string.date()

    # Try RFI format: '20/05/2025'
    try:
        return datetime.strptime(date_string, "%d/%m/%Y").date()
    except ValueError:
        pass

    # Try Actu format: '20 mai 2025'
    try:
        day, month, year = date_string.split()
        english_month = month_translation.get(month.lower(), month)
        date_string_english = f"{day} {english_month} {year}"
        return datetime.strptime(date_string_english, "%d %B %Y").date()
    except Exception:
        return None  # return None if both formats fail


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
