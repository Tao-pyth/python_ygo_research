from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp
from kivy.core.text import DEFAULT_FONT
from function.core.db_handler import DBHandler
import csv
import os

class DeckManagerScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DBHandler()
        self.dialog = None
        self.current_import_deck = None

        self.layout = MDBoxLayout(orientation="vertical", spacing=10, padding=10)

        # タイトル
        self.top_title = MDLabel(text="[デッキ管理]", halign="center", font_name=DEFAULT_FONT, size_hint_y=0.1)

        # デッキ作成エリア
        self.new_deck_row = MDBoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=dp(48))
        self.new_deck_input = MDTextField(hint_text="新しいデッキ名", font_name=DEFAULT_FONT)
        self.create_deck_button = MDRaisedButton(
            text="デッキを作成",
            on_press=self.create_deck,
            md_bg_color=(0.4, 0.4, 0.6, 1),
            size_hint_x=None,
            width=dp(120)
        )
        self.new_deck_row.add_widget(self.new_deck_input)
        self.new_deck_row.add_widget(self.create_deck_button)

        # デッキリストエリア（スクロールビュー）
        self.scroll_view = MDScrollView(size_hint=(1, 0.6))
        self.deck_buttons_layout = MDBoxLayout(orientation="vertical", spacing=5, size_hint_y=None)
        self.deck_buttons_layout.bind(minimum_height=self.deck_buttons_layout.setter("height"))
        self.scroll_view.add_widget(self.deck_buttons_layout)

        # CSVインポート行
        self.import_row = MDBoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=dp(48))
        self.import_path_input = MDTextField(hint_text="CSVファイルのパスを入力", font_name=DEFAULT_FONT, size_hint_x=0.7)
        self.import_button = MDRaisedButton(
            text="CSVからインポート",
            on_press=self.import_deck_from_csv,
            size_hint_x=0.3,
            md_bg_color=(0.3, 0.6, 0.3, 1)
        )
        self.import_row.add_widget(self.import_path_input)
        self.import_row.add_widget(self.import_button)

        # 下部ボタン（横並び）
        self.bottom_row = MDBoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=dp(48))
        self.back_button = MDRaisedButton(
            text="戻る",
            on_press=self.go_back,
            md_bg_color=(0.7, 0.2, 0.2, 1),
            size_hint_x=0.5
        )
        self.all_cards_button = MDRaisedButton(
            text="全てのカードを見る",
            on_press=self.show_all_cards,
            md_bg_color=(0.2, 0.6, 0.2, 1),
            size_hint_x=0.5
        )
        self.bottom_row.add_widget(self.back_button)
        self.bottom_row.add_widget(self.all_cards_button)

        self.layout.add_widget(self.top_title)
        self.layout.add_widget(self.new_deck_row)
        self.layout.add_widget(self.scroll_view)
        self.layout.add_widget(self.import_row)
        self.layout.add_widget(self.bottom_row)

        self.add_widget(self.layout)
        self.refresh_deck_list()

    def refresh_deck_list(self):
        self.deck_buttons_layout.clear_widgets()
        decks = self.db.get_all_decks()
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
            self.deck_buttons_layout.add_widget(row)

    def create_deck(self, instance):
        name = self.new_deck_input.text.strip()
        if name:
            self.db.add_deck(name)
            self.new_deck_input.text = ""
            self.refresh_deck_list()
            self.show_dialog("デッキを追加しました")

    def delete_deck(self, name):
        self.db.delete_deck(name)
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

        path = self.import_path_input.text.strip()
        if not os.path.isfile(path):
            self.show_dialog("無効なファイルパスです")
            return

        try:
            with open(path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) == 2:
                        name, count = row[0].strip(), int(row[1])
                        self.db.add_card(self.current_import_deck, name, count)
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
