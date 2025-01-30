import sqlite3

DB_FILE = "mtg_cards.db"

def search_card(card_name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cards WHERE name LIKE ?", ('%' + card_name + '%',))
    results = cursor.fetchall()

    conn.close()
    return results

if __name__ == "__main__":
    card_name = input("Enter a card name to search: ")
    results = search_card(card_name)

    if results:
        for card in results:
            print(card)
    else:
        print("No cards found.")
