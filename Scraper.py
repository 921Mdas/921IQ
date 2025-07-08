from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime
from helper import convert_date
import requests

def scrape_articles(page, config, source_meta):
    print(f"[{source_meta['source_name']}] Scraper started.")
    news = []

    try:
        page.goto(config['base_url'], timeout=60000)
        page.wait_for_timeout(3000)
        html = page.inner_html("body")
        soup = BeautifulSoup(html, 'html.parser')

        articles = config['get_articles'](soup)
        print(f"Found {len(articles)} articles.")

        if not articles:
            print("❗ No articles found. Here's a snippet:")
            print(html[:2000])

        for article in articles:
            title_tag = config['get_title'](article)
            if not title_tag:
                print("❌ Skipped due to missing title tag")
                continue

            title = title_tag.text.strip()
            relative_url = title_tag.get('href')
            url = urljoin(config['base_url'], relative_url)

            try:
                article_res = requests.get(url, timeout=10)
                article_soup = BeautifulSoup(article_res.content, 'html.parser')
                date_tag = config['get_date'](article_soup)

                raw_date = date_tag.get('content') if date_tag and date_tag.has_attr('content') else (date_tag.text.strip() if date_tag else None)
                date = convert_date(raw_date) if raw_date else datetime.now()

                article_data = {
                    'date': date.isoformat(),
                    'title': title,
                    'url': url,
                    'source_name': source_meta['source_name'],
                    'country': source_meta['country'],
                    'source_logo': source_meta['source_logo']
                }

                print(f"📄 Queued article: {title} | {url} | {date.isoformat()}")
                news.append(article_data)

            except Exception as e:
                print(f"❌ Failed to fetch article page: {url} — {e}")
                continue

    except Exception as e:
        print("Scraper error:", e)

    return news
