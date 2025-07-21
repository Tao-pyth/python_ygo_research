import threading
import time
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.tab import MDTabsBase
from function.core.db_handler import DBHandler
from function.core.card_img_download import CardImgDownload


class CardNameTab(BoxLayout, MDTabsBase):
    pass


class DeckURLTab(BoxLayout, MDTabsBase):
    pass


class CardInfoScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_handler = DBHandler()
        self.downloader = CardImgDownload(db_handler=self.db_handler)
        self.dialog = None
        self._is_downloading = False
        self.mode = "keyword"
        self._tab_map = {}  # タイトル名→インスタンスのマッピング

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        self.mode = "keyword" if tab_text == "カード名を入力" else "deck"
        self._tab_map[self.mode] = instance_tab

    def on_register_checkbox(self, checkbox, value):
        deck_tab = self._tab_map.get("deck")
        if deck_tab:
            deck_tab.ids.deck_name_input.disabled = not value
            deck_tab.ids.deck_name_input.opacity = 1 if value else 0

    def on_retrieve_pressed(self):
        if self._is_downloading:
            return
        self._is_downloading = True
        self.ids.retrieve_button.disabled = True
        self.ids.status_label.text = "処理を開始します..."
        self.ids.last_saved_label.text = ""
        threading.Thread(target=self._start_download_process).start()

    def _start_download_process(self):
        try:
            current_tab = self._tab_map.get(self.mode)
            if not current_tab:
                self._show_dialog("エラー", "タブが正しく認識されていません。")
                return

            if self.mode == "keyword":
                keyword = current_tab.ids.card_name_input.text.strip()
                if keyword:
                    search_url = (
                        "https://www.db.yugioh-card.com/yugiohdb/card_search.action?"
                        f"ope=1&sess=1&rp=10&mode=&sort=1&keyword={keyword}"
                    )
                    self._process_url(search_url)
                else:
                    self._show_dialog("エラー", "カード名が空です。")

            elif self.mode == "deck":
                deck_url = current_tab.ids.deck_url_input.text.strip()
                if deck_url:
                    if current_tab.ids.register_deck_checkbox.active:
                        deck_name = current_tab.ids.deck_name_input.text.strip()
                        if not deck_name:
                            self._show_dialog("エラー", "デッキ名が空です。")
                            return
                        if deck_name in self.db_handler.get_all_decks():
                            self._show_dialog("重複", f"デッキ名『{deck_name}』は既に存在します。別名を指定してください。")
                            return
                        self._card_list = []
                    self._process_url(deck_url)
                    if current_tab.ids.register_deck_checkbox.active:
                        self._register_deck(deck_name)
                else:
                    self._show_dialog("エラー", "デッキURLが空です。")
        finally:
            Clock.schedule_once(lambda dt: self._reset_ui())

    def _process_url(self, url):
        urls = self.downloader.get_card_urls_from_page(url)
        if not urls:
            self._update_status("URLが無効かカードが見つかりません。")
            return
        for i, detail_url in enumerate(urls, 1):
            self._update_status(f"{i}/{len(urls)} を処理中...")
            card_name = self.downloader.capture_card_image(detail_url)
            if card_name:
                self._update_last_saved(card_name)
                if self.mode == "deck" and hasattr(self, "_card_list"):
                    self._card_list.append(card_name)
        self._show_dialog("完了", "カードの取得を完了しました。")

    def _register_deck(self, deck_name):
        self.db_handler.create_deck(deck_name)
        counts = {}
        for card in getattr(self, "_card_list", []):
            counts[card] = counts.get(card, 0) + 1
        for card_name, count in counts.items():
            self.db_handler.add_card(deck_name, card_name, count)
        self._update_status(f"デッキ「{deck_name}」として登録しました。")
        self._card_list.clear()

    def _update_status(self, msg):
        Clock.schedule_once(lambda dt: setattr(self.ids.status_label, "text", msg))

    def _update_last_saved(self, name):
        if name:
            Clock.schedule_once(lambda dt: setattr(self.ids.last_saved_label, "text", f"直近保存: {name}"))

    def _show_dialog(self, title, text):
        def open_dialog(dt):
            self.dialog = MDDialog(title=title, text=text, size_hint=(0.8, 0.4))
            self.dialog.open()
        Clock.schedule_once(open_dialog)

    def _reset_ui(self):
        self._is_downloading = False
        self.ids.retrieve_button.disabled = False
