# routes/entity.py
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import logging
from psycopg2.extras import RealDictCursor
from typing import List
from Util.helpers import (
    get_wikipedia_summary,
    extract_sentiment,
    extract_top_topics,
    extract_co_mentions,
    extract_quotes,
    build_where_clause,
    get_db_connection
)
import spacy

router = APIRouter()
logger = logging.getLogger(__name__)
nlp = spacy.load("en_core_web_sm")

@router.get("/get_entities")
async def get_entities(
    and_keywords: List[str] = Query(default=[]),
    or_keywords: List[str] = Query(default=[]),
    not_keywords: List[str] = Query(default=[]),
    sources: List[str] = Query(default=[])
):
    try:
        params = {
            'and_keywords': [kw for kw in and_keywords if kw],
            'or_keywords': [kw for kw in or_keywords if kw],
            'not_keywords': [kw for kw in not_keywords if kw],
            'sources': [s for s in sources if s]
        }

        logger.info(f"Entity request params: {params}")

        where_clause, query_params = build_where_clause(
            params['and_keywords'],
            params['or_keywords'],
            params['not_keywords'],
            params['sources']
        )

        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(f"""
                    SELECT title, date, source_name, country
                    FROM articles
                    WHERE title IS NOT NULL AND {where_clause};
                """, query_params)
                articles = cursor.fetchall()

        if not articles:
            return JSONResponse(content={
                "top_people": [],
                "total_entities_found": 0,
                "note": "No articles matched the filters."
            })

        entity_data = defaultdict(lambda: {
            "name": "", "count": 0, "dates": [],
            "sources": set(), "countries": set(), "articles": set()
        })

        for article in articles:
            title = article["title"]
            doc = nlp(title)

            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    name = ent.text.strip()
                    if len(name.split()) < 2:
                        continue

                    normalized_name = " ".join([w.capitalize() for w in name.split()])
                    entity = entity_data[normalized_name]
                    entity["name"] = normalized_name
                    entity["count"] += 1
                    entity["dates"].append(article["date"])
                    entity["sources"].add(article["source_name"])
                    entity["countries"].add(article["country"])
                    entity["articles"].add(title)

        results = []
        for entity in entity_data.values():
            articles = list(entity["articles"])
            wiki_info = get_wikipedia_summary(entity["name"])

            results.append({
                "name": entity["name"],
                "count": entity["count"],
                "article_count": len(articles),
                "sentiment": extract_sentiment(articles),
                "top_topics": extract_top_topics(articles),
                "trend": process_trend_data(entity["dates"]),
                "co_mentions": extract_co_mentions(articles, entity["name"]),
                "top_quotes": extract_quotes(articles, entity["name"]),
                "sources": list(entity["sources"]),
                "source_diversity": len(entity["sources"]),
                "country_coverage": list(entity["countries"]),
                "wiki_summary": wiki_info["summary"],
                "wiki_url": wiki_info["url"],
                "wiki_image": wiki_info["image"]
            })

        top_entities = sorted(results, key=lambda x: x["count"], reverse=True)[:50]

        return JSONResponse(content={
            "top_people": top_entities,
            "total_entities_found": len(results)
        })

    except Exception as e:
        logger.exception("Error processing get_entities request")
        return JSONResponse(content={"error": str(e)}, status_code=500)