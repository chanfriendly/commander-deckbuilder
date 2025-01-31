# MTG Commander Deck Builder

A web application that helps users build Magic: The Gathering Commander (EDH) decks based on their chosen commander, budget constraints, power level preferences, and strategic approach.

## Current Implementation

### Backend (Flask)
The backend is built with Flask and SQLite, running in a Docker container. It provides several key functionalities:
- Database management for MTG cards using data from Scryfall's API
- Commander search with color identity filtering
- Deck generation algorithm that considers:
  - Commander color identity
  - Budget constraints
  - Basic land distribution
  - Card categorization (ramp, card draw, removal, etc.)
  - Power level preferences
  - Strategic approach selection

### Frontend (Vue.js)
The frontend is built with Vue.js and features:
- Commander search interface with color filtering
- Deck generation options including:
  - Budget slider with presets
  - Power level selection (1-10) with descriptions
  - Strategy selection dropdown
- Deck display showing:
  - Cards organized by category
  - Card counts and total price
  - Card preview on hover
  - Export functionality

## Project Structure

```
project/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py                 # Main Flask application
│   ├── fetch_scryfall_data.py # Data fetching script
│   └── mtg_cards.db          # SQLite database
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CommanderSelector.vue
│   │   │   ├── DeckOptions.vue
│   │   │   └── DeckDisplay.vue
│   │   └── App.vue
│   └── package.json
```

## Setup and Running

### Backend
1. Build the Docker container:
   ```bash
   docker build -t mtg-commander-builder .
   ```
2. Run the container:
   ```bash
   docker run -p 5000:5000 mtg-commander-builder
   ```

### Frontend
1. Install dependencies:
   ```bash
   npm install
   ```
2. Run the development server:
   ```bash
   npm run serve
   ```
   Access the application at http://localhost:8081

## API Endpoints

- `GET /commanders`: Search for legal commanders with optional color filtering
- `GET /search`: Search for cards by name
- `GET /card/<card_id>`: Get detailed information about a specific card
- `GET /generate-deck`: Generate a commander deck based on provided parameters

## Current Status

The application has a working prototype with core functionality implemented. Users can:
- Search for commanders by name and color identity
- Set deck generation parameters
- View generated decks with cards organized by category

## Known issues:
1. Basic land counting needs improvement
2. Deck generation algorithm could be refined for better synergy
3. Some decks may not reach exactly 100 cards
4. Budget constraints may need fine-tuning

## Future Plans
- Implementation of local AI using Llama for improved deck building suggestions
- Enhanced card synergy detection
- More sophisticated budget management
- Improved land base generation
- Additional deck analysis tools
  
