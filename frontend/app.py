from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from helper import extract_keywords
from collections import Counter
from datetime import datetime, timedelta


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

#         # All filtered article dates (for trend data)
#         cursor.execute(f"""
#             SELECT date FROM articles
#             WHERE {where_clause};
#         """, params)
#         all_dates = [row["date"] for row in cursor.fetchall()]
#         month_counts = Counter(
#     datetime.fromisoformat(date).strftime("%b %Y") for date in all_dates
# )


#         sorted_months = sorted(
#             month_counts.keys(),
#             key=lambda m: datetime.strptime(m, "%b %Y")
#         )

#         trend_data = {
#             "labels": sorted_months,
#             "data": [month_counts[month] for month in sorted_months]
#         }

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

        
        return render_template(
            "index.html",
            articles=articles,
            top_publications=top_publications,
            trend_data=trend_data,
            wordcloud_data=wordcloud_data,
            current_page=page,
            total_pages=total_pages,
            total_articles=total_articles,
            top_countries = top_countries
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