import sqlite3
import json

DB_FILE = "mtg_cards.db"
JSON_FILE = "scryfall_all_cards.json"

def load_data_into_db():
    # Connect to SQLite database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Load JSON data
    with open(JSON_FILE, "r", encoding="utf-8") as file:
        cards = json.load(file)

    # Insert each card into the database
    for card in cards:
        cursor.execute('''
            INSERT INTO cards (id, name, mana_cost, type_line, oracle_text, power, toughness, colors, rarity, set_name, image_uri, price_usd)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            card.get("id"),
            card.get("name"),
            card.get("mana_cost"),
            card.get("type_line"),
            card.get("oracle_text"),
            card.get("power"),
            card.get("toughness"),
            ",".join(card.get("colors", [])),
            card.get("rarity"),
            card.get("set_name"),
            card.get("image_uris", {}).get("normal"),
            card.get("prices", {}).get("usd")
        ))

    conn.commit()
    conn.close()
    print("Card data loaded successfully.")

if __name__ == "__main__":
    load_data_into_db()
