

from ArticleDB import runDB
from Scraper import scrape_articles
from AfricaNewsSourceBase.SourceBase_DRC_News import scraper_news_sources


async def RFICdScrap(page):

    source = scraper_news_sources["RFICD"]
    config = source["config"]
    source_meta = source["source_meta"]
   
    news = await scrape_articles(page, config, source_meta)
    runDB(news)
    print("[RFI] Scraper finished.")
