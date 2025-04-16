from bot.database.database_operations import execute_query

from bot.database.database_operations import execute_query

async def create_tables():
    queries = [
        # Таблиця Account
        """
        CREATE TABLE IF NOT EXISTS account (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cookie TEXT NOT NULL,
            rate_limit INTEGER,
            proxy_url TEXT,
            user_agent TEXT,
            user_id INTEGER NOT NULL,
            text_spam TEXT,
            count_spam INTEGER,
            category_link TEXT,
            name TEXT,
            geolocation_id INTEGER,
            radius INTEGER,
            time_filter_spam_id INTEGER DEFAULT 0,
            is_blocked BOOLEAN DEFAULT FALSE,
            is_ready BOOLEAN DEFAULT FALSE
        );
        """,

        # Таблиця User
        """
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY,
            time_created DATETIME,
            is_admin BOOLEAN DEFAULT FALSE
        );
        """,

        # Таблиця Payment
        """
        CREATE TABLE IF NOT EXISTS payment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time_created DATETIME,
            deadline DATETIME,
            is_active BOOLEAN,
            user_id INTEGER NOT NULL,
            invoice_id INTEGER,
            is_paid BOOLEAN DEFAULT FALSE,
            is_expired BOOLEAN DEFAULT FALSE
        );
        """,

        # Таблиця Product
        """
        CREATE TABLE IF NOT EXISTS product (
            id INTEGER PRIMARY KEY
        );
        """
    ]

    for query in queries:
        await execute_query(query)
