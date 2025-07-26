from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivy.metrics import dp
from function.core.db_handler import DBHandler
from kivymd.app import MDApp
from kivy.utils import get_color_from_hex
import os

class CardListScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DBHandler()
        self.current_deck_name = None
        self.yaml_dir = os.path.join("external_resource", "effect_yaml")

    def _create_status_label(self, card_name):
        """Return an MDLabel showing DSL status for the card."""
        cid = self.db.get_cid_by_card_name(card_name)
        text = ""
        if cid:
            path = os.path.join(self.yaml_dir, f"{cid}.yaml")
            if os.path.exists(path):
                text = "済"
        else:
            text = "未"
        label = MDLabel(text=text, halign="center", size_hint_x=None, width=dp(20))
        return label

    def load_deck(self, deck_name):
        self.current_deck_name = deck_name
        self.ids.app_bar.title = f"デッキ: {deck_name} のカード一覧"
        self.ids.grid.clear_widgets()
        cards = self.db.get_cards_by_deck(deck_name)
        for idx, (card_name, count) in enumerate(cards):
            bg_color = get_color_from_hex("#f5f5f5") if idx % 2 == 0 else get_color_from_hex("#ffffff")

            row = MDBoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=dp(50))
            label = MDLabel(text=f"{card_name} x{count}", halign="left")
            status_lbl = self._create_status_label(card_name)

            minus_btn = MDIconButton(icon="minus", on_press=lambda x, name=card_name: self.change_card_count(name, -1))
            plus_btn = MDIconButton(icon="plus", on_press=lambda x, name=card_name: self.change_card_count(name, 1))
            delete_btn = MDIconButton(icon="delete", on_press=lambda x, name=card_name: self.delete_card_from_deck(name))

            for btn in (minus_btn, plus_btn, delete_btn):
                btn.theme_text_color = "Custom"
                btn.text_color = (0.2, 0.2, 0.6, 1)
            delete_btn.text_color = (0.5, 0.2, 0.2, 1)

            row.add_widget(label)
            row.add_widget(status_lbl)
            row.add_widget(minus_btn)
            row.add_widget(plus_btn)
            row.add_widget(delete_btn)

            card = MDCard(row, size_hint_y=None, height=dp(50), padding=10, md_bg_color=bg_color)
            card.bind(on_release=lambda instance, name=card_name: self.open_card_detail(name))
            self.ids.grid.add_widget(card)

    def load_all_cards(self):
        self.current_deck_name = None
        self.ids.app_bar.title = "全カード一覧"
        self.ids.grid.clear_widgets()
        all_cards = self.db.get_all_card_names()
        for idx, card_name in enumerate(all_cards):
            bg_color = get_color_from_hex("#f5f5f5") if idx % 2 == 0 else get_color_from_hex("#ffffff")
            label = MDLabel(text=card_name, halign="left")
            status_lbl = self._create_status_label(card_name)
            delete_btn = MDIconButton(icon="delete", disabled=True)
            row = MDBoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=dp(50))
            row.add_widget(label)
            row.add_widget(status_lbl)
            row.add_widget(delete_btn)

            card = MDCard(row, size_hint_y=None, height=dp(50), padding=10, md_bg_color=bg_color)
            card.bind(on_release=lambda instance, name=card_name: self.open_card_detail(name))
            self.ids.grid.add_widget(card)

    def add_card_to_deck(self, instance):
        card_name = self.ids.name_input.text.strip()
        try:
            count = int(self.ids.count_input.text.strip())
        except ValueError:
            return

        if card_name and count > 0 and self.current_deck_name:
            self.db.add_card(self.current_deck_name, card_name, count)
            self.load_deck(self.current_deck_name)
            self.ids.name_input.text = ""
            self.ids.count_input.text = ""

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

