from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from function.core.db_handler import DBHandler
import csv
import os

class DeckManagerScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.current_import_deck = None

    def on_pre_enter(self, *args):
        self.refresh_deck_list()

    def refresh_deck_list(self):
        self.ids.deck_buttons_layout.clear_widgets()
        with DBHandler() as db:
            decks = db.get_all_decks()
        for deck in decks:
            row = MDBoxLayout(orientation="horizontal", spacing=5, size_hint_y=None, height=dp(48))

            display_name = f"★ {deck}" if self.current_import_deck == deck else deck
            deck_button = MDRaisedButton(
                text=display_name,
                on_press=lambda x, name=deck: self.select_deck(name),
                size_hint=(8, None),
                md_bg_color=(0.95, 0.95, 1, 1),
                text_color=(0, 0, 0, 1)
            )

            import_icon = MDIconButton(
                icon="import",
                on_press=lambda x, name=deck: self.set_import_deck(name),
                size_hint=(1, None),
            )
            delete_icon = MDIconButton(
                icon="delete",
                on_press=lambda x, name=deck: self.delete_deck(name),
                size_hint=(1, None),
            )

            row.add_widget(deck_button)
            row.add_widget(import_icon)
            row.add_widget(delete_icon)
            self.ids.deck_buttons_layout.add_widget(row)

    def create_deck(self, instance):
        name = self.ids.new_deck_input.text.strip()
        if name:
            with DBHandler() as db:
                db.add_deck(name)
            self.ids.new_deck_input.text = ""
            self.refresh_deck_list()
            self.show_dialog("デッキを追加しました")

    def delete_deck(self, name):
        with DBHandler() as db:
            db.delete_deck(name)
        if self.current_import_deck == name:
            self.current_import_deck = None
        self.refresh_deck_list()
        self.show_dialog("デッキを削除しました")

    def set_import_deck(self, name):
        self.current_import_deck = name
        self.refresh_deck_list()

    def import_deck_from_csv(self, instance):
        if not self.current_import_deck:
            self.show_dialog("先にインポート先のデッキを選択してください")
            return

        path = self.ids.import_path_input.text.strip()
        if not os.path.isfile(path):
            self.show_dialog("無効なファイルパスです")
            return

        try:
            with open(path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) == 2:
                        name, count = row[0].strip(), int(row[1])
                        with DBHandler() as db:
                            db.add_card(self.current_import_deck, name, count)
            self.show_dialog("CSVからインポートしました")
        except Exception as e:
            self.show_dialog(f"エラー: {e}")

    def select_deck(self, deck_name):
        self.manager.current = "card_list"
        self.manager.get_screen("card_list").load_deck(deck_name)

    def show_all_cards(self, instance):
        self.manager.current = "card_list"
        self.manager.get_screen("card_list").load_all_cards()

    def show_dialog(self, text):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(text=text)
        self.dialog.open()

    def go_back(self, instance):
        self.manager.current = "menu"
