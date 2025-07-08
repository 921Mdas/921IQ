

from urllib.parse import urljoin
from ArticleDB import runDB
from Scraper import scrape_articles
from helper import convert_date
from AfricaNewsSourceBase.SourceBase_News import scraper_news_sources


def ActuCdScrap(page):
    source = scraper_news_sources["ActuCD"]
    config = source["config"]
    source_meta = source["source_meta"]
 
    news = scrape_articles(page, config, source_meta)
    runDB(news)
    print("[Actucd] Scraper finished.")
