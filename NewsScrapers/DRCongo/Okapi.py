
from ArticleDB import runDB
from Scraper import scrape_articles
from AfricaNewsSourceBase.SourceBase_News import scraper_news_sources


def RadioOkapiScrap(page):

    source = scraper_news_sources["RadioOkapi"]
    config = source["config"]
    source_meta = source["source_meta"]

    news = scrape_articles(page, config, source_meta)
    runDB(news)
    print("[Radio Okapi] Scraper finished.")
