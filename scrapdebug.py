from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

base_url = 'https://www.rfi.fr/fr/'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(base_url)
    
    # Get the rendered HTML content after JavaScript execution
    html = page.content()
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    print(soup.prettify())  # or just print(soup) if you prefer
    
    browser.close()
