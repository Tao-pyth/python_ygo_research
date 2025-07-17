import sqlite3

class DBHandler:
    def __init__(self, db_path='external_resource\db\ygo_data.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.initialize_tables()

    def initialize_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS decks (
            name TEXT PRIMARY KEY
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS deck_cards (
            deck_name TEXT,
            card_name TEXT,
            count INTEGER,
            PRIMARY KEY (deck_name, card_name)
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS cards_info (
            name TEXT PRIMARY KEY,
            cid TEXT,
            card_text TEXT,
            info TEXT,
            field_score INTEGER DEFAULT 0,
            hand_score INTEGER DEFAULT 0,
            grave_score INTEGER DEFAULT 0
        );
        """)
        self.conn.commit()

    def get_cards_by_deck(self, deck_name):
        self.cursor.execute("SELECT card_name, count FROM deck_cards WHERE deck_name = ?", (deck_name,))
        return self.cursor.fetchall()

    def get_all_cards(self):
        self.cursor.execute("SELECT card_name, SUM(count) FROM deck_cards GROUP BY card_name")
        return self.cursor.fetchall()

    def add_card(self, deck_name, card_name, count):
        self.cursor.execute("SELECT count FROM deck_cards WHERE deck_name = ? AND card_name = ?", (deck_name, card_name))
        result = self.cursor.fetchone()
        if result:
            new_count = result[0] + count
            self.cursor.execute("UPDATE deck_cards SET count = ? WHERE deck_name = ? AND card_name = ?", (new_count, deck_name, card_name))
        else:
            self.cursor.execute("INSERT INTO deck_cards (deck_name, card_name, count) VALUES (?, ?, ?)", (deck_name, card_name, count))
        self.conn.commit()

    def remove_card(self, deck_name, card_name):
        self.cursor.execute("DELETE FROM deck_cards WHERE deck_name = ? AND card_name = ?", (deck_name, card_name))
        self.conn.commit()

    def get_card_info(self, card_name):
        self.cursor.execute("SELECT cid, card_text, info FROM cards_info WHERE name = ?", (card_name,))
        result = self.cursor.fetchone()
        if result:
            return {"cid": result[0], "card_text": result[1], "info": result[2]}
        return None

    def get_deck_usage_for_card(self, card_name):
        self.cursor.execute("SELECT deck_name, count FROM deck_cards WHERE card_name = ?", (card_name,))
        return self.cursor.fetchall()

    def set_card_scores(self, card_name, field, hand, grave):
        self.cursor.execute("""
            UPDATE cards_info
            SET field_score = ?, hand_score = ?, grave_score = ?
            WHERE name = ?
        """, (field, hand, grave, card_name))
        self.conn.commit()

    def get_all_decks(self):
        self.cursor.execute("SELECT name FROM decks")
        return [row[0] for row in self.cursor.fetchall()]

    def create_deck(self, deck_name):
        self.cursor.execute("INSERT INTO decks (name) VALUES (?)", (deck_name,))
        self.conn.commit()

    def add_deck(self, deck_name):
        self.create_deck(deck_name)

    def delete_deck(self, deck_name):
        self.cursor.execute("DELETE FROM decks WHERE name = ?", (deck_name,))
        self.cursor.execute("DELETE FROM deck_cards WHERE deck_name = ?", (deck_name,))
        self.conn.commit()

    def import_deck_from_csv(self, deck_name, csv_path):
        import csv
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) >= 2:
                    card_name, count = row[0], int(row[1])
                    self.add_card(deck_name, card_name, count)
