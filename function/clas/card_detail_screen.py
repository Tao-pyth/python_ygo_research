from kivymd.uix.screen import MDScreen
from kivymd.uix.chip import MDChip
from function.core.db_handler import DBHandler


class CardDetailScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DBHandler()
        self.card_name = ""

    def load_card(self, card_name):
        self.card_name = card_name
        info = self.db.get_full_card_info(card_name) or {}
        self.ids.name_label.text = card_name
        self.ids.field_score.text = str(info.get("field_score", 0))
        self.ids.hand_score.text = str(info.get("hand_score", 0))
        self.ids.grave_score.text = str(info.get("grave_score", 0))
        self.ids.card_text.text = info.get("card_text", "")
        self.ids.card_info.text = info.get("info", "")
        image = info.get("image_path") or ""
        self.ids.card_image.source = image
        self.ids.card_image.reload()
        usage_box = self.ids.deck_usage
        usage_box.clear_widgets()
        for deck, count in self.db.get_deck_usage_for_card(card_name):
            chip = MDChip(label=f"{deck} x{count}")
            usage_box.add_widget(chip)

    def save_scores(self):
        try:
            f = int(self.ids.field_score.text)
            h = int(self.ids.hand_score.text)
            g = int(self.ids.grave_score.text)
            self.db.set_card_scores(self.card_name, field=f, hand=h, grave=g)
        except ValueError:
            pass
        self.manager.current = "card_list"

