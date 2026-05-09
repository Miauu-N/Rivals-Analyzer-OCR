import sqlite3
from sqlalchemy import text
from app.core.database import engine

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE performances ADD COLUMN player_name VARCHAR;"))
        conn.execute(text("ALTER TABLE performances ADD COLUMN is_main_user BOOLEAN DEFAULT FALSE;"))
        conn.commit()
        print("Success")
    except Exception as e:
        print("Error:", e)
