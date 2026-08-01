import aiosqlite

DB_PATH = "data.sqlite"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("PRAGMA foreign_keys = ON")
        await conn.execute("""CREATE TABLE IF NOT EXISTS user_info (
                user_id INTEGER PRIMARY KEY,
                is_sub BOOLEAN DEFAULT FALSE,
                balance INTEGER NOT NULL DEFAULT 0,
                registered_at TEXT DEFAULT CURRENT_DATE
            )
        """)

        await conn.execute("""CREATE TABLE IF NOT EXISTS categories (
                category_id INTEGER PRIMARY KEY,
                category_name TEXT,
                parent_id INTEGER DEFAULT NULL,
                image TEXT DEFAULT NULL,
                FOREIGN KEY (parent_id) REFERENCES categories(category_id)
            )
        """)

        await conn.execute("""CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY,
                category_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                price INTEGER NOT NULL,
                image TEXT DEFAULT NULL,
                FOREIGN KEY (category_id) REFERENCES categories(category_id)
            )
        """)

        await conn.execute("""CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL,
                method TEXT,
                status TEXT DEFAULT 'draft',
                external_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) 
        """)

        await conn.commit()
