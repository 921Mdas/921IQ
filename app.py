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


@app.route("/get_data", methods=["GET"])
def home():
    conn = None
    cursor = None
    try:
        # Extract query params
        # and_keywords = request.args.getlist("and")
        # or_keywords = request.args.getlist("or")
        # not_keywords = request.args.getlist("not")
        and_keywords = [kw for kw in request.args.getlist("and") if kw]
        or_keywords = [kw for kw in request.args.getlist("or") if kw]
        not_keywords = [kw for kw in request.args.getlist("not") if kw]

        print('Raw args:', request.args)
        print('AND keywords:', request.args.getlist("and"))
        print('OR keywords:', request.args.getlist("or"))
        print('NOT keywords:', request.args.getlist("not"))


        # Pagination logic
        page = int(request.args.get("page", 1))
        per_page = 12
        offset = (page - 1) * per_page

        # Build SQL WHERE clause
        conditions = []
        params = []

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


        # Paginated filtered articles
       # Get all filtered articles (no pagination)
        cursor.execute(f"""
            SELECT title, date, url, source_name, source_logo
            FROM articles
            WHERE {where_clause}
            ORDER BY date DESC;
        """, params)
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

        #top countries
        cursor.execute(f"""
            SELECT country, COUNT(*) as count
            FROM articles
            WHERE {where_clause}
            GROUP BY country
            ORDER BY count DESC
            LIMIT 10;
        """, params)

        top_countries_result = cursor.fetchall()

        # Prepare for chart or map use
        top_countries = [
            {"country": row["country"], "count": row["count"]}
            for row in top_countries_result
        ]

        
        return jsonify({
            "articles":articles,
            "top_publications":top_publications,
            "trend_data":trend_data,
            "wordcloud_data":wordcloud_data,
            "current_page":page,
            "total_pages":total_pages,
            "total_articles":total_articles,
            "top_countries":top_countries,
        })

    except Exception as e:
        return f"<h1>Error home route: {e}</h1>"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/get_summary", methods=["GET"])
def get_summary():
    conn = None
    cursor = None
    try:
        where_clause, params = build_where_clause(request)
        print(f"Executing query with WHERE: {where_clause}")
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(f"SELECT title FROM articles WHERE {where_clause} ORDER BY date DESC LIMIT 5;", params)
        
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



# @app.route("/get_summary", methods=["GET"])
# def get_summary():
#     conn = None
#     cursor = None
#     try:
#          # 🔒 Reject summary requests with no query
#         # if not (request.args.getlist("and") or request.args.getlist("or") or request.args.getlist("not")):
#         #     return jsonify({"summary": "No query provided", "count": 0})
        
#         where_clause, params = build_where_clause(request)
#         print(f"Executing query with WHERE: {where_clause}")  # Debug log
        
#         conn = get_db_connection()
#         cursor = conn.cursor(cursor_factory=RealDictCursor)
        
#         cursor.execute(f"SELECT title FROM articles WHERE {where_clause} ORDER BY date DESC LIMIT 5;", params)
        
#         titles = [row["title"] for row in cursor.fetchall()]
#         print(f"Found {len(titles)} titles")  # Debug log
        
#         if not titles:
#             return jsonify({"summary": "No matching articles found", "count": 0})
            
#         summary = summarize_titles(titles)
#         print('Generated summary:', summary)  # Debug log
        
#         return jsonify({
#             "summary": summary,
#             "count": len(titles)
#         })
 
#     except Exception as e:
#         return jsonify({"error summary": str(e)}), 500
#     finally:
#         if cursor: cursor.close()
#         if conn: conn.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
