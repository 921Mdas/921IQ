from playwright.sync_api import sync_playwright
from RFIcd import RFICdScrap
from Actucd import ActuCdScrap


def run_scrapers():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()

            rfi_page = context.new_page()
            RFICdScrap(rfi_page)

            actu_page = context.new_page()
            ActuCdScrap(actu_page)

            browser.close()
    except Exception as e:
        print('❌ Something went wrong:')
        print(e)
    finally:
        print('✅ Scrapers ran successfully!')


if __name__ == "__main__":
    run_scrapers()

