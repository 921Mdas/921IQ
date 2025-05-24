from flask import Flask, render_template, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor

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

        trend_data = {
            "labels": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "data": [5, 12, 8, 20, 15]
        }

        wordcloud_data = [
            {"text": "AI", "size": 40},
            {"text": "Innovation", "size": 35},
            {"text": "Machine Learning", "size": 30},
            {"text": "Automation", "size": 28},
            {"text": "Data", "size": 27},
            {"text": "Growth", "size": 26},
            {"text": "Tech", "size": 25},
            {"text": "Cloud", "size": 24},
            {"text": "Scalability", "size": 22},
            {"text": "Efficiency", "size": 21},
            {"text": "Productivity", "size": 20},
            {"text": "Digital", "size": 19},
            {"text": "SaaS", "size": 18},
            {"text": "Transformation", "size": 17},
            {"text": "Analytics", "size": 16},
            {"text": "Agility", "size": 15},
            {"text": "Security", "size": 14},
            {"text": "DevOps", "size": 13},
            {"text": "Ecosystem", "size": 12},
            {"text": "Integration", "size": 11}
        ]

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

if __name__ == "__main__":
    app.run(debug=True)