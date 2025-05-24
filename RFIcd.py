from urllib.parse import urljoin
from ArticleDB import runDB
from bs4 import BeautifulSoup
from helper import convert_date

base_url = 'https://www.rfi.fr'

def RFICdScrap(page):
    try:
        actu_news = []

        page.set_extra_http_headers({"User-Agent": "Mozilla/5.0"})
        page.goto("https://www.rfi.fr/fr/tag/rdc/", timeout=60000)
        soup = BeautifulSoup(page.content(), 'html.parser')

        articles = soup.find_all('div', class_='article__infos')

        for article in articles:
            metadata_div = article.find('div', class_='article__metadata')
            if not metadata_div:
                continue
            time_tag = metadata_div.find('time')
            if not time_tag:
                continue

            raw_date = time_tag.get_text(strip=True)
            date = convert_date(raw_date)

            title_tag = article.select_one('h2')
            if not title_tag or not title_tag.text.strip():
                continue
            title = title_tag.text.strip()

            a_tag = article.select_one('div > a')
            if not a_tag or 'href' not in a_tag.attrs:
                continue
            url = urljoin(base_url, a_tag['href'])

            actu_news.append({
                'date': date.isoformat(),
                'title': title,
                'url': url,
                'source_name': 'RFI',
                'source_logo': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQFSKPQwi6ZtYU92JwnoJXgYTYXj0jcr9fGUQ&s' 
            })


        runDB(actu_news)

    except Exception as e:
        print("❌ RFI.cd Scraping error:", e)
