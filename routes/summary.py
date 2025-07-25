# from fastapi import APIRouter, Request
# from fastapi.responses import JSONResponse
# import asyncio
# import logging
# from typing import List
# from Util.helpers import (
#     build_where_clause,
#     get_db_connection
# )
# from AI import AIService

# router = APIRouter()
# logger = logging.getLogger(__name__)
# ai_service = AIService()

# SUMMARY_TIMEOUT = 10  # seconds
# SUMMARY_ARTICLE_LIMIT = 15
# TITLE_FETCH_LIMIT = 20

# @router.get("/get_summary")
# async def get_articles_summary(request: Request):
#     """
#     Fetch article titles based on query parameters, then generate a summary.
#     Gracefully handles errors and avoids blocking the event loop.
#     """
#     response = {"success": False, "processing_time_ms": 0, "error": None}
#     loop = asyncio.get_event_loop()
#     start_time = loop.time()

#     try:
#         # Extract and clean query parameters
#         params = {
#             key: [v for v in request.query_params.getlist(key) if isinstance(v, str) and v.strip()]
#             for key in ["and", "or", "not", "source"]
#         }

#         if not any(params.values()):
#             response["error"] = "At least one valid query parameter is required"
#             return JSONResponse(content=response, status_code=400)

#         # Build WHERE clause
#         try:
#             where_clause, query_params = build_where_clause(
#                 params.get("and", []),
#                 params.get("or", []),
#                 params.get("not", []),
#                 params.get("source", [])
#             )
#         except Exception as clause_err:
#             logger.error("Failed to build WHERE clause", exc_info=True)
#             response["error"] = "Invalid query parameters"
#             return JSONResponse(content=response, status_code=400)

#         # Fetch titles safely
#         async def fetch_titles() -> List[str]:
#             def db_query():
#                 with get_db_connection() as conn:
#                     with conn.cursor() as cursor:
#                         query = f"""
#                             SELECT title FROM articles
#                             WHERE {where_clause}
#                             ORDER BY date DESC
#                             LIMIT %s;
#                         """
#                         cursor.execute(query, query_params + [TITLE_FETCH_LIMIT])
#                         return [row[0] for row in cursor.fetchall()]
#             return await asyncio.to_thread(db_query)

#         try:
#             titles = await asyncio.wait_for(fetch_titles(), timeout=5)
#         except asyncio.TimeoutError:
#             response["error"] = "Database query timeout"
#             return JSONResponse(content=response, status_code=504)

#         processing_time = round((loop.time() - start_time) * 1000, 2)

#         response.update({
#             "success": True,
#             "count": len(titles),
#             "processing_time_ms": processing_time
#         })

#         if not titles:
#             response["summary"] = "No matching articles found"
#             return JSONResponse(content=response)

#         if len(titles) < 3:
#             response.update({
#                 "summary": "Insufficient articles for a meaningful summary",
#                 "titles": titles[:5]
#             })
#             return JSONResponse(content=response)

#         # Generate summary with timeout
#         try:
#             summary = await asyncio.wait_for(
#                 asyncio.to_thread(ai_service.summarize, tuple(titles[:SUMMARY_ARTICLE_LIMIT])),
#                 timeout=SUMMARY_TIMEOUT
#             )
#             response.update({
#                 "summary": summary,
#                 "titles": titles[:5]
#             })
#         except asyncio.TimeoutError:
#             logger.warning("Summary generation timed out")
#             response.update({
#                 "summary": "Summary generation timed out. Please try again later.",
#                 "titles": titles[:5]
#             })
#         except Exception as summary_err:
#             logger.error("Summary generation failed", exc_info=True)
#             response.update({
#                 "summary": "Summary currently unavailable due to internal error.",
#                 "titles": titles[:5]
#             })

#         return JSONResponse(content=response)

#     except Exception as e:
#         logger.error("Unexpected error in get_articles_summary", exc_info=True)
#         response.update({"error": "Internal server error"})
#         return JSONResponse(content=response, status_code=500)
