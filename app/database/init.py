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

        # 1. Таблица товаров
        await conn.execute("""CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY,
                category_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                price INTEGER NOT NULL,
                image TEXT DEFAULT NULL,
                delivery_type TEXT NOT NULL CHECK (delivery_type IN ('auto', 'manual')), 
                in_stock INTEGER NOT NULL DEFAULT 0 CHECK (in_stock IN (0, 1)),
                FOREIGN KEY (category_id) REFERENCES categories(category_id) 
            )
        """)

        # 2. Таблица заказов
        await conn.execute("""CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,          
                product_id INTEGER NOT NULL,         
                delivery_type TEXT NOT NULL CHECK (delivery_type IN ('auto', 'manual')),
                price INTEGER NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('pending', 'completed')), 
                FOREIGN KEY (user_id) REFERENCES user_info(user_id), 
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        """)

        await conn.execute("""CREATE TABLE IF NOT EXISTS digital_stock (
                id INTEGER PRIMARY KEY,
                product_id INTEGER NOT NULL,        
                order_id INTEGER DEFAULT NULL,    
                content TEXT NOT NULL,
                is_sold INTEGER DEFAULT 0 CHECK (is_sold IN (0, 1)), 
                FOREIGN KEY (product_id) REFERENCES products(product_id), 
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            )
        """)

        await conn.execute("""CREATE TABLE IF NOT EXISTS manual_stock (
                product_id INTEGER NOT NULL,
                stock_quantity INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
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
