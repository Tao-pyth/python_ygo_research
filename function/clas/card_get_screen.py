import threading
import time
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from function.core.db_handler import DBHandler
from function.core.card_img_download import CardImgDownload


class CardInfoScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_handler = DBHandler()
        self.downloader = CardImgDownload(db_handler=self.db_handler)
        self.dialog = None
        self._is_downloading = False

    def on_checkbox_toggle(self, checkbox, value):
        card_input = self.ids.card_name_input
        deck_url_input = self.ids.deck_url_input

        card_input.disabled = value
        card_input.text_color = (1, 0, 0, 1) if value else (0, 0, 0, 1)
        deck_url_input.disabled = not value
        deck_url_input.opacity = 1 if value else 0

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
            deck_mode = self.ids.deck_checkbox.active
            keyword = self.ids.card_name_input.text.strip()
            url = self.ids.deck_url_input.text.strip()

            if deck_mode and url:
                self._process_deck_url(url)
            elif keyword:
                self._process_card_keyword(keyword)
            else:
                self._show_dialog("エラー", "カード名またはデッキURLを入力してください。")
        finally:
            Clock.schedule_once(lambda dt: self._reset_ui())

    def _process_card_keyword(self, keyword):
        urls = self.downloader.get_card_urls_by_keyword(keyword)
        if not urls:
            self._update_status("カードが見つかりませんでした。")
            return

        for i, url in enumerate(urls, 1):
            self._update_status(f"カード {i}/{len(urls)} を取得中...")
            self.downloader.capture_card_image(url)
            card_name = self.downloader.last_saved_card_name
            self._update_last_saved(card_name)
        self._show_dialog("完了", f"{len(urls)} 件のカードを登録しました。")

    def _process_deck_url(self, deck_url):
        max_rounds = 3
        for round_num in range(max_rounds):
            self._update_status(f"{round_num+1} 周目の取得中...")
            urls = self.downloader.get_full_urls_from_input(deck_url)
            if not urls:
                self._update_status("URLが無効かカードが見つかりません。")
                return

            for i, url in enumerate(urls, 1):
                self._update_status(f"{round_num+1}周目: {i}/{len(urls)} を処理中...")
                self.downloader.capture_card_image(url)
                card_name = self.downloader.last_saved_card_name
                self._update_last_saved(card_name)

            if round_num < max_rounds - 1:
                self._update_status("待機中...（10秒）")
                time.sleep(10)

        self._show_dialog("完了", f"最大{max_rounds}回まで処理しました。")

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
