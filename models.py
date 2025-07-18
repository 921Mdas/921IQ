def create_users_table(cur, conn):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            full_name TEXT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            provider TEXT DEFAULT 'local',
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
