import os
import time
import re
from collections import Counter
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

    def get_card_urls_from_page(self, page_url):
        """
        カード画像URL（img[src*="get_image.action?"]）から cid を抽出し、詳細URLを構築して返す。
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        driver = webdriver.Chrome(service=Service(self.chromedriver_path), options=chrome_options)

        try:
            driver.get(page_url)
            time.sleep(2)
            images = driver.find_elements(By.CSS_SELECTOR, 'img[src*="get_image.action?"]')
            cid_set = set()
            for img in images:
                src = img.get_attribute("src")
                if src:
                    match = re.search(r'cid=(\d+)', src)
                    if match:
                        cid_set.add(match.group(1))

            detail_urls = [f"https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=2&cid={cid}" for cid in cid_set]
            return detail_urls
        except Exception as e:
            print(f"[DEBUG *]URL抽出エラー: {e}")
            return []
        finally:
            driver.quit()

    def get_card_counts_from_page(self, page_url):
        """
        デッキ構成ページから cid をカウントして返す
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        driver = webdriver.Chrome(service=Service(self.chromedriver_path), options=chrome_options)

        try:
            driver.get(page_url)
            time.sleep(3)
            images = driver.find_elements(By.CSS_SELECTOR, 'img[src*="card_search.action?ope=2&cid="]')
            urls = [img.get_attribute("src") for img in images if img.get_attribute("src")]
            cids = []
            for url in urls:
                match = re.search(r'cid=(\d+)', url)
                if match:
                    cid = match.group(1)
                    cids.append(cid)
            return Counter(cids)
        except Exception as e:
            print(f"[DEBUG *]URL取得エラー: {e}")
            return Counter()
        finally:
            driver.quit()

    def _extract_info_text(self, driver, lang):
        """
        カード情報欄から説明テキストを抽出（card_text部分は除去）
        """
        try:
            item_boxes = driver.find_elements(By.CLASS_NAME, "CardText")
            combined_text = ''.join(
                BeautifulSoup(box.get_attribute('outerHTML'), 'html.parser').get_text(strip=True)
                for box in item_boxes
            )
            if lang == "ja":
                return combined_text.split("カードテキスト")[0].strip()
            elif lang == "en":
                return combined_text.split("Card Text")[0].strip()
            return combined_text.strip()
        except Exception as e:
            print(f"[DEBUG *]カード情報取得エラー: {e}")
            return ""

    def capture_card_image(self, base_url):
        """
        カード詳細URLから画像・多言語情報を取得し、DBに保存
        """
        cid_match = re.search(r'cid=(\d+)', base_url)
        if not cid_match:
            print(f"[DEBUG *]URL形式不正: {base_url}")
            return None

        cid = "cid" + cid_match.group(1)
        if self.db_handler.cid_exists(cid):
            print(f"[DEBUG *]{cid} はすでに登録済みです。スキップ。")
            return self.db_handler.get_card_name_by_cid(cid)  # ← card_name を返して登録継続

        data = {}
        for lang in ["ja", "en"]:
            url = base_url + f"&request_locale={lang}"
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--window-size=1280,960")
            driver = webdriver.Chrome(service=Service(self.chromedriver_path), options=chrome_options)
            try:
                driver.get(url)
                time.sleep(2)

                if lang == "ja":
                    ActionChains(driver).move_to_element(driver.find_element(By.ID, "card_frame")).click().perform()
                    time.sleep(1)

                # カード名
                name_elem = driver.find_element(By.ID, "cardname")
                soup = BeautifulSoup(name_elem.get_attribute('outerHTML'), 'html.parser')
                for span in soup.find_all('span'):
                    span.decompose()
                data[f"name_{lang}"] = soup.get_text(strip=True)

                # テキスト欄
                text_elem = driver.find_element(By.CLASS_NAME, "item_box_text")
                soup = BeautifulSoup(text_elem.get_attribute('outerHTML'), 'html.parser')
                raw_text = soup.get_text(strip=True)
                clean_text = raw_text.replace("カードテキスト", "", 1).strip() if lang == "ja" else raw_text.replace("Card Text", "", 1).strip()
                data[f"card_text_{lang}"] = clean_text

                # 情報欄
                data[f"card_info_{lang}"] = self._extract_info_text(driver, lang)

                # 画像保存（日本語のみ）
                if lang == "ja":
                    screenshot_path = os.path.join(self.save_dir, "screenshot.png")
                    driver.save_screenshot(screenshot_path)
                    img = Image.open(screenshot_path)
                    cropped = img.crop((470, 200, 775, 635))
                    image_path = os.path.join(self.save_dir, f"{cid}.png")
                    cropped.save(image_path)
                    print(f"[DEBUG *]画像保存: {image_path}")
                    data["image_path"] = image_path
                    self.last_saved_card_name = data["name_ja"]

            except Exception as e:
                print(f"[DEBUG *]{lang}ページ処理中エラー: {e}")
            finally:
                driver.quit()

        # DB登録（ja/en両方取得後）
        self.db_handler.upsert_card_info(
            cid=cid,
            name_ja=data.get("name_ja", ""),
            name_en=data.get("name_en", ""),
            text_ja=data.get("card_text_ja", ""),
            text_en=data.get("card_text_en", ""),
            info_ja=data.get("card_info_ja", ""),
            info_en=data.get("card_info_en", ""),
            image_path=data.get("image_path", "")
        )

        return self.last_saved_card_name
