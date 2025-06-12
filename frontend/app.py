from flask import Flask, render_template, request, jsonify
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
    conn = None
    cursor = None
    try:
        # Extract query params
        and_keywords = request.args.getlist("and")
        or_keywords = request.args.getlist("or")
        not_keywords = request.args.getlist("not")

        # Pagination
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
        cursor.execute(f"""
            SELECT title, date, url, source_name, source_logo
            FROM articles
            WHERE {where_clause}
            ORDER BY date DESC
            OFFSET %s LIMIT %s;
        """, params + [offset, per_page])
        articles = cursor.fetchall()

        # All filtered article dates (for trend data)
        cursor.execute(f"""
            SELECT date FROM articles
            WHERE {where_clause};
        """, params)
        all_dates = [row["date"] for row in cursor.fetchall()]
        month_counts = Counter(date.strftime("%b %Y") for date in all_dates)

        sorted_months = sorted(
            month_counts.keys(),
            key=lambda m: datetime.strptime(m, "%b %Y")
        )

        trend_data = {
            "labels": sorted_months,
            "data": [month_counts[month] for month in sorted_months]
        }

        # All filtered titles (for wordcloud)
        cursor.execute(f"""
            SELECT title FROM articles
            WHERE {where_clause};
        """, params)
        all_titles = [row["title"] for row in cursor.fetchall()]
        wordcloud_data = extract_keywords(all_titles)

        # Dummy share of voice (replace with real logic if needed)
        share_of_voice = {
            "labels": ["Brand A", "Brand B", "Brand C"],
            "data": [35, 45, 20]
        }

        return render_template(
            "index.html",
            articles=articles,
            share_of_voice=share_of_voice,
            trend_data=trend_data,
            wordcloud_data=wordcloud_data,
            current_page=page,
            total_pages=total_pages,
            total_articles=total_articles  # 👈 Add this
        )

    except Exception as e:
        return f"<h1>Error: {e}</h1>"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    app.run(debug=True)