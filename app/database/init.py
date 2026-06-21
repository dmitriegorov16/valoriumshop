import aiosqlite

DB_PATH = "data.sqlite"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("""CREATE TABLE IF NOT EXISTS user_info (
                user_id INTEGER PRIMARY KEY,
                is_sub BOOLEAN DEFAULT FALSE
            )
        """)

        await conn.commit()
