# routes/entity.py
from fastapi import APIRouter, Query, Request
from psycopg2.extras import RealDictCursor
import logging
from typing import List
from collections import defaultdict
import spacy

from Util.helpers import (
    get_wikipedia_summary,
    extract_sentiment,
    extract_top_topics,
    extract_co_mentions,
    extract_quotes,
    build_where_clause,
    get_db_connection,
    process_trend_data
)

router = APIRouter()
logger = logging.getLogger(__name__)
nlp = spacy.load("en_core_web_sm")  # Load once at module level

@router.get("/get_entities")
async def get_entities(
    request: Request,
    and_keywords: List[str] =  Query([], alias="and"),
    or_keywords: List[str] = Query([], alias="or"),
    not_keywords: List[str] = Query([], alias="not"),
    sources: List[str] = Query([], alias="sources")
):
    try:
        # Clean input filters
         # Combine parameters from both sources for backward compatibility
        params = {
            "and_keywords": request.query_params.getlist("and") or and_keywords,
            "or_keywords": request.query_params.getlist("or") or or_keywords,
            "not_keywords": request.query_params.getlist("not") or not_keywords,
            "sources": request.query_params.getlist("sources") or sources
        }


        where_clause, query_params = build_where_clause(
            params['and_keywords'],
            params['or_keywords'],
            params['not_keywords'],
            params['sources']
        )

        # Fetch article titles (limit to avoid NLP overload)
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(f"""
                    SELECT title, date, source_name, country
                    FROM articles
                    WHERE title IS NOT NULL AND {where_clause}
                    ORDER BY date DESC
                    LIMIT 500;
                """, query_params)
                articles = cursor.fetchall()

        if not articles:
            return {
                "top_people": [],
                "total_entities_found": 0,
                "note": "No articles matched the filters."
            }

        entity_data = defaultdict(lambda: {
            "name": "", "count": 0, "dates": [],
            "sources": set(), "countries": set(), "articles": set()
        })

        for article in articles:
            doc = nlp(article["title"])
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    name = ent.text.strip()
                    if len(name.split()) < 2:
                        continue  # Skip single-word names

                    normalized_name = " ".join([w.capitalize() for w in name.split()])
                    entity = entity_data[normalized_name]
                    entity["name"] = normalized_name
                    entity["count"] += 1
                    entity["dates"].append(article["date"])
                    entity["sources"].add(article["source_name"])
                    entity["countries"].add(article["country"])
                    entity["articles"].add(article["title"])

        results = []
        for entity in entity_data.values():
            articles_list = list(entity["articles"])
            wiki_info = get_wikipedia_summary(entity["name"]) or {}

            results.append({
                "name": entity["name"],
                "count": entity["count"],
                "article_count": len(articles_list),
                "sentiment": extract_sentiment(articles_list),
                "top_topics": extract_top_topics(articles_list),
                "trend": process_trend_data(entity["dates"]),
                "co_mentions": extract_co_mentions(articles_list, entity["name"]),
                "top_quotes": extract_quotes(articles_list, entity["name"]),
                "sources": list(entity["sources"]),
                "source_diversity": len(entity["sources"]),
                "country_coverage": list(entity["countries"]),
                "wiki_summary": wiki_info.get("summary", ""),
                "wiki_url": wiki_info.get("url", ""),
                "wiki_image": wiki_info.get("image", "")
            })

        top_entities = sorted(results, key=lambda x: x["count"], reverse=True)[:50]

        return {
            "top_people": top_entities,
            "total_entities_found": len(results)
        }

    except Exception as e:
        logger.exception("Error processing /get_entities request")
        return {"error": "Internal server error"}
