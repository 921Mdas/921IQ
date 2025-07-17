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
from helper import clean_name, enrich_with_wikipedia
from collections import defaultdict, Counter
from textblob import TextBlob
from keybert import KeyBERT
import re
from datetime import datetime
from psycopg2.extras import RealDictCursor
import wikipedia
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity



import spacy
from collections import defaultdict
nlp = spacy.load("en_core_web_sm")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
kw_model = KeyBERT()


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

def get_wikipedia_summary(entity_name):
    try:
        page = wikipedia.page(entity_name, auto_suggest=False)
        summary = wikipedia.summary(entity_name, sentences=2, auto_suggest=False)

        # Extract the first image that looks like a person (optional filtering)
        image_url = ""
        for img in page.images:
            if any(ext in img.lower() for ext in [".jpg", ".jpeg", ".png"]) and "logo" not in img.lower():
                image_url = img
                break

        return {
            "summary": summary,
            "url": page.url,
            "image": image_url
        }

    except (wikipedia.DisambiguationError, wikipedia.PageError, wikipedia.HTTPTimeoutError):
        return {
            "summary": "No Wikipedia summary available.",
            "url": "",
            "image": ""
        }

def extract_sentiment(titles):
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    total_score = 0

    for title in titles:
        blob = TextBlob(title)
        polarity = blob.sentiment.polarity
        total_score += polarity

        if polarity > 0.1:
            sentiment_counts["positive"] += 1
        elif polarity < -0.1:
            sentiment_counts["negative"] += 1
        else:
            sentiment_counts["neutral"] += 1

    sentiment_counts["overall_score"] = round(total_score / len(titles), 2) if titles else 0
    return sentiment_counts


# def extract_top_topics(titles, top_n=5):
#     combined_text = ". ".join(titles)
#     keywords = kw_model.extract_keywords(combined_text, top_n=top_n, stop_words='english')
#     return [kw[0] for kw in keywords]

def extract_top_topics(titles, top_n=5, diversity_threshold=0.75):
    # Combine and preprocess titles
    combined_text = ". ".join(set(titles))  # remove duplicates
    if not combined_text.strip():
        return []

    # Extract more candidates than needed to allow filtering
    candidates = kw_model.extract_keywords(
        combined_text,
        keyphrase_ngram_range=(1, 3),
        stop_words='english',
        use_maxsum=True,  # maximize relevance + diversity
        top_n=top_n * 3
    )

    # Deduplicate and reduce similar phrases
    unique_keywords = []
    vectors = []

    for kw, score in candidates:
        vector = kw_model.model.embed([kw])[0]
        if all(cosine_similarity([vector], [v])[0][0] < diversity_threshold for v in vectors):
            unique_keywords.append((kw, score))
            vectors.append(vector)
        if len(unique_keywords) >= top_n:
            break

    return [kw for kw, _ in unique_keywords]


def extract_co_mentions(titles, target_name):
    pattern = re.compile(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b')
    co_mentions = Counter()
    for title in titles:
        candidates = pattern.findall(title)
        filtered = [c for c in candidates if c != target_name and target_name not in c]
        co_mentions.update(filtered)
    return [c for c, _ in co_mentions.most_common(5)]


def extract_quotes(titles, person_name):
    quote_pattern = re.compile(rf'([\w\s]*{re.escape(person_name)}[\w\s]*?said[^.]*\.)', re.IGNORECASE)
    quotes = []
    for title in titles:
        matches = quote_pattern.findall(title)
        quotes.extend(matches)
    return quotes[:5]




@app.route("/get_entities", methods=["GET"])
def get_entities():
    try:
        # Step 1: Extract query parameters
        params = {
            'and_keywords': [kw for kw in request.args.getlist("and") if kw],
            'or_keywords': [kw for kw in request.args.getlist("or") if kw],
            'not_keywords': [kw for kw in request.args.getlist("not") if kw],
            'sources': [s for s in request.args.getlist("source") if s]
        }

        logger.info(f"Entity request params: {params}")

        # Step 2: Build WHERE clause
        where_clause, query_params = build_where_clause(
            params['and_keywords'],
            params['or_keywords'],
            params['not_keywords'],
            params['sources']
        )

        # Step 3: Fetch filtered article titles & dates
        with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f"""
                SELECT title, date, source_name, country
                FROM articles
                WHERE title IS NOT NULL AND {where_clause};
            """, query_params)
            articles = cursor.fetchall()

        if not articles:
            return jsonify({
                "top_people": [],
                "total_entities_found": 0,
                "note": "No articles matched the filters."
            })

        # Step 4: Extract PERSON entities
        entity_data = defaultdict(lambda: {
            "name": "",
            "count": 0,
            "dates": [],
            "sources": set(),
            "countries": set(),
            "articles": set()
        })

        for article in articles:
            title = article["title"]
            doc = nlp(title)

            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    name = ent.text.strip()
                    parts = name.split()
                    if len(parts) < 2:
                        continue  # Skip single names

                    normalized_name = " ".join([w.capitalize() for w in parts])
                    entity = entity_data[normalized_name]
                    entity["name"] = normalized_name
                    entity["count"] += 1
                    entity["dates"].append(article["date"])
                    entity["sources"].add(article["source_name"])
                    entity["countries"].add(article["country"])
                    entity["articles"].add(title)

        # Step 5: Structure and enrich results
        results = []
        for entity in entity_data.values():
            articles = list(entity["articles"])
            trend = process_trend_data(entity["dates"])
            sentiment = extract_sentiment(articles)
            top_topics = extract_top_topics(articles)
            co_mentions = extract_co_mentions(articles, entity["name"])
            quotes = extract_quotes(articles, entity["name"])

            wiki_info = get_wikipedia_summary(entity["name"])

            results.append({
                "name": entity["name"],
                "count": entity["count"],
                "article_count": len(articles),
                "sentiment": sentiment,
                "top_topics": top_topics,
                "trend": trend,
                "co_mentions": co_mentions,
                "top_quotes": quotes,
                "sources": list(entity["sources"]),
                "source_diversity": len(entity["sources"]),
                "country_coverage": list(entity["countries"]),
                "wiki_summary": wiki_info["summary"],
                "wiki_url": wiki_info["url"],
                "wiki_image": wiki_info["image"]
            })

        top_entities = sorted(results, key=lambda x: x["count"], reverse=True)[:50]

        return jsonify({
            "top_people": top_entities,
            "total_entities_found": len(results)
        })

    except Exception as e:
        logger.exception("Error processing get_entities request")
        return jsonify({"error": str(e)}), 500


# @app.route("/get_entities", methods=["GET"])
# def get_entities():
#     try:
#         # Step 1: Extract query parameters
#         params = {
#             'and_keywords': [kw for kw in request.args.getlist("and") if kw],
#             'or_keywords': [kw for kw in request.args.getlist("or") if kw],
#             'not_keywords': [kw for kw in request.args.getlist("not") if kw],
#             'sources': [s for s in request.args.getlist("source") if s]
#         }

#         logger.info(f"Entity request params: {params}")

#         # Step 2: Build WHERE clause
#         where_clause, query_params = build_where_clause(
#             params['and_keywords'],
#             params['or_keywords'],
#             params['not_keywords'],
#             params['sources']
#         )

#         # Step 3: Fetch filtered article titles & dates
#         with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cursor:
#             cursor.execute(f"""
#                 SELECT title, date, source_name, country
#                 FROM articles
#                 WHERE title IS NOT NULL AND {where_clause};
#             """, query_params)
#             articles = cursor.fetchall()

#         if not articles:
#             return jsonify({
#                 "top_people": [],
#                 "total_entities_found": 0,
#                 "note": "No articles matched the filters."
#             })

#         # Step 4: Extract PERSON entities
#         entity_data = defaultdict(lambda: {
#             "name": "",
#             "count": 0,
#             "dates": [],
#             "sources": set(),
#             "countries": set(),
#             "articles": set()
#         })

#         for article in articles:
#             title = article["title"]
#             doc = nlp(title)

#             for ent in doc.ents:
#                 if ent.label_ == "PERSON":
#                     name = ent.text.strip()
#                     parts = name.split()
#                     if len(parts) < 2:
#                         continue  # skip single names

#                     normalized_name = " ".join([w.capitalize() for w in parts])

#                     entity = entity_data[normalized_name]
#                     entity["name"] = normalized_name
#                     entity["count"] += 1
#                     entity["dates"].append(article["date"])
#                     entity["sources"].add(article["source_name"])
#                     entity["countries"].add(article["country"])
#                     entity["articles"].add(title)

#         # Step 5: Structure and enrich results
#         results = []
#         for entity in entity_data.values():
#             articles = list(entity["articles"])
#             trend = process_trend_data(entity["dates"])
#             sentiment = extract_sentiment(articles)
#             top_topics = extract_top_topics(articles)
#             co_mentions = extract_co_mentions(articles, entity["name"])
#             quotes = extract_quotes(articles, entity["name"])

#             results.append({
#                 "name": entity["name"],
#                 "count": entity["count"],
#                 "article_count": len(articles),
#                 "sentiment": sentiment,
#                 "top_topics": top_topics,
#                 "trend": trend,
#                 "co_mentions": co_mentions,
#                 "top_quotes": quotes,
#                 "sources": list(entity["sources"]),
#                 "source_diversity": len(entity["sources"]),
#                 "country_coverage": list(entity["countries"])
#             })

#         top_entities = sorted(results, key=lambda x: x["count"], reverse=True)[:50]

#         return jsonify({
#             "top_people": top_entities,
#             "total_entities_found": len(results)
#         })

#     except Exception as e:
#         logger.error(f"Error in /get_entities: {str(e)}", exc_info=True)
#         return jsonify({
#             "error": "Internal server error",
#             "details": str(e)
#         }), 500


if __name__ == "__main__":
    # Print available routes
    app.run(debug=True)
    print("\nAvailable routes:")
    for rule in app.url_map.iter_rules():
        if "static" not in rule.endpoint:
            print(f"- {rule}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)