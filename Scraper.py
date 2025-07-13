import asyncio
from urllib.parse import urljoin
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import aiohttp
import cachetools

# Playwright imports
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

# Local imports
from helper import convert_date
from AfricaNewsSourceBase.SourceBase_DRC_News import scraper_news_sources
from ArticleDB import article_db
from article_cache import ArticleCache

# Initialize cache
listing_cache = cachetools.TTLCache(maxsize=100, ttl=3600)  # 1 hour cache

class ArticleScraper:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(10)  # Limit concurrent requests

    async def scrape_articles(self, page: Page, config: dict, source_meta: dict) -> List[dict]:
        print(f"[{source_meta['source_name']}] Starting scrape...")
        news = []
        session = aiohttp.ClientSession()
        
        try:
            # 1. Get listing page (cached if possible)
            html = await self._get_listing_page(page, config, source_meta)
            if not html:
                return []
                
            # 2. Extract article metadata without full page loads
            articles_metadata = self._extract_metadata(html, config, source_meta)
            
            # 3. Filter only new articles
            new_articles = await self._filter_new_articles(articles_metadata)
            
            # 4. Parallel processing of article details
            news = await self._process_articles(new_articles, config, source_meta, session)
            
        except Exception as e:
            print(f"Scraper error: {str(e)[:200]}")
        finally:
            await session.close()
            return news

    async def _get_listing_page(self, page: Page, config: dict, source_meta: dict) -> Optional[str]:
        """Optimized listing page fetcher with caching"""
        cache_key = f"{config['base_url']}_listing"
        
        # Try cache first
        if config.get('use_cache', True) and cache_key in listing_cache:
            return listing_cache[cache_key]
            
        try:
            await page.goto(config['base_url'], 
                           timeout=config.get('timeout', 30000),
                           wait_until="domcontentloaded")
            
            await page.wait_for_selector(config['article_container'], 
                                       timeout=10000)
            
            html = await page.content()
            
            if config.get('use_cache', True):
                listing_cache[cache_key] = html
                
            return html
        except PlaywrightTimeoutError:
            print(f"Timeout loading {source_meta['source_name']}")
            return None

    def _extract_metadata(self, html: str, config: dict, source_meta: dict) -> List[dict]:
        """Extract article metadata from HTML"""
        soup = BeautifulSoup(html, 'lxml')
        articles = []
        
        for article in config['get_articles'](soup):
            try:
                title_tag = config['get_title'](article)
                if not title_tag:
                    continue
                    
                url = urljoin(config['base_url'], title_tag.get('href', ''))
                date_tag = config.get('get_date')(article)
                date = config.get('process_date')(date_tag) if date_tag else datetime.now()
                
                articles.append({
                    'title': title_tag.text.strip(),
                    'url': url,
                    'date': date.isoformat(),
                    'source': source_meta['source_name']
                })
            except Exception:
                continue
                
        return articles

    async def _filter_new_articles(self, articles: List[dict]) -> List[dict]:
        """Deduplicate using cache"""
        return [a for a in articles if not await ArticleCache.check_exists(a['url'])]

    async def _process_articles(self, articles: List[dict], config: dict, 
                              source_meta: dict, session: aiohttp.ClientSession) -> List[dict]:
        """Process articles with proper session management"""
        tasks = [self._process_single(a, source_meta, session) for a in articles]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

    async def _process_single(self, article: dict, source_meta: dict, 
                            session: aiohttp.ClientSession) -> Optional[dict]:
        """Process a single article"""
        async with self.semaphore:
            try:
                async with session.get(article['url'], 
                                     timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        html = await resp.text()
                        soup = BeautifulSoup(html, 'lxml')
                        
                        return {
                            'title': article['title'],
                            'url': article['url'],
                            'date': article['date'],
                            'source': article['source'],
                            'country': source_meta['country'],
                            'source_logo': source_meta['source_logo'],
                            'content': "..."  # Add actual content extraction
                        }
            except Exception as e:
                print(f"Error processing {article['url']}: {str(e)[:100]}")
                return None