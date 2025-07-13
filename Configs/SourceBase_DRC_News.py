from urllib.parse import urljoin
from helper import convert_date, extract_sur7cd_date
from functools import partial
import cachetools

# Configure cache for article listings (1 hour TTL)
listing_cache = cachetools.TTLCache(maxsize=1000, ttl=3600)

def make_article_lambda(selector):
    """Factory for article selector lambdas"""
    return lambda soup: soup.select(selector)

def make_element_lambda(selector):
    """Factory for element selector lambdas"""
    return lambda article: article.select_one(selector)

scraper_news_sources = {
 
    "ActuCD": {
    "config": {
        "base_url": "https://actualite.cd",
        "get_articles": lambda soup: soup.select(".trending-top, .trending-bottom .single-bottom, .single-recent"),
        
        "get_title": lambda article: (
            article.find('h2') or 
            article.find('h4')
        ),
        
        "get_date": lambda article: (
            article.find('span', class_='color1') or 
            article.find('span')
        ),
        
        "get_url": lambda article, base_url: urljoin(
            base_url,
            (article.find('h2') or article.find('h4')).find_parent('a')["href"] if (article.find('h2') or article.find('h4')) 
            else article.find('a')["href"]
        ),
        
        "get_image": lambda article, base_url: urljoin(
            base_url,
            article.find('img')['src']
        ) if article.find('img') else None,
        
        "process_date": lambda tag: tag.get_text(strip=True) if tag else None,
        
        "timeout": 60000,
        "retries": 3,
        "required_selectors": [".trending-top", ".single-recent", "h2, h4"]
    },
    "source_meta": {
        "source_name": "Actualite.cd",
        "country": "Dem. Rep. Congo",
        "source_logo": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBw0ODQ8QEA8VEBAQFw0QDQ8ODhIPDg8QFhIWGBURFhUYHSggGBolGxMVITEhJSkrLi4uFx8zODMtNygtLisBCgoKDg0OFw0OEisdFRkrKystLSsrKysrLSsrKysrLTcrKysrKysrKystKysrKysrKysrKysrKysrKysrKysrK//AABEIAOEA4QMBIgACEQEDEQH/xAAcAAEBAAIDAQEAAAAAAAAAAAAAAQcIBAUGAgP/xAA7EAACAQMBBgMFBwEA/wAAAAAAAQIDBBEFBgcSITFBIlFxExQjMmEIQoGRoRUzUmJyscEkNZLwJUTR/8QAFAEBAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AM4AAAUhQIAABSFAEAAiPPPaqitTdhLCnhSi2+bysnoka0bw9dlQ2m94jLnSlBPHkuqA2XBwNC1KF3a0q8HlTjF/jjmc/IAFIBQCAAAAKQoEAAApCgCAAUAAQFAEKABAUAQoAEBSAfFSfDGUn0SbNP8Abq59rql1LtxzS/M231efBa1peUJv9DTXWanHdV5ec5v9QM77gNo1Vtp2c5eKk800+riZfNRN3WuOw1OhVziLlGM/Rs23o1IzjGcXlSSafZoD9SAoAhQBAUAQpAAyDpaO0NtUvJWlOXHVhzqcLyo/RndIAUACAoAAACAAAUhQIAABSFAgAA6bbGv7PTbqXTwT/sadVpcU5Pzbf6m2W9CrwaPcvzjg1KAJ4aa6rmjardHrqvdKpJyzOklCfPnyNVTJe43aH3XUfYSfgr8ks8uL/rA2WBGUCkKQAARgJHid6G2lPSrOUYyTuKicacU+az3O82t2ho6ZZ1Liq/lWIR7yl2RqdtNrlfUbqpcVZNuTfCm/lj2QGbNwFrOcLq7q+KdWXzPmzMCPC7mrF0dGo56z8TPdACkKBAABQABAUAQoAEBQBCgAQFIB4TfNX4NGq/XCNWTZ/fh/s8/VGsAA5WmXsrevTrRfOEoy5fRnFAG5uzWpq8sqFdP54wb9ccztDE24DXHXsp28nl0Xy88MyyBSAAD861WMIylJ4jFNyb8kfoYh337cO2pe428viVP3sk+cY+QGO97W20tTu3Spy/09FtRS6Sku54OhHinCPm4r82fDZ2uy1n7e/t6ePmnD9GBtnsdbex023h5Qj/Y7k/G0pcFKEf4VFfofsAKABAUAAABAAAKQoEAAApCgCAAdNtTokNQs6ttP7yfC/J9jV/afZ25025nRrQa4W1GeOUl2ZuTwnWa5oFnf03C4pRmvNrmvxA0xBsHrW420qNyt6rpvtF/KjFO3Gw9XSa9Ki6iqzq/Io9QOVut2jqaddVJwXEnHnB9zJ1pvytM8NahKElyfXBgi4tbm0rKM4unUWMLu8mQbTYG/urBXNah1WY8P7zHngDL2l7ztIuEvjKDfaXI7yltPp0ul1T/5o1J1rSJ2su/D594vyZwYTqv5ZS5dcNgbQbfbxbTTrWTo1I1a08qmovOPqzWTVdRrXVedarJynNttt/oew0Hdlqs6kVdZpw7t9WZf2X3Zadp8Yy9mp1F1lJZ5gYh3d7v7rUa8K1eEoW8Wm3JY4/obJ6TptG0oQo0oqMILSjaQpxUYxUYrokfqAKQoAgAFAABAAAKQoEAAApCgSAAGFN+2z3tKEb2nHx0+VTHeJlg4OtadC7tqtvNZjUi4v8QNNj1O7PXf2fqVKbfgn4J+jPPbS6RU0+8rW81jhk3D1i+hwIScWmujTygN1aNRTipReVJJp+aaP0MX7lNtI3tvG0rS/1VFYjnrOJlACkKQAAUAAQAAAFAAEAAApCgQAAf/9k=",
        "language": "French",
        "category": "general",
    }
}
}

# Add dynamic priority sorting
PRIORITY_ORDER = {1: 0, 2: 1, 3: 2}
scraper_news_sources = dict(sorted(
    scraper_news_sources.items(),
    key=lambda x: PRIORITY_ORDER.get(x[1]["config"].get("priority", 3), 3)
))