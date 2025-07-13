from flask import Flask, request, jsonify
from flask_cors import CORS
from psycopg2.extras import RealDictCursor
from helper import extract_keywords
from helper import extract_keywords_cloud
from collections import Counter
from datetime import datetime, timedelta
import psycopg2
import logging
import time
from AI import SummaryGenerator

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

summary_generator = SummaryGenerator()

def get_db_connection():
    """Create a new database connection"""
    return psycopg2.connect(
        dbname="echo_db",
        user="vongaimusvaire",
        password="MySushi32",
        host="localhost",
        port="5432"
    )


def build_where_clause(and_keywords, or_keywords, not_keywords, sources):
    """Build SQL WHERE clause from request parameters"""
    conditions = []
    params = []
    
    # Process AND keywords
    for kw in and_keywords:
        if kw:
            conditions.append("LOWER(title) LIKE %s")
            params.append(f"%{kw.lower()}%")
    
    # Process OR keywords
    if or_keywords:
        or_conditions = []
        for kw in or_keywords:
            if kw:
                or_conditions.append("LOWER(title) LIKE %s")
                params.append(f"%{kw.lower()}%")
        if or_conditions:
            conditions.append(f"({' OR '.join(or_conditions)})")
    
    # Process NOT keywords
    for kw in not_keywords:
        if kw:
            conditions.append("LOWER(title) NOT LIKE %s")
            params.append(f"%{kw.lower()}%")
    
    # Process sources
    if sources:
        filter_sources = sources[1:] if len(sources) > 1 else sources
        placeholders = ",".join(["%s"] * len(filter_sources))
        conditions.append(f"source_name IN ({placeholders})")
        params.extend(filter_sources)
    
    where_clause = " AND ".join(conditions) if conditions else "TRUE"
    return where_clause, params

def process_trend_data(dates):
    """Convert raw dates into daily trend data"""
    date_objs = []
    for date in dates:
        try:
            if isinstance(date, str):
                date_objs.append(datetime.fromisoformat(date))
            elif isinstance(date, datetime):
                date_objs.append(date)
        except (ValueError, TypeError) as e:
            logger.debug(f"Skipping invalid date {date}: {e}")
            continue

    if not date_objs:
        return {"labels": [], "data": []}

    # Format each date as "Jul 13"
    formatted_dates = [date.strftime('%b %d') for date in date_objs]
    date_counts = Counter(formatted_dates)

    # Sort labels by actual date object (not string)
    unique_dates = sorted(set(date_objs))
    sorted_labels = [date.strftime('%b %d') for date in unique_dates]

    return {
        "labels": sorted_labels,
        "data": [date_counts[label] for label in sorted_labels]
    }


# def process_trend_data(dates):
#     """Convert raw dates into trend data"""
#     date_objs = []
#     for date in dates:
#         try:
#             if isinstance(date, str):
#                 date_objs.append(datetime.fromisoformat(date))
#             elif isinstance(date, datetime):
#                 date_objs.append(date)
#         except (ValueError, TypeError) as e:
#             logger.debug(f"Skipping invalid date {date}: {e}")
#             continue
    
#     if not date_objs:
#         return {"labels": [], "data": []}
    
#     def week_start(date):
#         start = date - timedelta(days=date.weekday())
#         end = start + timedelta(days=6)
#         return f"{start.strftime('%b %d')}–{end.strftime('%b %d')}"
    
#     week_counts = Counter(week_start(date) for date in date_objs)
#     sorted_weeks = sorted(
#         week_counts.keys(),
#         key=lambda label: datetime.strptime(label.split("–")[0], "%b %d")
#     )
    
#     return {
#         "labels": sorted_weeks,
#         "data": [week_counts[week] for week in sorted_weeks]
#     }

# @app.before_request
# def initialize_ai_services():
#     """Verify environment and warm up models"""
#     try:
#         logger.info("Initializing AI services...")
#         get_summarizer()  # This will verify environment and load model
#         logger.info("AI services ready")
#     except Exception as e:
#         logger.critical(f"AI service initialization failed: {str(e)}")
#         # Consider whether to continue running without AI features

@app.after_request
def add_cors_headers(response):
    """Add CORS headers to all responses"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    return response

@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return {'status': 'healthy'}, 200

@app.route("/get_data", methods=["GET"])
def get_articles_data():
    """Comprehensive article data endpoint with all analytics"""
    start_time = time.time()
    
    try:
        # Extract and validate parameters
        params = {
            'and_keywords': [kw for kw in request.args.getlist("and") if kw],
            'or_keywords': [kw for kw in request.args.getlist("or") if kw],
            'not_keywords': [kw for kw in request.args.getlist("not") if kw],
            'sources': [s for s in request.args.getlist("source") if s]
        }
        
        logger.info(f"Request parameters: {params}")

        # Build WHERE clause and parameters
        where_clause, query_params = build_where_clause(
            params['and_keywords'],
            params['or_keywords'],
            params['not_keywords'],
            params['sources']
        )

        # Fetch base articles
        with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get filtered articles
            cursor.execute(f"""
                SELECT 
                    title, date, url, 
                    source_name, source_logo, country
                FROM articles
                WHERE {where_clause}
                ORDER BY date DESC;
            """, query_params)
            articles = cursor.fetchall()
            total_articles = len(articles)

            print(total_articles)

            # Get dates for trend analysis
            cursor.execute(f"""
                SELECT date FROM articles
                WHERE {where_clause};
            """, query_params)
            all_dates = [row["date"] for row in cursor.fetchall()]
            trend_data = process_trend_data(all_dates)

            # Get top publications
            cursor.execute(f"""
                SELECT 
                    source_name, 
                    COUNT(*) as count
                FROM articles
                WHERE {where_clause}
                GROUP BY source_name
                ORDER BY count DESC
                LIMIT 10;
            """, query_params)
            top_publications = [
                {"source_name": row["source_name"], "count": row["count"]}
                for row in cursor.fetchall()
            ]

            logger.info(f"Top publications: {top_publications}")


            # Get top countries
            cursor.execute(f"""
                SELECT 
                    country, 
                    COUNT(*) as count
                FROM articles
                WHERE {where_clause}
                GROUP BY country
                ORDER BY count DESC
                LIMIT 10;
            """, query_params)
            top_countries = [
                {"country": row["country"], "count": row["count"]}
                for row in cursor.fetchall()
            ]

            # Get content type distribution
            cursor.execute(f"""
                SELECT 
                    category,
                    COUNT(*) as count
                FROM articles
                WHERE {where_clause}
                GROUP BY category
                ORDER BY count DESC
                LIMIT 5;
            """, query_params)
            content_types = [
                {"category": row["category"], "count": row["count"]}
                for row in cursor.fetchall()
            ]

            # Get sentiment analysis
            cursor.execute(f"""
                SELECT 
                    sentiment,
                    COUNT(*) as count
                FROM articles
                WHERE {where_clause}
                GROUP BY sentiment
                ORDER BY count DESC;
            """, query_params)
            sentiment_dist = [
                {"sentiment": row["sentiment"], "count": row["count"]}
                for row in cursor.fetchall()
            ]

        # Generate word cloud data
        wordcloud_data = extract_keywords_cloud([a['title'] for a in articles])

        # Calculate performance metrics
        processing_time = time.time() - start_time
        articles_per_sec = total_articles / processing_time if processing_time > 0 else 0


        response = {
            "articles": articles,
             "trend_data": trend_data,
                "top_publications": top_publications,
                "top_countries": top_countries,
                "content_types": content_types,
                "sentiment_distribution": sentiment_dist,
                "wordcloud_data": wordcloud_data,
                "total_articles": total_articles,
            # "analytics": {
            #     "trend_data": trend_data,
            #     "top_publications": top_publications,
            #     "top_countries": top_countries,
            #     "content_types": content_types,
            #     "sentiment_distribution": sentiment_dist,
            #     "wordcloud_data": wordcloud_data,
            #     "total_articles": total_articles,

            #     "performance_metrics": {
            #         "processing_time_sec": round(processing_time, 3),
            #         "articles_per_second": round(articles_per_sec, 1),
            #         "total_articles": total_articles
            #     }
            # },
            "filter_applied": {
                "received_sources": params['sources'],
                "actual_filter": params['sources'][1:] if len(params['sources']) > 1 else params['sources']
            }
        }

        logger.info(f"Processed {total_articles} articles in {processing_time:.2f}s")
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error in /get_data: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500



@app.route("/get_summary", methods=["GET"])
def get_articles_summary():
    start_time = time.time()
    response = {
        "success": False,
        "processing_time_ms": 0,
        "error": None
    }

    try:
        # Parameter extraction with validation
        params = {
            'and': request.args.getlist("and"),
            'or': request.args.getlist("or"),
            'not': request.args.getlist("not"),
            'source': request.args.getlist("source")
        }
        
        # Clean and validate parameters
        clean_params = {
            k: [v for v in vals if v and isinstance(v, str)] 
            for k, vals in params.items()
        }
        
        if not any(clean_params.values()):
            response.update({
                "error": "At least one valid query parameter is required",
                "status": 400
            })
            return jsonify(response), 400

        # Database query
        try:
            where_clause, query_params = build_where_clause(
                clean_params['and'],
                clean_params['or'],
                clean_params['not'],
                clean_params['source']
            )
            
            with get_db_connection() as conn, conn.cursor() as cursor:
                cursor.execute(f"""
                    SELECT title FROM articles
                    WHERE {where_clause}
                    ORDER BY date DESC
                    LIMIT 20;
                """, query_params)
                titles = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            response.update({
                "error": "Database query failed",
                "status": 500
            })
            return jsonify(response), 500

        # Prepare response
        response.update({
            "success": True,
            "count": len(titles),
            "processing_time_ms": round((time.time() - start_time) * 1000, 2)
        })

        if not titles:
            response["summary"] = "No matching articles found"
            return jsonify(response), 200

        if len(titles) < 3:
            response.update({
                "summary": "Insufficient articles for full summary",
                "titles": titles[:5]
            })
            return jsonify(response), 200

        # Generate summary - KEY: Convert to tuple for caching
        summary = summary_generator.summarize(tuple(titles[:15]))
        response.update({
            "summary": summary,
            "titles": titles[:5]
        })

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        response.update({
            "error": "Internal server error",
            "status": 500
        })
        return jsonify(response), 500


if __name__ == "__main__":
    # Print available routes
    app.run(debug=True)
    print("\nAvailable routes:")
    for rule in app.url_map.iter_rules():
        if "static" not in rule.endpoint:
            print(f"- {rule}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)