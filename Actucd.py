from urllib.parse import urljoin
from ArticleDB import runDB
from bs4 import BeautifulSoup
from helper import convert_date, find_ads, testSoup
import requests

base_url = 'https://actualite.cd'

# adSoup = testSoup(base_url)
# find_ads( adSoup)




def ActuCdScrap(page):
    try:
        actu_news = []
        page.set_extra_http_headers({"User-Agent": "Mozilla/5.0"})
        page.goto("https://actualite.cd/", timeout=60000)
        page.wait_for_selector("div.what-cap")  # Ensure content is loaded

        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        articles = soup.find_all('div', class_='what-cap')

        for article in articles:
            date_tag = article.select_one('span')
            title_tag = article.select_one('h4 > a')

            if not (date_tag and title_tag and title_tag.get('href')):
                continue

            # Convert date text (e.g., "20 mai 2025") to date object
            date = convert_date(date_tag.text.strip())
            if date is None:
                # Skip or log that date conversion failed
                # print(f"Warning: could not parse date: {date_tag.text.strip()}")
                continue
            title = title_tag.text.strip()
            url = urljoin(base_url, title_tag.get('href'))

            actu_news.append({
                'date': date.isoformat(),
                'title': title,
                'url': url,
                'source_name': 'Actualite.cd',
                'country':'Dem. Rep. Congo',
                'source_logo': 'data:image/png;base64,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'  # Replace with real or static logo
            })
         

        runDB(actu_news)

    except Exception as e:
        print("❌ Actualite.cd Scraping error:", e)
