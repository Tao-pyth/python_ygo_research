from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivy.metrics import dp
from function.core.db_handler import DBHandler
from kivy.core.text import DEFAULT_FONT
from kivy.utils import get_color_from_hex

class CardListScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DBHandler()
        self.current_deck_name = None

        self.layout = MDBoxLayout(orientation='vertical', spacing=10, padding=10)

        self.title_label = MDLabel(text="[カード一覧]", halign="center", font_name=DEFAULT_FONT, size_hint_y=0.15)
        self.scroll = MDScrollView()
        self.grid = MDGridLayout(cols=1, spacing=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)

        self.input_row = MDBoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(48))
        self.name_input = MDTextField(hint_text="カード名", font_name=DEFAULT_FONT, size_hint_x=0.5)
        self.count_input = MDTextField(hint_text="枚数", input_filter='int', font_name=DEFAULT_FONT, size_hint_x=0.2)
        self.add_button = MDRaisedButton(text="追加", on_press=self.add_card_to_deck, size_hint_x=0.3, md_bg_color=(0.2, 0.6, 0.2, 1))
        self.input_row.add_widget(self.name_input)
        self.input_row.add_widget(self.count_input)
        self.input_row.add_widget(self.add_button)

        self.back_button = MDRaisedButton(text="戻る", on_press=self.go_back, md_bg_color=(0.7, 0.2, 0.2, 1), size_hint_y=None, height=dp(48))

        self.layout.add_widget(self.title_label)
        self.layout.add_widget(self.scroll)
        self.layout.add_widget(self.input_row)
        self.layout.add_widget(self.back_button)
        self.add_widget(self.layout)

    def load_deck(self, deck_name):
        self.current_deck_name = deck_name
        self.title_label.text = f"デッキ: {deck_name} のカード一覧"
        self.grid.clear_widgets()
        cards = self.db.get_cards_by_deck(deck_name)
        for idx, (card_name, count) in enumerate(cards):
            bg_color = get_color_from_hex("#f5f5f5") if idx % 2 == 0 else get_color_from_hex("#ffffff")

            row = MDBoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=dp(50))
            label = MDLabel(text=f"{card_name} x{count}", halign="left", font_name=DEFAULT_FONT)

            minus_btn = MDIconButton(icon="minus", on_press=lambda x, name=card_name: self.change_card_count(name, -1))
            plus_btn = MDIconButton(icon="plus", on_press=lambda x, name=card_name: self.change_card_count(name, 1))
            delete_btn = MDIconButton(icon="delete", on_press=lambda x, name=card_name: self.delete_card_from_deck(name))

            for btn in (minus_btn, plus_btn, delete_btn):
                btn.theme_text_color = "Custom"
                btn.text_color = (0.2, 0.2, 0.6, 1)
            delete_btn.text_color = (0.5, 0.2, 0.2, 1)

            row.add_widget(label)
            row.add_widget(minus_btn)
            row.add_widget(plus_btn)
            row.add_widget(delete_btn)

            card = MDCard(row, size_hint_y=None, height=dp(50), padding=10, md_bg_color=bg_color)
            card.bind(on_release=lambda instance, name=card_name: self.open_card_detail(name))
            self.grid.add_widget(card)

    def load_all_cards(self):
        self.current_deck_name = None
        self.title_label.text = "全カード一覧"
        self.grid.clear_widgets()
        all_cards = self.db.get_all_card_names()
        for idx, card_name in enumerate(all_cards):
            bg_color = get_color_from_hex("#f5f5f5") if idx % 2 == 0 else get_color_from_hex("#ffffff")
            label = MDLabel(text=card_name, halign="left", font_name=DEFAULT_FONT)
            delete_btn = MDIconButton(icon="delete", disabled=True)
            row = MDBoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=dp(50))
            row.add_widget(label)
            row.add_widget(delete_btn)

            card = MDCard(row, size_hint_y=None, height=dp(50), padding=10, md_bg_color=bg_color)
            card.bind(on_release=lambda instance, name=card_name: self.open_card_detail(name))
            self.grid.add_widget(card)

    def add_card_to_deck(self, instance):
        card_name = self.name_input.text.strip()
        try:
            count = int(self.count_input.text.strip())
        except ValueError:
            return

        if card_name and count > 0 and self.current_deck_name:
            self.db.add_card(self.current_deck_name, card_name, count)
            self.load_deck(self.current_deck_name)
            self.name_input.text = ""
            self.count_input.text = ""

    def delete_card_from_deck(self, card_name):
        if self.current_deck_name:
            self.db.remove_card(self.current_deck_name, card_name)
            self.load_deck(self.current_deck_name)

    def open_card_detail(self, card_name):
        detail_screen = self.manager.get_screen("card_detail")
        detail_screen.load_card(card_name)
        self.manager.current = "card_detail"

    def change_card_count(self, card_name, delta):
        if self.current_deck_name:
            self.db.adjust_card_count(self.current_deck_name, card_name, delta)
            self.load_deck(self.current_deck_name)

    def save_card_scores(self, card_name, field, hand, grave):
        pass  # obsolete

    def go_back(self, instance):
        self.manager.current = "deck"

