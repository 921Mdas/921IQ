from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from Util.helpers import build_where_clause, get_db_connection
from AI import AIService

router = APIRouter()
ai_service = AIService()

@router.get("/get_summary")
async def get_articles_summary(request: Request, ):
    try:
        
        # Convert query params to lists
        query_params = {
            "and": request.query_params.getlist("and"),
            "or": request.query_params.getlist("or"),
            "not": request.query_params.getlist("not"),
            "source": request.query_params.getlist("source")
        }

        
        if not any(query_params.values()):
            return JSONResponse(
                {"success": False, "error": "At least one query parameter is required"},
                status_code=400
            )

        # 2. Build database query
        where_clause, db_params = build_where_clause(
            query_params["and"],
            query_params["or"],
            query_params["not"],
            query_params["source"]
        )



        # 3. Fetch titles
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"SELECT title FROM articles WHERE {where_clause} ORDER BY date DESC LIMIT 20",
                    db_params
                )
                titles = [row[0] for row in cursor.fetchall()]

        # 4. Prepare base response
        response = {
            "success": True,
            "count": len(titles),
            "titles": titles[:5]
        }

        # 5. Generate summary if enough articles
        if len(titles) >= 3:
            try:
                response["summary"] = ai_service.summarize(titles[:15])
            except Exception as e:
                response["summary"] = "Summary generation failed"
                response["success"] = False

        return JSONResponse(response)

    except Exception as e:
        return JSONResponse(
            {"success": False, "error": "Internal server error"},
            status_code=500
        )

# from fastapi import APIRouter, Request, HTTPException, Query
# from fastapi.responses import JSONResponse
# from typing import List
# from Util.helpers import build_where_clause, get_db_connection
# from AI import AIService
# import logging

# router = APIRouter()
# ai_service = AIService()
# logger = logging.getLogger(__name__)

# @router.get("/get_summary")
# async def get_articles_summary(
#     request: Request,
#     and_terms: List[str] = Query([], alias="and"),
#     or_terms: List[str] = Query([], alias="or"),
#     not_terms: List[str] = Query([], alias="not"),
#     sources: List[str] = Query([], alias="source")
# ):
#     try:
#         # Maintain backward compatibility with direct URL params
#         query_params = {
#             "and": request.query_params.getlist("and") or and_terms,
#             "or": request.query_params.getlist("or") or or_terms,
#             "not": request.query_params.getlist("not") or not_terms,
#             "source": request.query_params.getlist("source") or sources
#         }

#         logger.info(f"Received query params: {query_params}")

#         if not any(query_params.values()):
#             return JSONResponse(
#                 {"success": False, "error": "At least one query parameter is required"},
#                 status_code=400
#             )

#         # 2. Build database query
#         where_clause, db_params = build_where_clause(
#             query_params["and"],
#             query_params["or"],
#             query_params["not"],
#             query_params["source"]
#         )

#         logger.info(f"Generated SQL WHERE clause: {where_clause}")
#         logger.info(f"SQL parameters: {db_params}")

#         # 3. Fetch titles
#         with get_db_connection() as conn:
#             with conn.cursor() as cursor:
#                 cursor.execute(
#                     f"SELECT title FROM articles WHERE {where_clause} ORDER BY date DESC LIMIT 20",
#                     db_params
#                 )
#                 titles = [row[0] for row in cursor.fetchall()]

#         logger.info(f"Fetched {len(titles)} titles")

#         # 4. Prepare base response
#         response = {
#             "success": True,
#             "count": len(titles),
#             "titles": titles[:5]
#         }

#         # 5. Generate summary if enough articles
#         if len(titles) >= 3:
#             try:
#                 response["summary"] = ai_service.summarize(titles[:15])
#             except Exception as e:
#                 logger.error(f"Summary generation failed: {str(e)}")
#                 response["summary"] = "Summary generation failed"
#                 response["success"] = False

#         return response

#     except Exception as e:
#         logger.error(f"Internal server error: {str(e)}", exc_info=True)
#         return JSONResponse(
#             {"success": False, "error": "Internal server error"},
#             status_code=500
#         )