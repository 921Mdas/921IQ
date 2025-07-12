from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from ArticleDB import runDB
from bs4 import BeautifulSoup
from helper import convert_date, find_ads, testSoup
import requests

base_url = 'https://www.gabonreview.com/'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(base_url)
    
    # Get the rendered HTML content after JavaScript execution
    html = page.content()
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all('div', class_='post')
    news = []
    print(articles)  # or just print(soup) if you prefer

    # for article in articles:
            # title_tag = article
            # date_tag = article

            # if not title_tag or not date_tag:
            #     continue

            # title = title_tag.text.strip()
            # url = urljoin(base_url, title_tag.get('href'))
            # date = convert_date(date_tag.text.strip())

            # if not date:
            #     continue

            # news.append({
            #     'date': date.isoformat(),
            #     'title': title,
            #     'url': url,
            #     'source_name': 'Radio Okapi',
            #     'country': 'Dem. Rep. Congo',
            #     'source_logo': 'data:image/jpeg;base64,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'
            # })
    
    # print(news)
    browser.close()
