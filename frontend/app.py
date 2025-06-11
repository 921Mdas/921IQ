from flask import Flask, render_template, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
from helper import extract_keywords
from collections import Counter
from datetime import datetime
 
app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        dbname="echo",
        user="vongaimusvaire",
        password="MySushi32",
        host="localhost",
        port="5432"
    )

@app.route("/", methods=["GET"])
def home():
    try:
        # Pagination logic
        page = int(request.args.get("page", 1))
        per_page = 12
        offset = (page - 1) * per_page

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Paginated article query
        cursor.execute("""
            SELECT title, date, url, source_name, source_logo
            FROM articles
            ORDER BY date DESC
            OFFSET %s LIMIT %s;
        """, (offset, per_page))
        articles = cursor.fetchall()

        # Get total number of articles
        cursor.execute("SELECT COUNT(*) FROM articles;")
        total_articles = cursor.fetchone()["count"]
        total_pages = (total_articles + per_page - 1) // per_page  # ceiling division

        # Dummy dashboard data
        share_of_voice = {
            "labels": ["Brand A", "Brand B", "Brand C"],
            "data": [35, 45, 20]
        }
        
        #trend data and logic
        cursor.execute("SELECT date FROM articles;")
        all_dates = [row["date"] for row in cursor.fetchall()]
        month_counts = Counter(date.strftime("%b %Y") for date in all_dates)

        # Sort months chronologically
        sorted_months = sorted(
            month_counts.keys(),
            key=lambda m: datetime.strptime(m, "%b %Y")
        )

        trend_data = {
            "labels": sorted_months,
            "data": [month_counts[month] for month in sorted_months]
        }


        
        # Fetch all titles for keyword extraction
        cursor.execute("SELECT title FROM articles;")
        all_titles = [row["title"] for row in cursor.fetchall()]
        wordcloud_data = extract_keywords(all_titles)


        return render_template(
            "index.html",
            articles=articles,
            share_of_voice=share_of_voice,
            trend_data=trend_data,
            wordcloud_data=wordcloud_data,
            current_page=page,
            total_pages=total_pages
        )

    except Exception as e:
        return f"<h1>Error: {e}</h1>"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@app.route("/api/search", methods=["GET"])
def search_articles():
    and_keywords = request.args.getlist("and")
    or_keywords = request.args.getlist("or")
    not_keywords = request.args.getlist("not")

    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        conditions = []
        params = []

        # AND: title must contain all these
        for kw in and_keywords:
            conditions.append("LOWER(title) LIKE %s")
            params.append(f"%{kw.lower()}%")

        # OR: title must contain at least one of these
        if or_keywords:
            or_clause = " OR ".join(["LOWER(title) LIKE %s" for _ in or_keywords])
            conditions.append(f"({or_clause})")
            params.extend([f"%{kw.lower()}%" for kw in or_keywords])

        # NOT: title must NOT contain these
        for kw in not_keywords:
            conditions.append("LOWER(title) NOT LIKE %s")
            params.append(f"%{kw.lower()}%")

        where_clause = " AND ".join(conditions) if conditions else "TRUE"

        cursor.execute(f"""
            SELECT title, date, url, source_name, source_logo
            FROM articles
            WHERE {where_clause}
            ORDER BY date DESC
            LIMIT 20;
        """, params)

        articles = cursor.fetchall()
        return jsonify({"articles": articles})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    app.run(debug=True)