import psycopg2

def runDB(data: list):
    try:
        conn = psycopg2.connect(
            dbname="echo_db",
            user="vongaimusvaire",
            password="MySushi32",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        print("✅ Database connection established successfully!")

        # Confirm DB and current article count
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]
        print(f"Connected to database: {db_name}")

        cursor.execute("SELECT COUNT(*) FROM articles;")
        count = cursor.fetchone()[0]
        print(f"Number of articles in the table: {count}\n")

        new_article_count = 0
        updated_article_count = 0

        for article in data:
            title = article.get('title', 'unknown')
            url = article.get('url')
            date_value = article.get('date', 'unknown')
            source_name = article.get('source_name', 'unknown')
            source_logo = article.get('source_logo', 'unknown')

            author = article.get('author', 'unknown')
            category = article.get('category', 'unknown')
            body_intro = article.get('body_intro', 'unknown')
            named_entities = article.get('named_entities', [])[:5]
            first_comment = article.get('first_comment', 'unknown')
            ad_slots = article.get('ad_slots', [])[:5]
            country = article.get('country', 'unknown')
            reach = article.get('reach', 0)
            sentiment = article.get('sentiment', 'unknown')

            if not (title and url and date_value and source_name and source_logo):
                print(f"⚠️ Skipping invalid article (missing required fields): {title}")
                continue

            # Check if article already exists
            print(f"🔍 Checking URL: {url}")
            cursor.execute("""
                SELECT title, date, source_name, source_logo 
                FROM articles 
                WHERE url = %s 
                LIMIT 1;
            """, (url,))
            existing = cursor.fetchone()

            if existing:
                existing_title, existing_date, existing_name, existing_logo = existing

                # Optional update if values changed
                if (existing_title != title or existing_date != date_value or
                    not existing_name or not existing_logo):

                    cursor.execute("""
                        UPDATE articles
                        SET title = %s,
                            date = %s,
                            source_name = %s,
                            source_logo = %s
                        WHERE url = %s;
                    """, (title, date_value, source_name, source_logo, url))
                    updated_article_count += 1
                    print(f"🔄 Updated article: {url}")
                else:
                    print(f"⏭ Already exists: {url}")
                continue

            # Insert new article
            cursor.execute("""
                INSERT INTO articles (
                    title, date, url, source_name, source_logo,
                    author, category, body_intro, named_entities,
                    first_comment, ad_slots, country, reach, sentiment
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                );
            """, (
                title, date_value, url, source_name, source_logo,
                author, category, body_intro, named_entities,
                first_comment, ad_slots, country, reach, sentiment
            ))
            new_article_count += 1
            print(f"✅ Inserted new article: {url}")

        conn.commit()
        print(f"\n✅ {new_article_count} new article(s) inserted successfully!")
        print(f"🔄 {updated_article_count} article(s) updated successfully!")

    except psycopg2.Error as e:
        print("❌ in ArticleDB: Failed to connect to or operate on the database")
        print("Error:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("🔌 Connection closed.")
