
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import json
from typing import Dict, List
import logging
from Util.helpers import process_article_date
import datetime
import os
import glob

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def load_config(source_id: str) -> Dict:
    """Search for and load JSON config for a publication from any African country folder."""
    try:
        # Search pattern: any JSON file under Configs/Africa/** matching the source_id
        search_pattern = os.path.join("Configs", "Africa", "*", f"{source_id}.json")
        matches = glob.glob(search_pattern)

        if not matches:
            raise FileNotFoundError(f"No config found for source_id '{source_id}' in any country folder under Configs/Africa")

        config_path = matches[0]  # take the first match

        with open(config_path, "r") as f:
            config = json.load(f)

        # Basic validation
        assert "config" in config, "Missing 'config' section"
        assert "base_url" in config["config"], "Missing base_url"
        assert "selectors" in config["config"], "Missing selectors"

        return config

    except FileNotFoundError as e:
        logger.error(str(e))
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in config file: {config_path}")
        raise
    except Exception as e:
        logger.error(f"Config load failed for {source_id}: {str(e)}")
        raise



# def scrape_publication(source_id: str, page) -> List[Dict]:
#     """Scrape articles with more lenient date processing"""
#     try:
#         config = load_config(source_id)
#         base_url = config["config"]["base_url"]
#         selectors = config["config"]["selectors"]
        
#         # Fetch page
#         page.goto(base_url, timeout=config["config"].get("timeout_ms", 60000))
#         page.wait_for_selector(selectors["article"])
        
#         soup = BeautifulSoup(page.content(), 'html.parser')
#         articles = []
        
#         for article in soup.select(selectors["article"]):
#             try:
#                 # Title
#                 title_tag = article.select_one(selectors["title"])
#                 if not title_tag:
#                     logger.warning("Skipping article: missing title")
#                     continue
                
#                 # URL
#                 url = urljoin(base_url, title_tag['href'])
                
#                 # More lenient date processing
#                 date = None
#                 try:
#                     raw_date = article.select_one(selectors.get("date", "")).text.strip() if selectors.get("date") else None
#                     date = process_article_date(
#                         url=url,
#                         soup=article,
#                         raw_date=raw_date,
#                         publication_id=source_id
#                     )
#                 except Exception as e:
#                     logger.warning(f"Date processing failed for article, defaulting to today: {str(e)}")
#                     date = datetime.datetime.now().strftime("%Y-%m-%d")
                
#                 articles.append({
#                     "date": date or datetime.datetime.now().strftime("%Y-%m-%d"),  # Default to today if still None
#                     "title": title_tag.text.strip(),
#                     "url": url,
#                     "source_name": config["meta"]["source_name"],
#                     "country": config["meta"]["country"],
#                     "source_logo": config["meta"].get("source_logo", "")
#                 })
                
#             except Exception as e:
#                 logger.warning(f"Skipping article due to error: {str(e)}")
#                 continue
                
#         return articles
        
#     except Exception as e:
#         logger.error(f"Scraping failed: {str(e)}")
#         return []


def scrape_publication(source_id: str, page) -> List[Dict]:
    """Scrape articles with more lenient date processing"""
    try:
        config = load_config(source_id)
        base_url = config["config"]["base_url"]
        selectors = config["config"]["selectors"]
        
        # Fetch page
        page.goto(base_url, timeout=config["config"].get("timeout_ms", 60000))
        page.wait_for_selector(selectors["article"])
        
        soup = BeautifulSoup(page.content(), 'html.parser')
        articles = []
        
        for article in soup.select(selectors["article"]):
            try:
                # Title
                title_tag = article.select_one(selectors["title"])
                if not title_tag:
                    logger.warning("Skipping article: missing title")
                    continue
                
                # URL
                url = urljoin(base_url, title_tag.get("href", "").strip())

                # Default to today's date unless we can extract
                date = datetime.datetime.now().strftime("%Y-%m-%d")

                # Try to extract the raw date safely
                date_selector = selectors.get("date", "")
                if date_selector:
                    date_element = article.select_one(date_selector)
                    raw_date = date_element.text.strip() if date_element else None

                    if raw_date:
                        try:
                            date = process_article_date(
                                url=url,
                                soup=article,
                                raw_date=raw_date,
                                publication_id=source_id
                            )
                        except Exception:
                            # Already defaulted above
                            logger.debug("Could not parse date, using today’s date.")

                articles.append({
                    "date": date,
                    "title": title_tag.text.strip(),
                    "url": url,
                    "source_name": config["meta"]["source_name"],
                    "country": config["meta"]["country"],
                    "source_logo": config["meta"].get("source_logo", "")
                })

            except Exception as e:
                logger.warning(f"Skipping article due to error: {str(e)}")
                continue
                
        return articles
        
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        return []
