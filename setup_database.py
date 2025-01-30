import sqlite3
import json

DB_FILE = "mtg_cards.db"
JSON_FILE = "scryfall_all_cards.json"

def create_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Drop the table if it already exists (for testing purposes)
    cursor.execute("DROP TABLE IF EXISTS cards")

    # Create a new table for storing card data
    cursor.execute('''
        CREATE TABLE cards (
            id TEXT PRIMARY KEY,
            name TEXT,
            mana_cost TEXT,
            type_line TEXT,
            oracle_text TEXT,
            power TEXT,
            toughness TEXT,
            colors TEXT,
            rarity TEXT,
            set_name TEXT,
            image_uri TEXT,
            price_usd REAL
        )
    ''')

    conn.commit()
    conn.close()
    print("Database and table created successfully.")

if __name__ == "__main__":
    create_database()
