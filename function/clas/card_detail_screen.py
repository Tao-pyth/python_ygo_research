from kivymd.uix.screen import MDScreen
from kivymd.uix.chip import MDChip
from function.core.db_handler import DBHandler
from function.core.effect_dsl_generator import generate_effect_yaml
import os


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

    def open_effect_editor(self):
        """Generate temporary YAML and open the effect edit screen."""
        info = self.db.get_full_card_info(self.card_name)
        if not info:
            return
        cid = info.get("cid")
        text = info.get("card_text", "")
        yaml_dir = os.path.join("external_resource", "effect_yaml")
        os.makedirs(yaml_dir, exist_ok=True)
        path = os.path.join(yaml_dir, f"{cid}.yaml")
        try:
            yaml_text = generate_effect_yaml(cid, self.card_name, text)
            with open(path, "w", encoding="utf-8") as f:
                f.write(yaml_text)
        except Exception:
            pass

        edit_screen = self.manager.get_screen("card_effect_edit")
        edit_screen.load_yaml(cid)
        self.manager.current = "card_effect_edit"

