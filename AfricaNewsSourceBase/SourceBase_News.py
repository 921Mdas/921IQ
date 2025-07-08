# scraper_config.py

from urllib.parse import urljoin
from helper import convert_date, extract_sur7cd_date  # assuming you moved extract_sur7cd_date here

scraper_news_sources = {
    "ActuCD": {
        "config": {
            "base_url": "https://actualite.cd",
            "get_articles": lambda soup: soup.find_all("div", class_="what-cap"),
            "get_title": lambda article: article.select_one("h4 > a"),
            "get_date": lambda article: article.select_one("span"),
            "process_date": lambda tag: convert_date(tag.text.strip()) if tag else None,
        },
        "source_meta": {
            "source_name": "Actualite.cd",
            "country": "Dem. Rep. Congo",
            "source_logo": "data:image/png;base64,...",
        },
    },
    "Sur7CD": {
        "config": {
            "base_url": "https://7sur7.cd",
            "get_articles": lambda soup: soup.select("div.views-row"),
            "get_title": lambda article: article.select_one("div.views-field-title span.field-content a"),
            "get_date": lambda article: None,
            "get_url": lambda article, base_url: urljoin(
                base_url, article.select_one("div.views-field-title span.field-content a")["href"]
            )
            if article.select_one("div.views-field-title span.field-content a")
            else None,
            "process_date": lambda tag: tag,
            "get_article_date_from_url": lambda url: extract_sur7cd_date(url),
        },
        "source_meta": {
            "source_name": "7sur7.cd",
            "country": "Dem. Rep. Congo",
            "source_logo": "<your_base64_logo_here>",
        },
    },
    # Add more scrapers here
    "RFICD": {
        "config": {
            "base_url": "https://www.rfi.fr",
            "get_articles": lambda soup: soup.find_all('div', class_='article__infos'),
            "get_title": lambda article: article.select_one('h2'),
            "get_date": lambda article: article.find('time'),
            "process_date": lambda tag: convert_date(tag.text.strip()) if tag else None,
            "get_url": lambda article, base_url: urljoin(
                base_url, article.select_one('div > a')['href']
            ) if article.select_one('div > a') and 'href' in article.select_one('div > a').attrs else None,
        },
        "source_meta": {
            "source_name": "RFI",
            "country": "France",
            "source_logo": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQFSKPQwi6ZtYU92JwnoJXgYTYXj0jcr9fGUQ&s",
        },
    },
     "RadioOkapi": {
        "config": {
            "base_url": "https://www.radiookapi.net",
            "get_articles": lambda soup: soup.find_all("div", class_="views-row"),
            "get_title": lambda article: article.select_one("h2 > a"),
            "get_date": lambda article: (
                article.select_one("span.date-display-single") or
                article.select_one("div.submitted") or
                article.select_one("time")
            ),
            "get_url": lambda article, base_url: urljoin(base_url, article.select_one("h2 > a")["href"])
                if article.select_one("h2 > a") else None,
            "process_date": lambda tag: convert_date(tag.text.strip()) if tag else None,
        },
        "source_meta": {
            "source_name": "Radio Okapi",
            "country": "Dem. Rep. Congo",
            "source_logo": "<your_base64_logo_here>"
        }
    }
}
