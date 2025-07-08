from playwright.sync_api import sync_playwright
from fastapi import FastAPI, Query

# News
from NewsScrapers.AllScrapers import DRC_scrapers


# social
from Reddit import RedditScrap



def run_scrapers():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()

            for scraper in DRC_scrapers:
                page = context.new_page()
                print(f"📰 Running {scraper.__name__}")
                scraper(page)

            browser.close()

        RedditScrap()

    except Exception as e:
        print('❌ Something went wrong:')
        print(e)
    finally:
        print('✅ Scrapers ran successfully!')


if __name__ == "__main__":
    run_scrapers()


