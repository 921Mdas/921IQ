from ArticleDB import runDB
from Scraper import scrape_articles
from AfricaNewsSourceBase.SourceBase_Gabon_News import scraper_news_sources



# Dictionary to hold scraper functions for each publication
scraper_functions = {}

# Dynamically create async functions for each source
for source_key, source_data in scraper_news_sources.items():
    async def scraper_function(page, key=source_key):
        source = scraper_news_sources[key]
        config = source["config"]
        source_meta = source["source_meta"]
        news = await scrape_articles(page, config, source_meta)
        runDB(news)
        print(f"[{source_meta['source_name']}] Scraper finished.")
    
    scraper_functions[source_key] = scraper_function

# Optional: Explicit function names for direct imports
GabonReviewScrap = scraper_functions["GabonReview"]
LUnionScrap = scraper_functions["LUnion"]
GabonActuScrap = scraper_functions["GabonActu"]
Info241Scrap = scraper_functions["Info241"]
GabonMediaTimeScrap = scraper_functions["GabonMediaTime"]
