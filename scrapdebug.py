# from playwright.sync_api import sync_playwright
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin

# base_url = 'https://actualite.cd'

# with sync_playwright() as p:
#     browser = p.chromium.launch(headless=True)
#     page = browser.new_page()
#     page.goto(base_url)
    
#     # Get the rendered HTML content after JavaScript execution
#     html = page.content()
    
#     # Parse with BeautifulSoup
#     soup = BeautifulSoup(html, 'html.parser')
#     news = []
    
#     # Extract trending articles
#     for article in soup.select('.trending-top, .trending-bottom .single-bottom, .single-recent'):
#         title_elem = article.find('h2') or article.find('h4')
#         if not title_elem:
#             continue
            
#         link = title_elem.find_parent('a') or article.find('a')
#         if not link:
#             continue
            
#         title = title_elem.get_text(strip=True)
#         url = urljoin(base_url, link['href'])
#         date_elem = article.find('span', class_='color1') or article.find('span')
#         date = date_elem.get_text(strip=True) if date_elem else None
#         image = article.find('img')
#         image_url = urljoin(base_url, image['src']) if image else None
        
#         news.append({
#             'title': title,
#             'url': url,
#             'date': date,
#             'image': image_url
#         })
    
#     # Print the scraped data
#     for i, article in enumerate(news, 1):
#         print(f"\nArticle {i}:")
#         print(f"Title: {article['title']}")
#         print(f"URL: {article['url']}")
#         print(f"Date: {article['date']}")
#         print(f"Image: {article['image']}")
    
#     browser.close()


# Default debuger above, adapter below 
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin

base_url = 'https://www.gabonreview.com/'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(base_url, timeout=60000)
    
    # Wait for post blocks to be loaded
    page.wait_for_selector('.post')
    
    # Get the rendered HTML
    html = page.content()

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    posts = soup.select('.post')
    
    news = []
    
    for post in posts:
        title_tag = post.select_one('h3 a')
        title = title_tag.get_text(strip=True) if title_tag else None
        link = urljoin(base_url, title_tag['href']) if title_tag else None
        
        img_tag = post.select_one('.cover img')
        image_url = urljoin(base_url, img_tag['src']) if img_tag else None
        image_alt = img_tag.get('alt') if img_tag else None
        
        date_tag = post.select_one('.postmetadata')
        date_text = date_tag.get_text(strip=True) if date_tag else None
        
        news.append({
            'title': title,
            'link': link,
            'image_url': image_url,
            'image_alt': image_alt,
            'date': date_text
        })
    
    # Print the extracted data
    for article in news:
        print(article)

    browser.close()
