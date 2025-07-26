# # routes/analytics.py
# from fastapi import APIRouter, Request
# from fastapi.responses import JSONResponse
# from fastapi.encoders import jsonable_encoder
# from psycopg2.extras import RealDictCursor
# import time
# import logging
# from Util.helpers import (
#     extract_keywords_cloud,
#     build_where_clause,
#     process_trend_data, get_db_connection
# )

# router = APIRouter()
# logger = logging.getLogger(__name__)


# # === Analytics Endpoint ===
# @router.get("/get_data")
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

#     except Exception as e:
#         logger.error(f"Error in /get_data: {e}", exc_info=True)
#         return JSONResponse({"error": "Internal server error"}, status_code=500)



from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from psycopg2.extras import RealDictCursor
import time
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from Util.helpers import (
    extract_keywords_cloud,
    build_where_clause,
    process_trend_data, 
    get_db_connection
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/get_data")
async def get_data(
    request: Request,
    and_terms: List[str] = Query([], alias="and"),
    or_terms: List[str] = Query([], alias="or"),
    not_terms: List[str] = Query([], alias="not"),
    sources: List[str] = Query([], alias="source")
):
    start_time = time.time()
    try:
        # Combine parameters from both sources for backward compatibility
        params = {
            "and_keywords": request.query_params.getlist("and") or and_terms,
            "or_keywords": request.query_params.getlist("or") or or_terms,
            "not_keywords": request.query_params.getlist("not") or not_terms,
            "sources": request.query_params.getlist("source") or sources
        }

        logger.info(f"Received params: {params}")

        # Return empty results if no filters are applied
        if not any(params["and_keywords"] + params["or_keywords"] + params["not_keywords"] + params["sources"]):
            return JSONResponse(content=jsonable_encoder({
                "success": True,
                "articles": [],
                "trend_data": [],
                "top_publications": [],
                "top_countries": [],
                "wordcloud_data": [],
                "total_articles": 0,
                "processing_time": "0.00s",
                "filter_applied": {
                    "and_terms": [],
                    "or_terms": [],
                    "not_terms": [],
                    "sources": []
                }
            }))

        where_clause, query_params = build_where_clause(
            params["and_keywords"],
            params["or_keywords"],
            params["not_keywords"],
            params["sources"],
        )

        logger.info(f"Executing query with WHERE: {where_clause}")
        logger.info(f"Query parameters: {query_params}")

        with get_db_connection() as conn:
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(f"""
                    SELECT title, date, url, source_name, source_logo, country
                    FROM articles
                    WHERE {where_clause}
                    ORDER BY date DESC;
                """, query_params)
                articles = cursor.fetchall()

                cursor.execute(f"""
                    SELECT date FROM articles WHERE {where_clause};
                """, query_params)
                all_dates = [row["date"] for row in cursor.fetchall()]

                cursor.execute(f"""
                    SELECT source_name, COUNT(*) as count
                    FROM articles WHERE {where_clause}
                    GROUP BY source_name ORDER BY count DESC LIMIT 10;
                """, query_params)
                top_publications = cursor.fetchall()

                cursor.execute(f"""
                    SELECT country, COUNT(*) as count
                    FROM articles WHERE {where_clause}
                    GROUP BY country ORDER BY count DESC LIMIT 10;
                """, query_params)
                top_countries = cursor.fetchall()

                cursor.execute(f"""
                    SELECT category, COUNT(*) as count
                    FROM articles WHERE {where_clause}
                    GROUP BY category ORDER BY count DESC LIMIT 5;
                """, query_params)
                content_types = cursor.fetchall()

                cursor.execute(f"""
                    SELECT sentiment, COUNT(*) as count
                    FROM articles WHERE {where_clause}
                    GROUP BY sentiment ORDER BY count DESC;
                """, query_params)
                sentiment_dist = cursor.fetchall()

            trend_data = process_trend_data(all_dates)
            wordcloud_data = extract_keywords_cloud([a["title"] for a in articles])
            processing_time = time.time() - start_time

        return JSONResponse(content=jsonable_encoder({
            "success": True,
            "articles": articles,
            "trend_data": trend_data,
            "top_publications": top_publications,
            "top_countries": top_countries,
            "wordcloud_data": wordcloud_data,
            "total_articles": len(articles),
            "processing_time": f"{processing_time:.2f}s",
            "filter_applied": {
                "and_terms": params["and_keywords"],
                "or_terms": params["or_keywords"],
                "not_terms": params["not_keywords"],
                "sources": params["sources"]
            }
        }))

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in /get_data: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )