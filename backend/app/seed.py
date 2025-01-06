import os
import asyncio
import asyncpg

# Параметры подключения к базе данных
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASSWORD", "postgres")
DB_NAME = os.getenv("DB_NAME", "messanger_db")


async def seed_data():
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
    )

    try:
        print("Cleaning and seeding database...")
        with open("seed.sql", "r", encoding="utf-8") as f:
            sql_script = f.read()
        await conn.execute(sql_script)
        print("Database seeded successfully.")
    except Exception as e:
        print(f"Error during seeding: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(seed_data())
