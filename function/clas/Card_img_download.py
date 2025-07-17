import os
import time
import json
import re
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
from bs4 import BeautifulSoup

class CardImgDownload:
    def __init__(self,
                 chromedriver_path=r'D:\\_user_template_\\Documents\\PG\\python_game_play_ygo_3\\resource\\chromedriver-win32\\chromedriver.exe',
                 save_dir=r"D:\\_user_template_\\Documents\\PG\\python_game_play_ygo_3\\resource\\image\\card",
                 used_urls_file=r'D:\\_user_template_\\Documents\\PG\\python_game_play_ygo_3\\resource\\image\\used_urls.json',
                 card_info_file=r'D:\\_user_template_\\Documents\\PG\\python_game_play_ygo_3\\resource\\image\\cards_info.json'):

        # 設定項目
        self.chromedriver_path = chromedriver_path
        self.save_dir = save_dir
        self.used_urls_file = used_urls_file or os.path.join(save_dir, 'used_urls.json')
        self.card_info_file = card_info_file or os.path.join(save_dir, 'cards_info.json')

        # ディレクトリ作成
        os.makedirs(self.save_dir, exist_ok=True)

        # 使用済みURLとカード情報の初期化
        self.used_urls = self._load_json(self.used_urls_file)
        self.card_info_json = self._load_json(self.card_info_file)

    def _load_json(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_json(self, filepath, data):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def extract_card_info(self, driver):
        """
        seleniumのdriverを使用してカード情報（テキスト）を抽出
        """
        card_specs = {'info': None}
        item_boxes = driver.find_elements(By.CLASS_NAME, "CardText")
        item_box_text = ''
        for box in item_boxes:
            try:
                html = box.get_attribute('outerHTML')
                soup = BeautifulSoup(html, 'html.parser')
                item_box_text += soup.get_text(strip=True)
            except Exception as e:
                print(f"カード情報取得エラー: {e}")

        item_box_text = item_box_text.split('カードテキスト')[0]
        card_specs['info'] = item_box_text
        return card_specs

    def capture_card_image(self, url):
        if url in self.used_urls:
            print(f"URL {url} はすでに処理済みです。スキップします。")
            return

        # Chromeのオプション設定
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  # 新しいヘッドレスモード
        chrome_options.add_argument("--window-size=1280,960")
        driver = webdriver.Chrome(service=Service(self.chromedriver_path), options=chrome_options)

        try:
            driver.get(url)
            time.sleep(10)

            # カード画像クリックで詳細表示
            driver.find_element(By.ID, "card_frame")
            ActionChains(driver).move_to_element(driver.find_element(By.ID, "card_frame")).click().perform()
            time.sleep(1)

            # カード名取得
            name_elem = driver.find_element(By.ID, "cardname")
            soup = BeautifulSoup(name_elem.get_attribute('outerHTML'), 'html.parser')
            for span in soup.find_all('span'):
                span.decompose()
            card_name = soup.get_text(strip=True)

            # カードテキスト取得
            text_elem = driver.find_element(By.CLASS_NAME, "item_box_text")
            soup = BeautifulSoup(text_elem.get_attribute('outerHTML'), 'html.parser')
            card_text = soup.get_text(strip=True)

            # カード情報取得
            card_specs = self.extract_card_info(driver)

            # スクリーンショットからトリミング
            screenshot_path = os.path.join(self.save_dir, "screenshot.png")
            driver.save_screenshot(screenshot_path)
            img = Image.open(screenshot_path)
            #cropped = img.crop((0, 0, 1280, 960))  # 位置は調整可
            cropped = img.crop((470, 200, 775, 635))  # 位置は調整可
            path = os.path.join(self.save_dir, f"{card_name}.png")
            cropped.save(path)
            print(f"画像保存: {path}")

            # 情報登録
            self.used_urls[url] = f"{card_name}.png"
            self.card_info_json[card_name] = {
                "cid": "cid" + re.search(r'cid=(\d+)', url).group(1),
                "card_text": card_text,
                **card_specs
            }

            # 各カードごとにJSON保存
            self._save_json(self.used_urls_file, self.used_urls)
            self._save_json(self.card_info_file, self.card_info_json)

        except Exception as e:
            print(f"エラー: {e}")
        finally:
            driver.quit()

    def get_full_urls_from_input(self, input_page_url, base_url="https://www.db.yugioh-card.com/"):
        """
        デッキURLからカードの詳細ページURLをすべて取得する
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(service=Service(self.chromedriver_path), options=chrome_options)

        try:
            driver.get(input_page_url)
            time.sleep(3)
            inputs = driver.find_elements(By.CLASS_NAME, "link_value")
            rel_urls = [i.get_attribute('value') for i in inputs]
            full_urls = [base_url + u.replace('&request_locale=ja', '') for u in rel_urls if 'ope=2' in u]
            return full_urls
        except Exception as e:
            print(f"URL取得エラー: {e}")
            return []
        finally:
            driver.quit()

    def process_links(self, input_page_url, max_rounds=50):
        """
        指定回数ループし、カード画像を取得
        """
        for round_num in range(max_rounds):
            print(f"\n【{round_num+1}/{max_rounds} 周回目】")
            urls = self.get_full_urls_from_input(input_page_url)
            skip_flag = True

            for url in urls:
                if url not in self.used_urls:
                    skip_flag = False
                    self.capture_card_image(url)

            if skip_flag:
                print("すべて処理済みのURLです。終了します。")
                break

            input_page_url = random.choice(urls)
            print("10秒待機中...")
            time.sleep(10)
        print("処理完了")

# 実行例
if __name__ == '__main__':
    downloader = CardImgDownload()
    start_url = "https://www.db.yugioh-card.com/yugiohdb/member_deck.action?cgid=34731dd440ead453bf227072bbb05a46&dno=14&request_locale=ja"
    downloader.process_links(start_url, max_rounds=50)
