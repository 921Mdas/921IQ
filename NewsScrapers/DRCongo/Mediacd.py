

from urllib.parse import urljoin
from ArticleDB import runDB
from Scraper import scrape_articles
from helper import convert_date
from AfricaNewsSourceBase.SourceBase_DRC_News import scraper_news_sources


async def MediaCdScrap(page):
    source = scraper_news_sources["MediaCongo"]
    config = source["config"]
    source_meta = source["source_meta"]
 
    news = await scrape_articles(page, config, source_meta)
    runDB(news)
    print("[MediaCongo] Scraper finished.")
