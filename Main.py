
# Standard Library
import os
import re
import time
import logging
from datetime import datetime
from collections import Counter, defaultdict
import asyncio
from fastapi import Query
from typing import List


# Third-Party Libraries
import uvicorn
import spacy
import wikipedia
import psycopg2
from psycopg2.extras import RealDictCursor
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob
from keybert import KeyBERT
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from playwright.sync_api import sync_playwright
from routes.health import router as health_router
from routes.data import router as getData_router
from routes.entity import router as getEntities_router
from routes.summary import router as getSummary_router


# Local Modules
from auth_routes import router as auth_router
from helper import extract_keywords_cloud
from AI import SummaryGenerator
from NewsScrapers.DRCongo.Actucd import ActuCdScrap


load_dotenv()
logger = logging.getLogger(__name__)

# === Init FastAPI App ===
app = FastAPI()
app.include_router(health_router)
app.include_router(getData_router)
app.include_router(getEntities_router)
app.include_router(getSummary_router)

# === Environment Mode & CORS ===
mode = os.getenv("MODE")
origins = (
    [os.getenv("PRODUCTION_DOMAIN")] if mode == "production"
    else ["http://localhost:5173", "http://127.0.0.1:5173"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Routers ===
app.include_router(auth_router, prefix="/auth")

# === AI + NLP Models ===
kw_model = KeyBERT()
summary_generator = SummaryGenerator()
nlp = spacy.load("en_core_web_sm")

# === DB Connection ===
# def get_db_connection():
#     try:
#         if mode == "production":
#             conn = psycopg2.connect(
#                 dbname=os.getenv("POSTGRES_DB_PROD"),
#                 user=os.getenv("POSTGRES_USER_PROD"),
#                 password=os.getenv("POSTGRES_PASSWORD_PROD"),
#                 host=os.getenv("POSTGRES_HOST_PROD"),
#                 port=os.getenv("POSTGRES_PORT_PROD"),
#             )
#         else:
#             conn = psycopg2.connect(
#                 dbname=os.getenv("POSTGRES_DB"),
#                 user=os.getenv("POSTGRES_USER"),
#                 password=os.getenv("POSTGRES_PASSWORD"),
#                 host=os.getenv("POSTGRES_HOST"),
#                 port=os.getenv("POSTGRES_PORT"),
#             )
#         return conn
#     except Exception as e:
#         logger.error(f"❌ Database connection failed: {e}")
#         raise

# === Util Functions ===
# def build_where_clause(and_keywords, or_keywords, not_keywords, sources):
#     conditions = []
#     params = []

#     for kw in and_keywords:
#         if kw:
#             conditions.append("LOWER(title) LIKE %s")
#             params.append(f"%{kw.lower()}%")

#     if or_keywords:
#         or_conditions = []
#         for kw in or_keywords:
#             if kw:
#                 or_conditions.append("LOWER(title) LIKE %s")
#                 params.append(f"%{kw.lower()}%")
#         if or_conditions:
#             conditions.append(f"({' OR '.join(or_conditions)})")

#     for kw in not_keywords:
#         if kw:
#             conditions.append("LOWER(title) NOT LIKE %s")
#             params.append(f"%{kw.lower()}%")

#     if sources:
#         filter_sources = sources[1:] if len(sources) > 1 else sources
#         placeholders = ",".join(["%s"] * len(filter_sources))
#         conditions.append(f"source_name IN ({placeholders})")
#         params.extend(filter_sources)

#     where_clause = " AND ".join(conditions) if conditions else "TRUE"
#     return where_clause, params

# def process_trend_data(dates):
#     date_objs = []
#     for date in dates:
#         try:
#             if isinstance(date, str):
#                 date_objs.append(datetime.fromisoformat(date))
#             elif isinstance(date, datetime):
#                 date_objs.append(date)
#         except Exception:
#             continue

#     if not date_objs:
#         return {"labels": [], "data": []}

#     formatted_dates = [date.strftime('%b %d') for date in date_objs]
#     date_counts = Counter(formatted_dates)
#     unique_dates = sorted(set(date_objs))
#     sorted_labels = [date.strftime('%b %d') for date in unique_dates]

#     return {
#         "labels": sorted_labels,
#         "data": [date_counts[label] for label in sorted_labels]
#     }

# === Health Check ===
# @app.get("/health")
# async def health():
#     return {"status": "healthy"}

# === Analytics Endpoint ===
# @app.get("/get_data")
# async def get_data(request: Request):
#     start_time = time.time()
#     try:
#         # Extract query parameters
#         params = {
#             "and_keywords": request.query_params.getlist("and"),
#             "or_keywords": request.query_params.getlist("or"),
#             "not_keywords": request.query_params.getlist("not"),
#             "sources": request.query_params.getlist("source"),
#         }

#         where_clause, query_params = build_where_clause(
#             params["and_keywords"],
#             params["or_keywords"],
#             params["not_keywords"],
#             params["sources"],
#         )

#         with get_db_connection() as conn:
#             with conn.cursor(cursor_factory=RealDictCursor) as cursor:
#                 cursor.execute(f"""
#                     SELECT title, date, url, source_name, source_logo, country
#                     FROM articles
#                     WHERE {where_clause}
#                     ORDER BY date DESC;
#                 """, query_params)
#                 articles = cursor.fetchall()

#                 cursor.execute(f"""
#                     SELECT date FROM articles WHERE {where_clause};
#                 """, query_params)
#                 all_dates = [row["date"] for row in cursor.fetchall()]

#                 cursor.execute(f"""
#                     SELECT source_name, COUNT(*) as count
#                     FROM articles WHERE {where_clause}
#                     GROUP BY source_name ORDER BY count DESC LIMIT 10;
#                 """, query_params)
#                 top_publications = cursor.fetchall()

#                 cursor.execute(f"""
#                     SELECT country, COUNT(*) as count
#                     FROM articles WHERE {where_clause}
#                     GROUP BY country ORDER BY count DESC LIMIT 10;
#                 """, query_params)
#                 top_countries = cursor.fetchall()

#                 cursor.execute(f"""
#                     SELECT category, COUNT(*) as count
#                     FROM articles WHERE {where_clause}
#                     GROUP BY category ORDER BY count DESC LIMIT 5;
#                 """, query_params)
#                 content_types = cursor.fetchall()

#                 cursor.execute(f"""
#                     SELECT sentiment, COUNT(*) as count
#                     FROM articles WHERE {where_clause}
#                     GROUP BY sentiment ORDER BY count DESC;
#                 """, query_params)
#                 sentiment_dist = cursor.fetchall()

#         trend_data = process_trend_data(all_dates)
#         wordcloud_data = extract_keywords_cloud([a["title"] for a in articles])
#         processing_time = time.time() - start_time

#         return JSONResponse(content=jsonable_encoder({
#             "articles": articles,
#             "trend_data": trend_data,
#             "top_publications": top_publications,
#             "top_countries": top_countries,
#             "content_types": content_types,
#             "sentiment_distribution": sentiment_dist,
#             "wordcloud_data": wordcloud_data,
#             "total_articles": len(articles),
#             "processing_time": f"{processing_time:.2f}s",
#             "filter_applied": {
#                 "received_sources": params["sources"],
#                 "actual_filter": params["sources"][1:] if len(params["sources"]) > 1 else params["sources"]
#             }
#         }))

        # return JSONResponse({
        #     "articles": articles,
        #     "trend_data": trend_data,
        #     "top_publications": top_publications,
        #     "top_countries": top_countries,
        #     "content_types": content_types,
        #     "sentiment_distribution": sentiment_dist,
        #     "wordcloud_data": wordcloud_data,
        #     "total_articles": len(articles),
        #     "processing_time": f"{processing_time:.2f}s",
        #     "filter_applied": {
        #         "received_sources": params["sources"],
        #         "actual_filter": params["sources"][1:] if len(params["sources"]) > 1 else params["sources"]
        #     }
        # })

    # except Exception as e:
    #     logger.error(f"Error in /get_data: {e}", exc_info=True)
    #     return JSONResponse({"error": "Internal server error"}, status_code=500)


#=== Get Summaries ===== & Get Entities ====

# @app.get("/get_summary")
# async def get_articles_summary(request: Request):
#     start_time = time.time()
#     response = {"success": False, "processing_time_ms": 0, "error": None}

#     try:
#         # Extract query parameters (multiple values per key)
#         params = {
#             'and': request.query_params.getlist("and"),
#             'or': request.query_params.getlist("or"),
#             'not': request.query_params.getlist("not"),
#             'source': request.query_params.getlist("source"),
#         }

#         # Clean parameters: filter out empty strings and non-str values
#         clean_params = {
#             k: [v for v in vals if v and isinstance(v, str)]
#             for k, vals in params.items()
#         }

#         if not any(clean_params.values()):
#             response.update({
#                 "error": "At least one valid query parameter is required",
#                 "status": 400
#             })
#             return JSONResponse(content=response, status_code=400)

#         # Build SQL WHERE clause and parameters
#         where_clause, query_params = build_where_clause(
#             clean_params['and'],
#             clean_params['or'],
#             clean_params['not'],
#             clean_params['source']
#         )

#         # Query database (blocking I/O, so run in thread pool)


#         def db_query():
#             with get_db_connection() as conn:
#                 with conn.cursor() as cursor:
#                     cursor.execute(f"""
#                         SELECT title FROM articles
#                         WHERE {where_clause}
#                         ORDER BY date DESC
#                         LIMIT 20;
#                     """, query_params)
#                     return [row[0] for row in cursor.fetchall()]

#         titles = await asyncio.to_thread(db_query)

#         # Prepare response
#         response.update({
#             "success": True,
#             "count": len(titles),
#             "processing_time_ms": round((time.time() - start_time) * 1000, 2)
#         })

#         if not titles:
#             response["summary"] = "No matching articles found"
#             return JSONResponse(content=response)

#         if len(titles) < 3:
#             response.update({
#                 "summary": "Insufficient articles for full summary",
#                 "titles": titles[:5]
#             })
#             return JSONResponse(content=response)

#         # Generate summary (assuming synchronous)
#         summary = summary_generator.summarize(tuple(titles[:15]))
#         response.update({
#             "summary": summary,
#             "titles": titles[:5]
#         })

#         return JSONResponse(content=response)

#     except Exception as e:
#         logger.error(f"Unexpected error in get_articles_summary: {str(e)}", exc_info=True)
#         response.update({"error": "Internal server error", "status": 500})
#         return JSONResponse(content=response, status_code=500)

# def get_wikipedia_summary(entity_name):
#     """Fetch Wikipedia summary for an entity"""
#     try:
#         page = wikipedia.page(entity_name, auto_suggest=False)
#         summary = wikipedia.summary(entity_name, sentences=2, auto_suggest=False)
        
#         # Find first suitable image
#         image_url = next(
#             (img for img in page.images 
#              if any(ext in img.lower() for ext in [".jpg", ".jpeg", ".png"]) 
#              and "logo" not in img.lower()),
#             ""
#         )

#         return {
#             "summary": summary,
#             "url": page.url,
#             "image": image_url
#         }

#     except (wikipedia.DisambiguationError, wikipedia.PageError, wikipedia.HTTPTimeoutError):
#         return {
#             "summary": "No Wikipedia summary available.",
#             "url": "",
#             "image": ""
#         }

# def extract_sentiment(titles):
#     """Analyze sentiment of given titles"""
#     sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
#     total_score = 0

#     for title in titles:
#         blob = TextBlob(title)
#         polarity = blob.sentiment.polarity
#         total_score += polarity

#         if polarity > 0.1:
#             sentiment_counts["positive"] += 1
#         elif polarity < -0.1:
#             sentiment_counts["negative"] += 1
#         else:
#             sentiment_counts["neutral"] += 1

#     sentiment_counts["overall_score"] = round(total_score / len(titles), 2) if titles else 0
#     return sentiment_counts

# def extract_top_topics(titles, top_n=5, diversity_threshold=0.75):
#     """Extract diverse topics from titles"""
#     combined_text = ". ".join(set(titles))
#     if not combined_text.strip():
#         return []

#     candidates = kw_model.extract_keywords(
#         combined_text,
#         keyphrase_ngram_range=(1, 3),
#         stop_words='english',
#         use_maxsum=True,
#         top_n=top_n * 3
#     )

#     unique_keywords = []
#     vectors = []

#     for kw, score in candidates:
#         vector = kw_model.model.embed([kw])[0]
#         if all(cosine_similarity([vector], [v])[0][0] < diversity_threshold for v in vectors):
#             unique_keywords.append((kw, score))
#             vectors.append(vector)
#         if len(unique_keywords) >= top_n:
#             break

#     return [kw for kw, _ in unique_keywords]

# def extract_co_mentions(titles, target_name):
#     """Extract co-mentioned names"""
#     pattern = re.compile(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b')
#     co_mentions = Counter()
#     for title in titles:
#         candidates = pattern.findall(title)
#         filtered = [c for c in candidates if c != target_name and target_name not in c]
#         co_mentions.update(filtered)
#     return [c for c, _ in co_mentions.most_common(5)]

# def extract_quotes(titles, person_name):
#     """Extract quotes mentioning a person"""
#     quote_pattern = re.compile(rf'([\w\s]*{re.escape(person_name)}[\w\s]*?said[^.]*\.)', re.IGNORECASE)
#     quotes = []
#     for title in titles:
#         matches = quote_pattern.findall(title)
#         quotes.extend(matches)
#     return quotes[:5]


# @app.get("/get_entities")
# async def get_entities(
#     and_keywords: List[str] = Query(default=[]),
#     or_keywords: List[str] = Query(default=[]),
#     not_keywords: List[str] = Query(default=[]),
#     sources: List[str] = Query(default=[])
# ):
#     """Extract and analyze entities from articles"""
#     try:
#         params = {
#             'and_keywords': [kw for kw in and_keywords if kw],
#             'or_keywords': [kw for kw in or_keywords if kw],
#             'not_keywords': [kw for kw in not_keywords if kw],
#             'sources': [s for s in sources if s]
#         }

#         logger.info(f"Entity request params: {params}")

#         where_clause, query_params = build_where_clause(
#             params['and_keywords'],
#             params['or_keywords'],
#             params['not_keywords'],
#             params['sources']
#         )

#         with get_db_connection() as conn:
#             with conn.cursor(cursor_factory=RealDictCursor) as cursor:
#                 cursor.execute(f"""
#                     SELECT title, date, source_name, country
#                     FROM articles
#                     WHERE title IS NOT NULL AND {where_clause};
#                 """, query_params)
#                 articles = cursor.fetchall()

#         if not articles:
#             return JSONResponse(content={
#                 "top_people": [],
#                 "total_entities_found": 0,
#                 "note": "No articles matched the filters."
#             })

#         entity_data = defaultdict(lambda: {
#             "name": "", "count": 0, "dates": [],
#             "sources": set(), "countries": set(), "articles": set()
#         })

#         for article in articles:
#             title = article["title"]
#             doc = nlp(title)

#             for ent in doc.ents:
#                 if ent.label_ == "PERSON":
#                     name = ent.text.strip()
#                     if len(name.split()) < 2:
#                         continue

#                     normalized_name = " ".join([w.capitalize() for w in name.split()])
#                     entity = entity_data[normalized_name]
#                     entity["name"] = normalized_name
#                     entity["count"] += 1
#                     entity["dates"].append(article["date"])
#                     entity["sources"].add(article["source_name"])
#                     entity["countries"].add(article["country"])
#                     entity["articles"].add(title)

#         results = []
#         for entity in entity_data.values():
#             articles = list(entity["articles"])
#             wiki_info = get_wikipedia_summary(entity["name"])

#             results.append({
#                 "name": entity["name"],
#                 "count": entity["count"],
#                 "article_count": len(articles),
#                 "sentiment": extract_sentiment(articles),
#                 "top_topics": extract_top_topics(articles),
#                 "trend": process_trend_data(entity["dates"]),
#                 "co_mentions": extract_co_mentions(articles, entity["name"]),
#                 "top_quotes": extract_quotes(articles, entity["name"]),
#                 "sources": list(entity["sources"]),
#                 "source_diversity": len(entity["sources"]),
#                 "country_coverage": list(entity["countries"]),
#                 "wiki_summary": wiki_info["summary"],
#                 "wiki_url": wiki_info["url"],
#                 "wiki_image": wiki_info["image"]
#             })

#         top_entities = sorted(results, key=lambda x: x["count"], reverse=True)[:50]

#         return JSONResponse(content={
#             "top_people": top_entities,
#             "total_entities_found": len(results)
#         })

#     except Exception as e:
#         logger.exception("Error processing get_entities request")
#         return JSONResponse(content={"error": str(e)}, status_code=500)
# === Scraper ===
def run_scrapers():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            ActuCdScrap(page)
            browser.close()
    except Exception as e:
        logger.error(f"❌ Browser error: {e}")
    finally:
        logger.info("✅ Scraping completed.")

if __name__ == "__main__":
    run_scrapers()
    print("🚀 Starting server with uvicorn...")
    uvicorn.run("Main:app", host="0.0.0.0", port=5000, reload=True)
