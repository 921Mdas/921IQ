

from urllib.parse import urljoin
from Scraper import scrape_articles
from helper import convert_date
from AfricaNewsSourceBase.SourceBase_DRC_News import scraper_news_sources
from ArticleDB import runDB




async def ActuCdScrap(page):
    source = scraper_news_sources["ActuCD"]
    config = source["config"]
    source_meta = source["source_meta"]
 
    news = await scrape_articles(page, config, source_meta)  # Note the await here

    print('testing news actu', news)
    runDB(news)
    print("[Actucd] Scraper finished.")