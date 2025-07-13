import asyncio
import logging
from typing import Dict, Optional
from NewsScrapers.Scraper_engine import scrape_publication
from ArticleDB import article_db
from bs4 import BeautifulSoup
from AfricaNewsSourceBase.SourceBase_DRC_News import scraper_news_sources
from datetime import datetime, timedelta
from urllib.parse import urljoin



logger = logging.getLogger("CongoNews")

async def CongoDB(page, retry_count: int = 2, delay_between: int = 2) -> Dict:
    """
    Optimized Congo news scraper combining best of both approaches
    """
    publications = ["ActuCD"]
    results = {}
    failures = 0
    
    logger.info(f"Starting CongoDB scraper for {len(publications)} publications")
    
    for pub in publications:
        for attempt in range(1, retry_count + 1):
            try:
                logger.info(f"Scraping {pub} (attempt {attempt}/{retry_count})")
                
                # Use the simpler, more reliable scraping approach
                result = await simple_scrape_publication(page, pub)
                
                if result and result.get('new', 0) + result.get('updated', 0) > 0:
                    results[pub] = result
                    logger.info(f"✅ {pub} succeeded with {result.get('new', 0)} new articles")
                    break
                else:
                    logger.warning(f"⚠️ {pub} returned no new/updated articles")
                    
            except Exception as e:
                logger.error(f"❌ {pub} attempt {attempt} failed: {str(e)[:200]}")
                if attempt == retry_count:
                    failures += 1
                    logger.error(f"☠️ Final attempt failed for {pub}")
                await asyncio.sleep(attempt * 2)  # Exponential backoff
        
        await asyncio.sleep(delay_between)  # Respectful delay between sites
    
    success_rate = ((len(publications) - failures) / len(publications)) * 100
    logger.info(
        f"CongoDB completed with {success_rate:.0f}% success rate | "
        f"{len([r for r in results.values() if r])}/{len(publications)} succeeded"
    )
    
    return results

async def simple_scrape_publication(page, publication_name: str) -> Optional[Dict]:
    """Simplified scraping function based on previous working version"""
    try:
        source = scraper_news_sources[publication_name]
        config = source["config"]
        source_meta = source["source_meta"]
        
        # Load page with basic wait
        await page.goto(config['base_url'], timeout=60000)
        await page.wait_for_timeout(3000)  # Small delay for JavaScript
        
        # Get HTML and parse with BeautifulSoup
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find articles using the proven selectors
        articles = config['get_articles'](soup)
        if not articles:
            logger.warning(f"No articles found for {publication_name}")
            return None
            
        # Process articles (simplified version)
        processed_articles = []
        for article in articles:
            try:
                title_tag = config['get_title'](article)
                if not title_tag:
                    continue
                    
                url = urljoin(config['base_url'], title_tag.get('href', ''))
                date_tag = config['get_date'](article)
                date = config['process_date'](date_tag) if date_tag else datetime.now()
                
                processed_articles.append({
                    'title': title_tag.text.strip(),
                    'url': url,
                    'date': date.isoformat(),
                    'source': source_meta['source_name'],
                    'country': source_meta['country'],
                    'source_logo': source_meta['source_logo'],
                    'content': "",  # Add if needed
                    'author': 'Unknown',
                    'category': 'General'
                })
            except Exception as e:
                logger.debug(f"Skipping article: {str(e)}")
                continue
                
        if not processed_articles:
            return None
            
        # Insert to DB
        return article_db.runDB(processed_articles)
        
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        return None