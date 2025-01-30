import requests
import json

# URL to get bulk data info
BULK_DATA_URL = "https://api.scryfall.com/bulk-data"

def fetch_scryfall_data():
    print("Fetching Scryfall bulk data info...")

    # Step 1: Get the bulk data JSON from Scryfall
    response = requests.get(BULK_DATA_URL)
    if response.status_code != 200:
        print("Failed to fetch bulk data info.")
        return

    bulk_data = response.json()
    all_cards_data = next((item for item in bulk_data['data'] if item['type'] == "all_cards"), None)

    if not all_cards_data:
        print("Couldn't find the 'all_cards' dataset.")
        return

    # Step 2: Download the all_cards JSON file
    print("Downloading card data...")
    card_data_response = requests.get(all_cards_data["download_uri"])
    if card_data_response.status_code != 200:
        print("Failed to download card data.")
        return

    # Step 3: Save the JSON file locally
    with open("scryfall_all_cards.json", "w", encoding="utf-8") as file:
        json.dump(card_data_response.json(), file, indent=2)

    print("Scryfall card data saved as 'scryfall_all_cards.json'.")

if __name__ == "__main__":
    fetch_scryfall_data()
