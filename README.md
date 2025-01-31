# MTG Commander Deck Builder

An API that helps build Magic: The Gathering Commander decks based on your chosen commander, budget constraints, and other parameters.

## Features

- Search for any Magic: The Gathering card
- List all legal commanders with color filtering
- Generate commander decks based on selected commander
- Support for budget and power level constraints
- Pagination support for large queries

## Setup

### Prerequisites

- Python 3.10 or higher
- Docker
- SQLite3

### Installation

1. Clone the repository
2. Install required Python packages:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python setup_database.py
python fetch_scryfall_data.py
```

4. Build and run the Docker container:
```bash
docker build -t mtg-api .
docker run -d -p 5000:5000 --name mtg-api-container mtg-api
```

## API Endpoints

### Search Cards
```
GET /search?name={card_name}&limit={limit}&offset={offset}
```
- `name`: Name of the card to search for (required)
- `limit`: Number of results to return (default: 50)
- `offset`: Number of results to skip (default: 0)

### Get Card Details
```
GET /card/{card_id}
```
- Returns detailed information about a specific card

### List Commanders
```
GET /commanders?colors={colors}&limit={limit}&offset={offset}
```
- `colors`: Filter by color combination (e.g., 'WR' for White-Red)
- `limit`: Number of results to return (default: 50)
- `offset`: Number of results to skip (default: 0)

### Generate Deck
```
GET /generate-deck?commander_id={commander_id}&max_price={max_price}
```
- `commander_id`: ID of the chosen commander (required)
- `max_price`: Maximum total deck price in USD (optional)

## Known Issues

1. Deck Generation
   - Total deck price may exceed specified max_price
   - Decks might not always contain exactly 100 cards
   - Need to improve card selection algorithm for better synergy

2. Commander Color Filtering
   - Current color filtering returns commanders that include specified colors plus additional colors
   - Need to implement exact color combination matching

3. Future Improvements
   - Add support for different play styles (aggro, control, etc.)
   - Implement better synergy detection between commander and deck
   - Add card categorization for better deck building
   - Add support for excluding certain cards or card types
   - Add support for preferred card types or themes

## Project Structure

```
mtg-deck-builder/
├── app.py                  # Main Flask application
├── Dockerfile             # Docker configuration
├── requirements.txt       # Python dependencies
├── setup_database.py      # Database initialization
├── fetch_scryfall_data.py # Data fetching script
└── mtg_cards.db          # SQLite database
```

## Tech Stack

- Backend: Python/Flask
- Database: SQLite
- Containerization: Docker
- Data Source: Scryfall API

## Contributing

Currently a personal project, but suggestions and feedback are welcome!

## License

I don't know enough about licenses yet, but take it and run with it if you can do better.

## Acknowledgments

- Scryfall for their comprehensive MTG card database. THANK YOU for doing the hard work.
- Magic: The Gathering and all card information is copyrighted by Wizards of the Coast
