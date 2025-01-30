from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_FILE = "mtg_cards.db"

# Connect to the database
def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(query, args)
    rows = cursor.fetchall()
    conn.close()
    
    return (rows[0] if rows else None) if one else rows

# Route: Home
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the MTG Card API!"})

# Route: Search cards by name
@app.route('/search', methods=['GET'])
def search_card():
    card_name = request.args.get('name', '')

    if not card_name:
        return jsonify({"error": "Please provide a card name"}), 400

    query = "SELECT id, name, mana_cost, type_line, oracle_text, colors, rarity, set_name, image_uri, price_usd FROM cards WHERE name LIKE ?"
    results = query_db(query, ('%' + card_name + '%',))

    cards = []
    for row in results:
        cards.append({
            "id": row[0],
            "name": row[1],
            "mana_cost": row[2],
            "type_line": row[3],
            "oracle_text": row[4],
            "colors": row[5],
            "rarity": row[6],
            "set_name": row[7],
            "image_uri": row[8],
            "price_usd": row[9]
        })

    return jsonify(cards)

# Route: Get card details by ID
@app.route('/card/<card_id>', methods=['GET'])
def get_card(card_id):
    query = "SELECT id, name, mana_cost, type_line, oracle_text, colors, rarity, set_name, image_uri, price_usd FROM cards WHERE id = ?"
    card = query_db(query, (card_id,), one=True)

    if not card:
        return jsonify({"error": "Card not found"}), 404

    return jsonify({
        "id": card[0],
        "name": card[1],
        "mana_cost": card[2],
        "type_line": card[3],
        "oracle_text": card[4],
        "colors": card[5],
        "rarity": card[6],
        "set_name": card[7],
        "image_uri": card[8],
        "price_usd": card[9]
    })

# Start the Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)