from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.chip import MDChip
from kivymd.uix.dialog import MDDialog
from function.core.db_handler import DBHandler


class MatchRegisterScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DBHandler()
        self.deck_menu = None
        self.tag_chips = []
        self.dialog = None

    def on_pre_enter(self, *args):
        self._load_decks()
        self._load_tags()

    def _load_decks(self):
        decks = self.db.get_all_decks()
        menu_items = [
            {
                "text": name,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=name: self._set_deck(x),
            }
            for name in decks
        ]
        if self.deck_menu:
            self.deck_menu.dismiss()
        self.deck_menu = MDDropdownMenu(
            caller=self.ids.deck_select_btn, items=menu_items, width_mult=4
        )
        if decks:
            self.ids.deck_field.text = decks[0]

    def _set_deck(self, name):
        self.ids.deck_field.text = name
        if self.deck_menu:
            self.deck_menu.dismiss()

    def open_deck_menu(self):
        if self.deck_menu:
            self.deck_menu.open()

    def _load_tags(self):
        self.ids.tag_box.clear_widgets()
        self.tag_chips = []

        for tag in self.db.get_all_tags():
            chip = MDChip(text=tag)
            chip.state = "normal"
            chip.bind(on_release=self._on_chip_toggle)
            self.ids.tag_box.add_widget(chip)
            self.tag_chips.append(chip)

    def add_new_tag(self):
        tag = self.ids.new_tag_field.text.strip()
        if tag:
            self.db.add_tag(tag)
            chip = MDChip(text=tag)
            chip.state = "normal"
            chip.bind(on_release=self._on_chip_toggle)
            self.ids.tag_box.add_widget(chip)
            self.tag_chips.append(chip)
            self.ids.new_tag_field.text = ""

    def _on_chip_toggle(self, chip):
        if chip.state == "down":
            chip.state = "normal"
            chip.icon = ""
        else:
            chip.state = "down"
            chip.icon = "check"

    def on_win_checkbox(self, instance, value):
        if value:
            self.ids.lose_cb.active = False

    def on_lose_checkbox(self, instance, value):
        if value:
            self.ids.win_cb.active = False

    def register_match(self):
        deck = self.ids.deck_field.text.strip()
        if not deck:
            self._show_dialog("エラー", "デッキを選択してください")
            return
        result = (
            "win" if self.ids.win_cb.active else "lose" if self.ids.lose_cb.active else ""
        )
        if not result:
            self._show_dialog("エラー", "勝敗を選択してください")
            return
        tags = [chip.text for chip in self.tag_chips if chip.state == "down"]
        note = self.ids.note_field.text.strip()
        self.db.add_match_result(deck, tags, result, note)
        self._show_dialog("登録完了", "試合結果を登録しました")
        self.ids.note_field.text = ""
        for chip in self.tag_chips:
            chip.state = "normal"
            chip.icon = ""
        self.ids.win_cb.active = False
        self.ids.lose_cb.active = False

    def _show_dialog(self, title, text):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(title=title, text=text)
        self.dialog.open()
    def go_back(self, instance):
        self.manager.current = "menu"