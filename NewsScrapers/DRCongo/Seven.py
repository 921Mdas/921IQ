from urllib.parse import urljoin
from ArticleDB import runDB
from Scraper import scrape_articles
from helper import convert_date
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from AfricaNewsSourceBase.SourceBase_DRC_News import scraper_news_sources


async def Sur7CDScrap(page):
    source = scraper_news_sources["Sur7CD"]
    config = source["config"]
    source_meta = source["source_meta"]

    news = await scrape_articles(page, config, source_meta)
    runDB(news)
    print("[7sur7.cd] Scraper finished.")
