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
                response["summary"] = ai_service.summarize(tuple(titles[:15]))
            except Exception as e:
                response["summary"] = "Summary generation failed"
                response["success"] = False
                print('summary error')
                print(e)

        return JSONResponse(response)

    except Exception as e:
        return JSONResponse(
            {"success": False, "error": "Internal server error"},
            status_code=500
        )
