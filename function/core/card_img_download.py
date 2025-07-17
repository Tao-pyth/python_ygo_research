import os
import time
import re
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
from bs4 import BeautifulSoup
from function.core.db_handler import DBHandler


class CardImgDownload:
    def __init__(self,
                 db_handler: DBHandler,
                 chromedriver_path=r'external_resource/chromedriver-win32/chromedriver.exe',
                 save_dir='external_resource/image'):

        self.db_handler = db_handler
        self.chromedriver_path = chromedriver_path
        self.save_dir = save_dir
        self.last_saved_card_name = ""

        os.makedirs(self.save_dir, exist_ok=True)

    def extract_card_info(self, driver):
        """
        seleniumのdriverを使用してカード情報（テキスト）を抽出
        """
        card_specs = {'info': None}
        try:
            item_boxes = driver.find_elements(By.CLASS_NAME, "CardText")
            item_box_text = ''.join(
                BeautifulSoup(box.get_attribute('outerHTML'), 'html.parser').get_text(strip=True)
                for box in item_boxes
            )
            item_box_text = item_box_text.split('カードテキスト')[0]
            card_specs['info'] = item_box_text
        except Exception as e:
            print(f"カード情報取得エラー: {e}")
        return card_specs

    def capture_card_image(self, url):
        # cid 抽出と既存確認
        match = re.search(r'cid=(\d+)', url)
        if not match:
            print(f"URL形式不正: {url}")
            return
        cid = "cid" + match.group(1)
        if self.db_handler.cid_exists(cid):
            print(f"{cid} はすでに登録済みです。スキップ。")
            return

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1280,960")
        driver = webdriver.Chrome(service=Service(self.chromedriver_path), options=chrome_options)

        try:
            driver.get(url)
            time.sleep(10)

            ActionChains(driver).move_to_element(driver.find_element(By.ID, "card_frame")).click().perform()
            time.sleep(1)

            name_elem = driver.find_element(By.ID, "cardname")
            soup = BeautifulSoup(name_elem.get_attribute('outerHTML'), 'html.parser')
            for span in soup.find_all('span'):
                span.decompose()
            card_name = soup.get_text(strip=True)

            text_elem = driver.find_element(By.CLASS_NAME, "item_box_text")
            soup = BeautifulSoup(text_elem.get_attribute('outerHTML'), 'html.parser')
            card_text = soup.get_text(strip=True)

            card_specs = self.extract_card_info(driver)

            # スクリーンショット → トリミング
            screenshot_path = os.path.join(self.save_dir, "screenshot.png")
            driver.save_screenshot(screenshot_path)
            img = Image.open(screenshot_path)
            cropped = img.crop((470, 200, 775, 635))
            image_path = os.path.join(self.save_dir, f"{card_name}.png")
            cropped.save(image_path)
            print(f"画像保存: {image_path}")
            self.last_saved_card_name = card_name
            # DB登録
            self.db_handler.upsert_card_info(
                name=card_name,
                cid=cid,
                card_text=card_text,
                info=card_specs.get("info", ""),
                image_path=image_path
            )

        except Exception as e:
            print(f"エラー: {e}")
        finally:
            driver.quit()

    def get_card_urls_by_keyword(self, keyword: str):
        """
        検索結果ページからカードの詳細URLリストを取得
        """
        search_url = (
            "https://www.db.yugioh-card.com/yugiohdb/card_search.action?"
            f"ope=1&sess=1&rp=100&mode=&sort=1&keyword={keyword}"
        )

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        driver = webdriver.Chrome(service=Service(self.chromedriver_path), options=chrome_options)

        try:
            driver.get(search_url)
            time.sleep(3)
            elems = driver.find_elements(By.CLASS_NAME, "card_list")
            hrefs = [elem.get_attribute("href") for elem in elems if elem.get_attribute("href")]
            return [url for url in hrefs if "cid=" in url]
        except Exception as e:
            print(f"検索URL取得エラー: {e}")
            return []
        finally:
            driver.quit()

    def get_full_urls_from_input(self, input_page_url, base_url="https://www.db.yugioh-card.com/"):
        """
        デッキURLからカードの詳細ページURLをすべて取得する
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
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
        指定されたデッキURLからカードページURLをたどり、画像と情報を取得
        """
        for round_num in range(max_rounds):
            print(f"\n【{round_num+1}/{max_rounds} 周回目】")
            urls = self.get_full_urls_from_input(input_page_url)
            skip_flag = True

            for url in urls:
                cid_match = re.search(r'cid=(\d+)', url)
                if cid_match:
                    cid = "cid" + cid_match.group(1)
                    if not self.db_handler.cid_exists(cid):
                        skip_flag = False
                        self.capture_card_image(url)

            if skip_flag:
                print("すべて登録済みのURLです。終了します。")
                break

            input_page_url = random.choice(urls)
            print("1秒待機中...")
            time.sleep(1)
        print("処理完了")
