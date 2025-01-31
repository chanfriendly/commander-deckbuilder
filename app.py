from flask import Flask, request, jsonify
from flask_cors import CORS  
import sqlite3
import ast
import random
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:8081", "http://localhost:8080"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
DB_FILE = "mtg_cards.db"

# Helper class for deck generation constraints
@dataclass
class DeckConstraints:
    max_price: float
    power_level: Optional[int] = None
    strategy: Optional[str] = None

# Base class for deck enhancement strategies
class DeckEnhancer(ABC):
    @abstractmethod
    def enhance_deck(self, deck: Dict, commander_data: Dict) -> Dict:
        pass

# Current basic enhancement implementation
class BasicEnhancer(DeckEnhancer):
    def enhance_deck(self, deck: Dict, commander_data: Dict) -> Dict:
        deck["analysis"] = {
            "suggestions": [],
            "synergies": [],
            "strategy": "Basic strategy based on commander colors",
            "ai_enhanced": False
        }
        return deck

# Database query helper
def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(query, args)
    rows = cursor.fetchall()
    conn.close()
    return (rows[0] if rows else None) if one else rows

# Function to safely parse stored JSON-like fields
def safe_parse(value):
    try:
        return ast.literal_eval(value) if value else None
    except:
        return value

# Main service class for deck operations
class DeckService:
    def __init__(self, db_file: str, enhancer: DeckEnhancer = None):
        self.db_file = db_file
        self.enhancer = enhancer or BasicEnhancer()
    
    def query_db(self, query, args=(), one=False):
        return query_db(query, args, one)
    
    def get_color_identity(self, commander_colors: str) -> List[str]:
        if not commander_colors:
            return []
        colors = safe_parse(commander_colors)
        return colors if isinstance(colors, list) else []

    def _get_commander_data(self, commander_id: str) -> Dict:
        commander = self.query_db(
            "SELECT id, name, colors, oracle_text FROM cards WHERE id = ?",
            (commander_id,),
            one=True
        )
        if not commander:
            raise ValueError("Commander not found")
        return {
            "id": commander[0],
            "name": commander[1],
            "colors": self.get_color_identity(commander[2]),
            "oracle_text": commander[3]
        }

    def calculate_basic_land_counts(self, color_identity: List[str], utility_lands_count: int) -> Dict[str, int]:
        """
        Calculate the number of basic lands needed for each color based on color identity
        and number of utility lands.
        """
        total_basics_needed = 38 - utility_lands_count  # 38 is target land count
        
        if not color_identity:
            return {'Wastes': total_basics_needed}  # Colorless deck uses Wastes
            
        # Initialize counts
        basic_lands = {
            'W': ('Plains', 0),
            'U': ('Island', 0),
            'B': ('Swamp', 0),
            'R': ('Mountain', 0),
            'G': ('Forest', 0)
        }
        
        # Filter valid colors
        valid_colors = [c for c in color_identity if c in basic_lands]
        if not valid_colors:
            return {}
            
        # Calculate base distribution
        lands_per_color = total_basics_needed // len(valid_colors)
        remainder = total_basics_needed % len(valid_colors)
        
        # Distribute base amounts
        for color in valid_colors:
            count = lands_per_color
            if remainder > 0:
                count += 1
                remainder -= 1
            basic_lands[color] = (basic_lands[color][0], count)
        
        return {name: count for color, (name, count) in basic_lands.items() if count > 0}

    def get_utility_lands(self, color_identity: List[str], max_price: float) -> List[Dict]:
        """Get utility lands appropriate for the deck's colors and budget."""
        color_filter = ""
        if color_identity:
            color_conditions = []
            for color in color_identity:
                color_conditions.append(f"colors LIKE '%{color}%'")
            color_filter = f"AND ({' OR '.join(color_conditions)} OR colors IS NULL OR colors = '')"

        query = f"""
            SELECT id, name, type_line, price_usd 
            FROM cards 
            WHERE type_line LIKE '%Land%'
            AND type_line NOT LIKE '%Basic Land%'
            AND price_usd <= ?
            {color_filter}
            ORDER BY RANDOM()
            LIMIT 18
        """
        
        results = self.query_db(query, (max_price,))
        return [{
            "id": row[0],
            "name": row[1],
            "type": row[2],
            "price": row[3] or 0,
            "category": "lands"
        } for row in results]

    def _get_cards_by_category(self, color_identity: List[str], condition: str, max_price: float, limit: int) -> List[Dict]:
        color_filter = ""
        if color_identity:
            color_conditions = []
            for color in color_identity:
                color_conditions.append(f"colors LIKE '%{color}%'")
            color_filter = f"AND ({' OR '.join(color_conditions)} OR colors IS NULL OR colors = '')"

        query = f"""
            SELECT id, name, type_line, price_usd 
            FROM cards 
            WHERE {condition}
            AND price_usd <= ?
            {color_filter}
            ORDER BY RANDOM()
            LIMIT ?
        """
        
        results = self.query_db(query, (max_price, limit))
        return [{
            "id": row[0],
            "name": row[1],
            "type": row[2],
            "price": row[3] or 0
        } for row in results]

    def _get_category_condition(self, category: str) -> str:
        conditions = {
            'ramp': "type_line LIKE '%Artifact%' OR oracle_text LIKE '%search%library%land%'",
            'card_draw': "oracle_text LIKE '%draw%card%'",
            'removal': "oracle_text LIKE '%destroy%' OR oracle_text LIKE '%exile%'",
            'board_wipes': "oracle_text LIKE '%destroy all%' OR oracle_text LIKE '%exile all%'",
            'interaction': "type_line LIKE '%Instant%' OR type_line LIKE '%Flash%'",
            'synergy': "1=1"  # Will match any card for general synergy slots
        }
        return conditions.get(category, "1=1")

    def generate_deck(self, commander_id: str, constraints: DeckConstraints) -> Dict:
        commander_data = self._get_commander_data(commander_id)
        color_identity = commander_data["colors"]
        
        # Initialize deck
        deck = {
            "commander": commander_data["name"],
            "cards": [],
            "total_price": 0.0
        }
        
        # Get utility lands first
        utility_lands = self.get_utility_lands(color_identity, constraints.max_price)
        deck["cards"].extend(utility_lands)
        
        # Calculate and add basic lands
        basic_lands_needed = self.calculate_basic_land_counts(
            color_identity, 
            len(utility_lands)
        )
        
        for land_name, count in basic_lands_needed.items():
            basic_land = self.query_db(
                "SELECT id, name, type_line, price_usd FROM cards WHERE name = ?",
                (land_name,),
                one=True
            )
            if basic_land:
                deck["cards"].append({
                    "id": basic_land[0],
                    "name": basic_land[1],
                    "type": basic_land[2],
                    "price": basic_land[3] or 0,
                    "category": "lands",
                    "count": count
                })

        # Calculate remaining budget
        current_total = sum(
            (card["price"] or 0) * (card.get("count", 1)) 
            for card in deck["cards"]
        )
        remaining_budget = constraints.max_price - current_total

        # Define categories and their target counts
        categories = {
            'ramp': 10,
            'card_draw': 10,
            'removal': 8,
            'board_wipes': 3,
            'interaction': 7,
            'synergy': 23
        }

        # Fill each category while respecting budget
        for category, target_count in categories.items():
            category_cards = self._get_cards_by_category(
                color_identity,
                self._get_category_condition(category),
                remaining_budget,
                target_count
            )
            
            for card in category_cards:
                if (len(deck["cards"]) < 99 and  # Keep total at 99 (plus commander)
                    (card["price"] or 0) <= remaining_budget):
                    card["category"] = category  # Set the correct category
                    deck["cards"].append(card)
                    remaining_budget -= card["price"] or 0

        # Update total price
        deck["total_price"] = sum(
            (card["price"] or 0) * (card.get("count", 1)) 
            for card in deck["cards"]
        )
        
        return deck


# Initialize services
deck_service = DeckService(DB_FILE)

# Route: Home
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the MTG Card API!"})

# Route: Search cards by name with pagination
@app.route('/search', methods=['GET'])
def search_card():
    card_name = request.args.get('name', '')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    if not card_name:
        return jsonify({"error": "Please provide a card name"}), 400

    query = """
        SELECT id, name, mana_cost, type_line, oracle_text, colors, rarity, set_name, image_uri, price_usd 
        FROM cards 
        WHERE name LIKE ? 
        LIMIT ? OFFSET ?
    """
    results = query_db(query, ('%' + card_name + '%', limit, offset))

    cards = []
    for row in results:
        cards.append({
            "id": row[0],
            "name": row[1],
            "mana_cost": row[2],
            "type_line": row[3],
            "oracle_text": row[4],
            "colors": safe_parse(row[5]),
            "rarity": row[6],
            "set_name": row[7],
            "image_uri": row[8],
            "price_usd": row[9]
        })

    return jsonify({"total_results": len(cards), "cards": cards})

# Route: Get card details by ID
@app.route('/card/<card_id>', methods=['GET'])
def get_card(card_id):
    query = """
        SELECT id, name, mana_cost, type_line, oracle_text, colors, rarity, set_name, image_uri, price_usd 
        FROM cards WHERE id = ?
    """
    card = query_db(query, (card_id,), one=True)

    if not card:
        return jsonify({"error": "Card not found"}), 404

    return jsonify({
        "id": card[0],
        "name": card[1],
        "mana_cost": card[2],
        "type_line": card[3],
        "oracle_text": card[4],
        "colors": safe_parse(card[5]),
        "rarity": card[6],
        "set_name": card[7],
        "image_uri": card[8],
        "price_usd": card[9]
    })

# Route: Get legal Commander cards with optional color filtering
@app.route('/commanders', methods=['GET'])
def get_commanders():
    colors = request.args.get('colors', '').upper()
    name = request.args.get('name', '').strip()
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    # Start building the query
    query = """
        SELECT id, name, mana_cost, type_line, oracle_text, colors, rarity, set_name, image_uri, price_usd 
        FROM cards 
        WHERE (type_line LIKE '%Legendary Creature%' 
        OR (type_line LIKE '%Legendary%' AND oracle_text LIKE '%can be your commander%'))
    """
    
    params = []
    
    # Add name search condition if name is provided
    if name:
        query += " AND name LIKE ?"
        params.append(f'%{name}%')

    # Add color conditions if colors are specified
    if colors:
        color_conditions = []
        for color in colors:
            color_conditions.append("colors LIKE ?")
            params.append(f'%{color}%')
        if color_conditions:
            query += f" AND {' AND '.join(color_conditions)}"

    query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    results = query_db(query, params)
    
    commanders = []
    for row in results:
        commanders.append({
            "id": row[0],
            "name": row[1],
            "mana_cost": row[2],
            "type_line": row[3],
            "oracle_text": row[4],
            "colors": safe_parse(row[5]),
            "rarity": row[6],
            "set_name": row[7],
            "image_uri": row[8],
            "price_usd": row[9]
        })

    return jsonify({"total_results": len(commanders), "commanders": commanders})

# Route: Generate a Commander deck
@app.route('/generate-deck', methods=['GET'])
def generate_deck():
    commander_id = request.args.get('commander_id')
    max_price = float(request.args.get('max_price', 1000000.0))
    power_level = request.args.get('power_level', type=int)
    strategy = request.args.get('strategy')
    
    constraints = DeckConstraints(
        max_price=max_price,
        power_level=power_level,
        strategy=strategy
    )
    
    if not commander_id:
        return jsonify({"error": "Please provide a commander_id"}), 400
    
    try:
        deck = deck_service.generate_deck(commander_id, constraints)
        return jsonify(deck)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start the Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
