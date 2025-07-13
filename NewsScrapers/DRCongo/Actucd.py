from NewsScrapers.Scraper_engine import scrape_publication
from NewsScrapers.publication_ids import PUBLICATIONS  # Your existing import
from ArticleDB import runDB

def ActuCdScrap(page):
    """Main scraping function that handles all publications"""
    results = {}
    
    for pub_id in PUBLICATIONS:
        try:
            articles = scrape_publication(pub_id, page)
            if articles:
                runDB(articles)
                results[pub_id] = len(articles)
            else:
                results[pub_id] = 0
        except Exception as e:
            print(f"❌ {pub_id} failed: {str(e)}")
            results[pub_id] = None
    
    # Print simple report
    print("\n=== Results ===")
    for pub_id, count in results.items():
        status = "✅" if count else "⚠️" if count == 0 else "❌"
        print(f"{status} {pub_id}: {count or 'No'} articles")
    
    return results