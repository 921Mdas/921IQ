# routes/summary.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import time
import logging
import asyncio
from Util.helpers import (
    extract_keywords_cloud,
    build_where_clause,
    process_trend_data, get_db_connection
)
from AI import SummaryGenerator

router = APIRouter()
logger = logging.getLogger(__name__)
summary_generator = SummaryGenerator()

@router.get("/get_summary")
async def get_articles_summary(request: Request):
    start_time = time.time()
    response = {"success": False, "processing_time_ms": 0, "error": None}

    try:
        params = {
            'and': request.query_params.getlist("and"),
            'or': request.query_params.getlist("or"),
            'not': request.query_params.getlist("not"),
            'source': request.query_params.getlist("source"),
        }

        clean_params = {
            k: [v for v in vals if v and isinstance(v, str)]
            for k, vals in params.items()
        }

        if not any(clean_params.values()):
            response.update({
                "error": "At least one valid query parameter is required",
                "status": 400
            })
            return JSONResponse(content=response, status_code=400)

        where_clause, query_params = build_where_clause(
            clean_params['and'],
            clean_params['or'],
            clean_params['not'],
            clean_params['source']
        )

        def db_query():
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""
                        SELECT title FROM articles
                        WHERE {where_clause}
                        ORDER BY date DESC
                        LIMIT 20;
                    """, query_params)
                    return [row[0] for row in cursor.fetchall()]

        titles = await asyncio.to_thread(db_query)

        response.update({
            "success": True,
            "count": len(titles),
            "processing_time_ms": round((time.time() - start_time) * 1000, 2)
        })

        if not titles:
            response["summary"] = "No matching articles found"
            return JSONResponse(content=response)

        if len(titles) < 3:
            response.update({
                "summary": "Insufficient articles for full summary",
                "titles": titles[:5]
            })
            return JSONResponse(content=response)

        summary = summary_generator.summarize(tuple(titles[:15]))
        response.update({
            "summary": summary,
            "titles": titles[:5]
        })

        return JSONResponse(content=response)

    except Exception as e:
        logger.error(f"Unexpected error in get_articles_summary: {str(e)}", exc_info=True)
        response.update({"error": "Internal server error", "status": 500})
        return JSONResponse(content=response, status_code=500)