from playwright.sync_api import sync_playwright
from NewsScrapers.DRCongo.Actucd import ActuCdScrap  # No changes needed

def run_scrapers():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()  # Single page for all
            
            ActuCdScrap(page)  # Still calls the same function
            
            browser.close()
    except Exception as e:
        print('❌ Browser error:', e)
    finally:
        print('✅ Done')

if __name__ == "__main__":
    run_scrapers()