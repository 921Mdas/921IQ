from playwright.sync_api import sync_playwright
from fastapi import FastAPI, Query

# News
from NewsScrapers.AllScrapers import DRC_scrapers

# social
from Reddit import RedditScrap

import time
import asyncio
from playwright.async_api import async_playwright
from concurrent.futures import ThreadPoolExecutor
from typing import List, Callable

async def run_async_scraper(scraper, semaphore):
    async with semaphore:  # Limits concurrent executions
        try:
            start = time.monotonic()
            print(f"🚀 Starting {scraper.__name__}")
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                await scraper(page)
                
                await page.close()
                await context.close()
                await browser.close()
            
            print(f"✅ {scraper.__name__} completed in {time.monotonic()-start:.2f}s")
        except Exception as e:
            print(f"❌ {scraper.__name__} failed: {str(e)}")

async def run_all_async_scrapers(scrapers: List[Callable], max_concurrent: int = 10):
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = [run_async_scraper(scraper, semaphore) for scraper in scrapers]
    await asyncio.gather(*tasks, return_exceptions=True)

def run_scrapers():
    start_time = time.monotonic()
    
    # Run Playwright scrapers (async)
    asyncio.run(run_all_async_scrapers(DRC_scrapers, max_concurrent=10))
    
    # Run Reddit (sync)
    reddit_start = time.monotonic()
    RedditScrap()
    print(f"⏱️ RedditScrap took {time.monotonic()-reddit_start:.2f}s")
    
    print(f"🏁 ALL DONE in {time.monotonic()-start_time:.2f}s")

if __name__ == "__main__":
    run_scrapers()