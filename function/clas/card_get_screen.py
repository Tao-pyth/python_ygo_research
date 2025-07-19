import threading
import time
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from function.core.db_handler import DBHandler
from function.core.card_img_download import CardImgDownload
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


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
        related = self.ids.related_checkbox.active
        max_rounds = 3 if related else 1

        for round_num in range(max_rounds):
            self._update_status(f"{round_num+1} 周目の取得中...")
            urls = self._get_detail_urls_from_deck(deck_url)
            if not urls:
                self._update_status("URLが無効かカードが見つかりません。")
                return

            for i, url in enumerate(urls, 1):
                self._update_status(f"{round_num+1}周目: {i}/{len(urls)} を処理中...")
                self.downloader.capture_card_image(url)
                card_name = self.downloader.last_saved_card_name
                self._update_last_saved(card_name)

            if related and round_num < max_rounds - 1:
                self._update_status("待機中...（10秒）")
                time.sleep(10)

        self._show_dialog("完了", f"{max_rounds} 回の処理を完了しました。")

    def _get_detail_urls_from_deck(self, deck_url):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        driver = webdriver.Chrome(service=Service(self.downloader.chromedriver_path), options=chrome_options)

        try:
            driver.get(deck_url)
            time.sleep(3)
            inputs = driver.find_elements(By.CLASS_NAME, "link_value")
            rel_urls = [i.get_attribute('value') for i in inputs]
            full_urls = ["https://www.db.yugioh-card.com/" + u.replace('&request_locale=ja', '') for u in rel_urls if 'ope=2' in u]
            return full_urls
        except Exception as e:
            print(f"URL取得エラー: {e}")
            return []
        finally:
            driver.quit()

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
