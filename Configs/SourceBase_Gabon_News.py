from urllib.parse import urljoin
from helper import convert_date
from helper import parse_date

def safe_parse_date(tag, lang="fr"):
    if not tag:
        return None
    dt = parse_date(tag.text.strip(), lang=lang)
    return dt.isoformat() if dt else None


scraper_news_sources = {
"GabonReview": {
    "config": {
        "base_url": "https://www.gabonreview.com",
        "get_articles": lambda soup: soup.select("div.post"),
        "get_title": lambda article: article.select_one("h3 a"),
        "get_url": lambda article, base_url: urljoin(base_url, article.select_one("h3 a")["href"]),
        "get_image": lambda article, base_url: (
            urljoin(base_url, article.select_one("div.cover img")["src"])
            if article.select_one("div.cover img") else None
        ),
        "get_date": lambda article: article.select_one("p.postmetadata"),
        "process_date": lambda tag: convert_date(
            tag.text.strip().split('/')[0].strip() if tag else None
        ),  # extract date before the slash (comments)
    },
    "source_meta": {
        "source_name": "GabonReview",
        "country": "Gabon",
        "source_logo": "https://www.gabonreview.com/wp-content/themes/gabonreview/images/logo.png",
        "language": "French",
        "categories": ["politics", "economy", "society", "international"],
        "bias": "independent",
        "popularity_rank": 1,
        "fact_checking": "moderate",
        "social_media": {
            "twitter": "@GabonReview",
            "facebook": "GabonReview"
        }
    },
},

"LUnion": {
    "config": {
        "base_url": "https://www.union.sonapresse.com",
        "get_articles": lambda soup: soup.select("div.text-article"),
        "get_title": lambda article: article.select_one("div.titre-article a"),
        "get_url": lambda article, base_url: urljoin(base_url, article.select_one("div.titre-article a")["href"]),
        "get_image": lambda article, base_url: (
            urljoin(base_url, article.select_one("div.image-article img")["src"]) 
            if article.select_one("div.image-article img") else None
        ),
        "get_date": lambda article: article.select_one("div.categorie-article"),
        "process_date": lambda tag: convert_date(
            tag.text.replace("Publié le", "").strip().replace(" / ", "-") if tag else None
        ),  # change "10 / 07 / 2025" → "10-07-2025" for date parsing
    },
    "source_meta": {
        "source_name": "L'Union",
        "country": "Gabon",
        "source_logo": "https://www.union.sonapresse.com/sites/all/themes/union/logo.png",
        "language": "French",
        "categories": ["official", "government", "local", "general news"],
        "bias": "pro-government",
        "popularity_rank": 2,
        "fact_checking": "limited",
        "social_media": {
            "facebook": "LUnionOfficiel"
        }
    },
},

"GabonActu": {
        "config": {
            "base_url": "https://gabonactu.com",
            "get_articles": lambda soup: soup.select("div.td-module-container"),
            "get_title": lambda article: article.select_one("h3.entry-title a"),
            "get_date": lambda article: article.select_one("time.entry-date"),
            "get_url": lambda article, base_url: urljoin(base_url, article.select_one("a")["href"]),
            "get_image": lambda article, base_url: urljoin(base_url, article.select_one("img")["src"]) if article.select_one("img") else None,
            "process_date": lambda tag: convert_date(tag.text.strip()) if tag else None,
        },
        "source_meta": {
            "source_name": "GabonActu",
            "country": "Gabon",
            "source_logo": "https://gabonactu.com/wp-content/uploads/2018/10/logo-gabonactu.png",
            "language": "French",
            "categories": ["politics", "security", "international"],
            "bias": "independent",
            "popularity_rank": 3,
            "fact_checking": "moderate",
            "social_media": {
                "twitter": "@GabonActu",
                "facebook": "GabonActu"
            }
        },
},

"Info241": {
    "config": {
        "base_url": "https://www.info241.com",
        "get_articles": lambda soup: soup.select("div.card.i_o_h_d"),  # each card
        "get_url": lambda article, base_url: urljoin(base_url, article.select_one("a.card.color_inherit")["href"]),
        "get_title": lambda article: article.select_one("h2.headline"),
        "get_image": lambda article, base_url: (
            urljoin(base_url, article.select_one("img")["src"])
            if article.select_one("img") else None
        ),
        "get_excerpt": lambda article: article.select_one("div.deck div"),
        "get_date": lambda article: None,  # Not available in snippet
        "process_date": lambda tag: None
    },
    "source_meta": {
        "source_name": "Info241",
        "country": "Gabon",
        "source_logo": "https://www.info241.com/IMG/siteon0.png",
        "language": "French",
        "categories": ["online news", "general", "politics", "economy"],
        "bias": "neutral",
        "popularity_rank": 3,
        "fact_checking": "limited",
        "social_media": {
            "twitter": "info241"
        }
    }
},

"GabonMediaTime": {
    "config": {
        "base_url": "https://gabonmediatime.com",
        "get_articles": lambda soup: soup.select("li.post-item.tie-standard"),
        "get_url": lambda article, base_url: article.select_one("a.post-thumb")["href"],
        "get_title": lambda article: article.select_one("h2.post-title a"),
        "get_image": lambda article, base_url: article.select_one("img")["src"],
        "get_excerpt": lambda article: None,  # Excerpt not in preview
        "get_date": lambda article: article.select_one("span.date.meta-item"),
        "process_date": lambda tag: convert_date(tag.text.strip()) if tag else None,
    },
    "source_meta": {
        "source_name": "Gabon Media Time",
        "country": "Gabon",
        "source_logo": "https://gabonmediatime.com/wp-content/themes/jannah/assets/images/logo-light.png",
        "language": "French",
        "categories": ["online news", "general", "politics", "society"],
        "bias": "neutral",
        "popularity_rank": 2,
        "fact_checking": "limited",
        "social_media": {
            "twitter": "GabonMediaTime"
        }
    }
},

}
