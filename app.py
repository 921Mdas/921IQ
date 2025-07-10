from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from helper import extract_keywords
from helper import  build_where_clause
from collections import Counter
from datetime import datetime, timedelta
from AI import summarize_titles


app = Flask(__name__)
CORS(app)


def get_db_connection():
    return psycopg2.connect(
        dbname="echo",
        user="vongaimusvaire",
        password="MySushi32",
        host="localhost",
        port="5432"
    )

@app.route('/health')
def health_check():
    return {'status': 'healthy'}, 200


# @app.route("/get_data", methods=["GET"])
# def home():
#     conn = None
#     cursor = None
#     try:
#         # Extract query params
#         and_keywords = [kw for kw in request.args.getlist("and") if kw]
#         or_keywords = [kw for kw in request.args.getlist("or") if kw]
#         not_keywords = [kw for kw in request.args.getlist("not") if kw]

#         print('Raw args:', request.args)
#         print('AND keywords:', request.args.getlist("and"))
#         print('OR keywords:', request.args.getlist("or"))
#         print('NOT keywords:', request.args.getlist("not"))


#         # Pagination logic
#         page = int(request.args.get("page", 1))
#         per_page = 12
#         offset = (page - 1) * per_page

#         # Build SQL WHERE clause
#         conditions = []
#         params = []

#         for kw in and_keywords:
#             conditions.append("LOWER(title) LIKE %s")
#             params.append(f"%{kw.lower()}%")

#         if or_keywords:
#             or_clause = " OR ".join(["LOWER(title) LIKE %s" for _ in or_keywords])
#             conditions.append(f"({or_clause})")
#             params.extend([f"%{kw.lower()}%" for kw in or_keywords])

#         for kw in not_keywords:
#             conditions.append("LOWER(title) NOT LIKE %s")
#             params.append(f"%{kw.lower()}%")

#         where_clause = " AND ".join(conditions) if conditions else "TRUE"

#         conn = get_db_connection()
#         cursor = conn.cursor(cursor_factory=RealDictCursor)

#         # Total filtered article count
#         cursor.execute(f"""
#             SELECT COUNT(*) FROM articles
#             WHERE {where_clause};
#         """, params)
#         total_articles = cursor.fetchone()["count"]
#         total_pages = (total_articles + per_page - 1) // per_page


#         # Paginated filtered articles
#        # Get all filtered articles (no pagination)
#         cursor.execute(f"""
#             SELECT title, date, url, source_name, source_logo
#             FROM articles
#             WHERE {where_clause}
#             ORDER BY date DESC;
#         """, params)
#         articles = cursor.fetchall()

#         # All filtered article dates (for trend data)
#         cursor.execute(f"""
#             SELECT date FROM articles
#             WHERE {where_clause};
#         """, params)
#         all_dates = [row["date"] for row in cursor.fetchall()]

#         # Convert ISO date to datetime
#         date_objs = [datetime.fromisoformat(date) for date in all_dates]

#         # Helper to get start of the week (Monday)
#         def week_start(date):
#             start = date - timedelta(days=date.weekday())
#             end = start + timedelta(days=6)
#             return f"{start.strftime('%b %d')}–{end.strftime('%b %d')}"

#         # Count mentions per week
#         week_counts = Counter(week_start(date) for date in date_objs)

#         # Sort weeks chronologically by actual date
#         sorted_weeks = sorted(
#             week_counts.keys(),
#             key=lambda label: datetime.strptime(label.split("–")[0], "%b %d")
#         )

#         # Create trend data
#         trend_data = {
#             "labels": sorted_weeks,
#             "data": [week_counts[week] for week in sorted_weeks]
# }


#         # All filtered titles (for wordcloud)
#         cursor.execute(f"""
#             SELECT title FROM articles
#             WHERE {where_clause};
#         """, params)
#         all_titles = [row["title"] for row in cursor.fetchall()]
#         wordcloud_data = extract_keywords(all_titles)

#         # Top Publications (by source_name)
#         cursor.execute(f"""
#             SELECT source_name, COUNT(*) as count
#             FROM articles
#             WHERE {where_clause}
#             GROUP BY source_name
#             ORDER BY count DESC
#             LIMIT 10;
#         """, params)
#         top_publications_result = cursor.fetchall()

#         top_publications = {
#             "labels": [row["source_name"] for row in top_publications_result],
#             "data": [row["count"] for row in top_publications_result]
#         }

#         #top countries
#         cursor.execute(f"""
#             SELECT country, COUNT(*) as count
#             FROM articles
#             WHERE {where_clause}
#             GROUP BY country
#             ORDER BY count DESC
#             LIMIT 10;
#         """, params)

#         top_countries_result = cursor.fetchall()

#         # Prepare for chart or map use
#         top_countries = [
#             {"country": row["country"], "count": row["count"]}
#             for row in top_countries_result
#         ]

        
#         return jsonify({
#             "articles":articles,
#             "top_publications":top_publications,
#             "trend_data":trend_data,
#             "wordcloud_data":wordcloud_data,
#             "current_page":page,
#             "total_pages":total_pages,
#             "total_articles":total_articles,
#             "top_countries":top_countries,
#         })

#     except Exception as e:
#         return f"<h1>Error home route: {e}</h1>"

#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()

@app.route("/get_data", methods=["GET"])
def home():
    conn = None
    cursor = None
    try:
        # Extract query params
        and_keywords = [kw for kw in request.args.getlist("and") if kw]
        or_keywords = [kw for kw in request.args.getlist("or") if kw]
        not_keywords = [kw for kw in request.args.getlist("not") if kw]
        sources = request.args.getlist("source")


        print('Raw args:', request.args)
        print('AND keywords:', request.args.getlist("and"))
        print('OR keywords:', request.args.getlist("or"))
        print('NOT keywords:', request.args.getlist("not"))
        print("Received sources:", request.args.getlist("source"))


        # Pagination logic
        page = int(request.args.get("page", 1))
        per_page = 12
        offset = (page - 1) * per_page

        # Build SQL WHERE clause
        conditions = []
        params = []

        # Add keyword conditions
        for kw in and_keywords:
            conditions.append("LOWER(title) LIKE %s")
            params.append(f"%{kw.lower()}%")

        if or_keywords:
            or_clause = " OR ".join(["LOWER(title) LIKE %s" for _ in or_keywords])
            conditions.append(f"({or_clause})")
            params.extend([f"%{kw.lower()}%" for kw in or_keywords])

        for kw in not_keywords:
            conditions.append("LOWER(title) NOT LIKE %s")
            params.append(f"%{kw.lower()}%")

        # Add source filtering if sources parameter exists
        if sources:
            # Skip first element if multiple sources (for news), keep if single (for social)
            filter_sources = sources[1:] if len(sources) > 1 else sources
            placeholders = ",".join(["%s"] * len(filter_sources))
            conditions.append(f"source_name IN ({placeholders})")
            params.extend(filter_sources)

        where_clause = " AND ".join(conditions) if conditions else "TRUE"

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Total filtered article count
        cursor.execute(f"""
            SELECT COUNT(*) FROM articles
            WHERE {where_clause};
        """, params)
        total_articles = cursor.fetchone()["count"]
        total_pages = (total_articles + per_page - 1) // per_page

        # Get paginated filtered articles
        cursor.execute(f"""
            SELECT title, date, url, source_name, source_logo
            FROM articles
            WHERE {where_clause}
            ORDER BY date DESC
            LIMIT %s OFFSET %s;
        """, params + [per_page, offset])
        articles = cursor.fetchall()

        # All filtered article dates (for trend data)
        cursor.execute(f"""
            SELECT date FROM articles
            WHERE {where_clause};
        """, params)
        all_dates = [row["date"] for row in cursor.fetchall()]

        # Convert ISO date to datetime
        date_objs = [datetime.fromisoformat(date) for date in all_dates]

        # Helper to get start of the week (Monday)
        def week_start(date):
            start = date - timedelta(days=date.weekday())
            end = start + timedelta(days=6)
            return f"{start.strftime('%b %d')}–{end.strftime('%b %d')}"

        # Count mentions per week
        week_counts = Counter(week_start(date) for date in date_objs)

        # Sort weeks chronologically by actual date
        sorted_weeks = sorted(
            week_counts.keys(),
            key=lambda label: datetime.strptime(label.split("–")[0], "%b %d")
        )

        # Create trend data
        trend_data = {
            "labels": sorted_weeks,
            "data": [week_counts[week] for week in sorted_weeks]
        }

        # All filtered titles (for wordcloud)
        cursor.execute(f"""
            SELECT title FROM articles
            WHERE {where_clause};
        """, params)
        all_titles = [row["title"] for row in cursor.fetchall()]
        wordcloud_data = extract_keywords(all_titles)

        # Top Publications (by source_name)
        cursor.execute(f"""
            SELECT source_name, COUNT(*) as count
            FROM articles
            WHERE {where_clause}
            GROUP BY source_name
            ORDER BY count DESC
            LIMIT 10;
        """, params)
        top_publications_result = cursor.fetchall()

        top_publications = {
            "labels": [row["source_name"] for row in top_publications_result],
            "data": [row["count"] for row in top_publications_result]
        }

        # Top countries
        cursor.execute(f"""
            SELECT country, COUNT(*) as count
            FROM articles
            WHERE {where_clause}
            GROUP BY country
            ORDER BY count DESC
            LIMIT 10;
        """, params)
        top_countries_result = cursor.fetchall()

        top_countries = [
            {"country": row["country"], "count": row["count"]}
            for row in top_countries_result
        ]

        return jsonify({
            "articles": articles,
            "top_publications": top_publications,
            "trend_data": trend_data,
            "wordcloud_data": wordcloud_data,
            "current_page": page,
            "total_pages": total_pages,
            "total_articles": total_articles,
            "top_countries": top_countries,
            "filter_applied": {
                "received_sources": sources,
                "actual_filter": filter_sources if sources else None
            }
        })

    except Exception as e:
        print(f"Error in /get_data: {str(e)}")  # Add this for debugging
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# @app.route("/get_summary", methods=["GET"])
# def get_summary():
    conn = None
    cursor = None
    try:
        where_clause, params = build_where_clause(request)
        print(f"Executing query with WHERE: {where_clause}")
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(f"SELECT title FROM articles WHERE {where_clause} ORDER BY date DESC LIMIT 20;", params)
        
        titles = [row["title"] for row in cursor.fetchall()]
        print(f"Found {len(titles)} titles")
        
        if not titles:
            return jsonify({"summary": "No matching articles found", "count": 0})
        
        summary = summarize_titles(titles)  # or cached_summarize_titles(tuple(titles))
        print("Generated summary:", summary)
        
        return jsonify({
            "summary": summary,
            "count": len(titles)
        })

    except Exception as e:
        return jsonify({"error summary": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@app.route("/get_summary", methods=["GET"])
def get_summary():
    conn = None
    cursor = None
    try:
        # Extract the same parameters as get_data
        and_keywords = [kw for kw in request.args.getlist("and") if kw]
        or_keywords = [kw for kw in request.args.getlist("or") if kw]
        not_keywords = [kw for kw in request.args.getlist("not") if kw]
        sources_param = request.args.get("sources", "")

        # Build the same WHERE clause as get_data
        conditions = []
        params = []

        # Keyword conditions (same as get_data)
        for kw in and_keywords:
            conditions.append("LOWER(title) LIKE %s")
            params.append(f"%{kw.lower()}%")

        if or_keywords:
            or_clause = " OR ".join(["LOWER(title) LIKE %s" for _ in or_keywords])
            conditions.append(f"({or_clause})")
            params.extend([f"%{kw.lower()}%" for kw in or_keywords])

        for kw in not_keywords:
            conditions.append("LOWER(title) NOT LIKE %s")
            params.append(f"%{kw.lower()}%")

        # Source filtering (same as get_data)
        if sources_param:
            sources = [s.strip() for s in sources_param.split(",") if s.strip()]
            if sources:
                filter_sources = sources[1:] if len(sources) > 1 else sources
                placeholders = ",".join(["%s"] * len(filter_sources))
                conditions.append(f"source_name IN ({placeholders})")
                params.extend(filter_sources)

        where_clause = " AND ".join(conditions) if conditions else "TRUE"

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get titles for summarization (with same filters as get_data)
        cursor.execute(f"""
            SELECT title FROM articles 
            WHERE {where_clause}
            ORDER BY date DESC 
            LIMIT 20;
        """, params)
        
        titles = [row["title"] for row in cursor.fetchall()]
        print(f"Found {len(titles)} titles for summarization")
        
        if not titles:
            return jsonify({"summary": "No matching articles found", "count": 0})
        
        # Ensure we have enough quality titles
        if len(titles) < 5:  # Minimum threshold
            # Fallback to broader search if filtered too much
            cursor.execute("""
                SELECT title FROM articles
                ORDER BY date DESC
                LIMIT 20;
            """)
            fallback_titles = [row["title"] for row in cursor.fetchall()]
            print(f"Using fallback titles (n={len(fallback_titles)})")
            titles = fallback_titles[:5]  # Take top 5 as fallback

        summary = summarize_titles(titles)
        print("Generated summary:", summary)
        
        return jsonify({
            "summary": summary,
            "count": len(titles),
            "used_fallback": len(titles) < 5  # Indicate if fallback was used
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
