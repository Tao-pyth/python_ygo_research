import sqlite3
import csv

class DBHandler:
    def __init__(self, db_path='external_resource/db/ygo_data.db'):
        """
        データベース接続を初期化し、必要なテーブルを作成
        """
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.initialize_tables()

    def initialize_tables(self):
        """
        cards_info, decks, deck_cards の各テーブルを初期化
        """
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS cards_info (
            cid TEXT PRIMARY KEY,
            name_ja TEXT,
            name_en TEXT,
            card_text_ja TEXT,
            card_text_en TEXT,
            card_info_ja TEXT,
            card_info_en TEXT,
            image_path TEXT,
            field_score INTEGER DEFAULT 0,
            hand_score INTEGER DEFAULT 0,
            grave_score INTEGER DEFAULT 0
        );
        """)

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

        self.conn.commit()

    def get_cards_by_deck(self, deck_name):
        """
        指定されたデッキに含まれるカード名と枚数を取得
        """
        self.cursor.execute("SELECT card_name, count FROM deck_cards WHERE deck_name = ?", (deck_name,))
        return self.cursor.fetchall()

    def get_all_cards(self):
        """
        すべてのカード名と合計枚数を取得（デッキ横断集計）
        """
        self.cursor.execute("SELECT card_name, SUM(count) FROM deck_cards GROUP BY card_name")
        return self.cursor.fetchall()

    def add_card(self, deck_name, card_name, count):
        """
        デッキにカードを追加（既存なら加算）
        """
        print(f"[DEBUG *]デッキ登録中: {deck_name=} {card_name=} {count=}")
        self.cursor.execute("SELECT count FROM deck_cards WHERE deck_name = ? AND card_name = ?", (deck_name, card_name))
        result = self.cursor.fetchone()
        if result:
            new_count = result[0] + count
            self.cursor.execute("UPDATE deck_cards SET count = ? WHERE deck_name = ? AND card_name = ?", (new_count, deck_name, card_name))
        else:
            self.cursor.execute("INSERT INTO deck_cards (deck_name, card_name, count) VALUES (?, ?, ?)", (deck_name, card_name, count))
        self.conn.commit()

    def remove_card(self, deck_name, card_name):
        """
        デッキからカードを削除
        """
        self.cursor.execute("DELETE FROM deck_cards WHERE deck_name = ? AND card_name = ?", (deck_name, card_name))
        self.conn.commit()

    def get_card_info(self, card_name):
        """
        指定されたカード名に対応するカード情報を取得
        """
        self.cursor.execute("SELECT cid, card_text_ja, card_info_ja FROM cards_info WHERE name_ja = ?", (card_name,))
        result = self.cursor.fetchone()
        if result:
            return {"cid": result[0], "card_text": result[1], "info": result[2]}
        return None

    def get_deck_usage_for_card(self, card_name):
        """
        指定カードがどのデッキで何枚使われているかを取得
        """
        self.cursor.execute("SELECT deck_name, count FROM deck_cards WHERE card_name = ?", (card_name,))
        return self.cursor.fetchall()

    def set_card_scores(self, card_name, field, hand, grave):
        """
        カードのスコア情報を更新（フィールド／手札／墓地）
        """
        self.cursor.execute("""
            UPDATE cards_info
            SET field_score = ?, hand_score = ?, grave_score = ?
            WHERE name_ja = ?
        """, (field, hand, grave, card_name))
        self.conn.commit()

    def get_card_name_by_cid(self, cid):
        self.cursor.execute("SELECT name_ja FROM cards_info WHERE cid = ?", (cid,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_cid_by_card_name(self, card_name):
        self.cursor.execute("SELECT cid FROM cards_info WHERE name_ja = ?", (card_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_all_decks(self):
        """
        登録されているすべてのデッキ名を取得
        """
        self.cursor.execute("SELECT name FROM decks")
        return [row[0] for row in self.cursor.fetchall()]

    def create_deck(self, deck_name):
        """
        デッキを新規作成
        """
        self.cursor.execute("INSERT INTO decks (name) VALUES (?)", (deck_name,))
        self.conn.commit()

    def add_deck(self, deck_name):
        """
        デッキを追加（create_deck のエイリアス）
        """
        self.create_deck(deck_name)

    def delete_deck(self, deck_name):
        """
        デッキと対応するカード構成を削除
        """
        self.cursor.execute("DELETE FROM decks WHERE name = ?", (deck_name,))
        self.cursor.execute("DELETE FROM deck_cards WHERE deck_name = ?", (deck_name,))
        self.conn.commit()

    def import_deck_from_csv(self, deck_name, csv_path):
        """
        指定されたCSVファイルからデッキをインポート
        CSV形式: カード名, 枚数
        """
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) >= 2:
                    card_name, count = row[0], int(row[1])
                    self.add_card(deck_name, card_name, count)

    def upsert_card_info(self, cid, name_ja, name_en, text_ja, text_en, info_ja, info_en, image_path=None):
        """
        多言語カード情報を cards_info テーブルに登録または更新
        """
        self.cursor.execute("""
            INSERT INTO cards_info (
                cid, name_ja, name_en,
                card_text_ja, card_text_en,
                card_info_ja, card_info_en,
                image_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(cid) DO UPDATE SET
                name_ja = excluded.name_ja,
                name_en = excluded.name_en,
                card_text_ja = excluded.card_text_ja,
                card_text_en = excluded.card_text_en,
                card_info_ja = excluded.card_info_ja,
                card_info_en = excluded.card_info_en,
                image_path = excluded.image_path
        """, (cid, name_ja, name_en, text_ja, text_en, info_ja, info_en, image_path))
        self.conn.commit()

    def cid_exists(self, cid):
        """
        cid（カードID）が既に存在しているか確認
        """
        self.cursor.execute("SELECT 1 FROM cards_info WHERE cid = ?", (cid,))
        return self.cursor.fetchone() is not None
