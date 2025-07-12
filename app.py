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


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    return response


def get_db_connection():
    return psycopg2.connect(
        dbname="echo_db",
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
        and_keywords = [kw for kw in request.args.getlist("and") if kw]
        or_keywords = [kw for kw in request.args.getlist("or") if kw]
        not_keywords = [kw for kw in request.args.getlist("not") if kw]
        sources = request.args.getlist("source")

        print('Raw args:', request.args)
        print('AND keywords:', and_keywords)
        print('OR keywords:', or_keywords)
        print('NOT keywords:', not_keywords)
        print("Received sources:", sources)

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
            filter_sources = sources[1:] if len(sources) > 1 else sources
            placeholders = ",".join(["%s"] * len(filter_sources))
            conditions.append(f"source_name IN ({placeholders})")
            params.extend(filter_sources)

        where_clause = " AND ".join(conditions) if conditions else "TRUE"

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get ALL filtered articles (no pagination)
        cursor.execute(f"""
            SELECT title, date, url, source_name, source_logo, country
            FROM articles
            WHERE {where_clause}
            ORDER BY date DESC;
        """, params)
        articles = cursor.fetchall()
        total_articles = len(articles)

        # All filtered article dates (for trend data)
        cursor.execute(f"""
            SELECT date FROM articles
            WHERE {where_clause};
        """, params)
        all_dates = [row["date"] for row in cursor.fetchall() if row["date"] is not None]

        # Convert dates safely
        date_objs = []
        for date in all_dates:
            try:
                if isinstance(date, str):
                    date_objs.append(datetime.fromisoformat(date))
                elif isinstance(date, datetime):
                    date_objs.append(date)
            except (ValueError, TypeError) as e:
                print(f"Skipping invalid date {date}: {str(e)}")
                continue

        # Helper to get start of the week (Monday)
        def week_start(date):
            start = date - timedelta(days=date.weekday())
            end = start + timedelta(days=6)
            return f"{start.strftime('%b %d')}–{end.strftime('%b %d')}"

        # Handle trend data
        if not date_objs:
            trend_data = {"labels": [], "data": []}
        else:
            week_counts = Counter(week_start(date) for date in date_objs)
            sorted_weeks = sorted(
                week_counts.keys(),
                key=lambda label: datetime.strptime(label.split("–")[0], "%b %d")
            )
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
            "total_articles": total_articles,
            "top_countries": top_countries,
            "filter_applied": {
                "received_sources": sources,
                "actual_filter": filter_sources if sources else None
            }
        })

    except Exception as e:
        print(f"Error in /get_data: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/get_summary", methods=["GET"])
def get_summary():
    conn = None
    cursor = None
    print("✅ Route hit!")  # More visible print
    try:
        # Extract parameters
        and_keywords = request.args.getlist("and")
        or_keywords = request.args.getlist("or")
        not_keywords = request.args.getlist("not")
        sources = request.args.getlist("source")

        # Build WHERE clause more efficiently
        conditions = []
        params = []
        
        # Process keywords
        if and_keywords:
            conditions.append("(" + " AND ".join(["LOWER(title) LIKE %s"] * len(and_keywords)) + ")")
            params.extend([f"%{kw.lower()}%" for kw in and_keywords])
            
        if or_keywords:
            conditions.append("(" + " OR ".join(["LOWER(title) LIKE %s"] * len(or_keywords)) + ")")
            params.extend([f"%{kw.lower()}%" for kw in or_keywords])
            
        if not_keywords:
            conditions.append("(" + " AND ".join(["LOWER(title) NOT LIKE %s"] * len(not_keywords)) + ")")
            params.extend([f"%{kw.lower()}%" for kw in not_keywords])

        # Process sources
        if sources:
            filter_sources = sources[1:] if len(sources) > 1 else sources
            conditions.append(f"source_name IN ({','.join(['%s']*len(filter_sources))})")
            params.extend(filter_sources)

        where_clause = " AND ".join(conditions) if conditions else "TRUE"

        # Get connection with timeout
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Optimized query with timeout
        cursor.execute(f"""
            SELECT title FROM articles 
            WHERE {where_clause}
            ORDER BY date DESC 
            LIMIT 20;
        """, params)
        
        titles = [row["title"] for row in cursor.fetchall()]
        
        if not titles:
            return jsonify({"summary": "No matching articles found", "count": 0}), 200

        # Early return if we have minimal data
        if len(titles) < 3:
            return jsonify({
                "summary": "Insufficient data for full summary",
                "count": len(titles),
                "titles": titles  # Return raw titles for simple display
            }), 200
        
        print('verify the titles found', titles)

        # Process summary with timeout handling
        try:
            summary = summarize_titles(titles[:15])  # Limit to 15 titles max
            print('verify the summary found',summary)

            return jsonify({
                "summary": summary,
                "count": len(titles)
            }), 200
        except Exception as e:
            return jsonify({
                "summary": "Summary generation timed out",
                "count": len(titles),
                "titles": titles[:5]  # Return first few titles
            }), 200

    except Exception as e:
        print(f"Error in get_summary: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

print("Registered routes:")
for rule in app.url_map.iter_rules():
    print(f"- {rule}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
