# from playwright.sync_api import sync_playwright
# from fastapi import FastAPI, Query

# # News
# from NewsScrapers.AllScrapers import DRC_scrapers
# from NewsScrapers.AllScrapers import Gabon_scrapers

# # social
# from Reddit import RedditScrap

# import time
# import asyncio
# from playwright.async_api import async_playwright
# from concurrent.futures import ThreadPoolExecutor
# from typing import List, Callable

# async def run_async_scraper(scraper, semaphore):
#     async with semaphore:  # Limits concurrent executions
#         try:
#             start = time.monotonic()
#             print(f"🚀 Starting {scraper.__name__}")
            
#             async with async_playwright() as p:
#                 browser = await p.chromium.launch(headless=True)
#                 context = await browser.new_context()
#                 page = await context.new_page()
                
#                 await scraper(page)
                
#                 await page.close()
#                 await context.close()
#                 await browser.close()
            
#             print(f"✅ {scraper.__name__} completed in {time.monotonic()-start:.2f}s")
#         except Exception as e:
#             print(f"❌ In Main.py {scraper.__name__} failed: {str(e)}")

# async def run_all_async_scrapers(scrapers: List[Callable], max_concurrent: int = 10):
#     semaphore = asyncio.Semaphore(max_concurrent)
#     tasks = [run_async_scraper(scraper, semaphore) for scraper in scrapers]
#     await asyncio.gather(*tasks, return_exceptions=True)

# def run_scrapers():
#     start_time = time.monotonic()
    
#     # Run Playwright scrapers (async)
#     async def run_all():
#           await run_all_async_scrapers(DRC_scrapers + Gabon_scrapers, max_concurrent=3)

#     # asyncio.run(run_all_async_scrapers(DRC_scrapers, max_concurrent=10))
#     # asyncio.run(run_all_async_scrapers(Gabon_scrapers, max_concurrent=10))
    
#     # Run Reddit (sync)
#     reddit_start = time.monotonic()
#     RedditScrap()
#     print(f"⏱️ RedditScrap took {time.monotonic()-reddit_start:.2f}s")
    
#     print(f"🏁 ALL DONE in {time.monotonic()-start_time:.2f}s")

# if __name__ == "__main__":
#     run_scrapers()

import time
import asyncio
from fastapi import FastAPI, Query
from playwright.async_api import async_playwright
from typing import List, Callable

# News scrapers
from NewsScrapers.AllScrapers import DRC_scrapers, Gabon_scrapers

# Social scrapers
from Reddit import RedditScrap

# Async scraper runner using shared browser
async def run_async_scraper(scraper, browser, semaphore):
    async with semaphore:
        try:
            start = time.monotonic()
            print(f"🚀 Starting {scraper.__name__}")

            context = await browser.new_context()
            page = await context.new_page()

            await scraper(page)

            await page.close()
            await context.close()

            print(f"✅ {scraper.__name__} completed in {time.monotonic() - start:.2f}s")
        except Exception as e:
            print(f"❌ {scraper.__name__} failed: {str(e)}")

# Run all scrapers in parallel using shared browser and limited concurrency
async def run_all_async_scrapers(scrapers: List[Callable], max_concurrent: int = 3):
    semaphore = asyncio.Semaphore(max_concurrent)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        tasks = [run_async_scraper(scraper, browser, semaphore) for scraper in scrapers]
        await asyncio.gather(*tasks)
        await browser.close()

# Combine both scraper groups in a single run
async def run_all():
    all_scrapers = DRC_scrapers
    await run_all_async_scrapers(all_scrapers, max_concurrent=3)

# Entrypoint function
def run_scrapers():
    start_time = time.monotonic()

    # Run all news scrapers asynchronously
    asyncio.run(run_all())

    # Run Reddit scraper synchronously
    reddit_start = time.monotonic()
    RedditScrap()
    print(f"⏱️ RedditScrap took {time.monotonic() - reddit_start:.2f}s")

    print(f"🏁 ALL DONE in {time.monotonic() - start_time:.2f}s")

# Main
if __name__ == "__main__":
    run_scrapers()
