import sqlite3
from function.core.logger import get_logger

def clean_info_text(text, lang):
    if not text:
        return text
    if lang == "ja" and "カードテキスト" in text:
        return text.split("カードテキスト")[0].strip()
    if lang == "en" and "Card Text" in text:
        return text.split("Card Text")[0].strip()
    return text.strip()

def fix_existing_info_fields(db_path='external_resource/db/ygo_data.db'):
    logger = get_logger(__name__)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT cid, card_info_ja, card_info_en FROM cards_info")
    rows = cursor.fetchall()

    for cid, info_ja, info_en in rows:
        fixed_ja = clean_info_text(info_ja, "ja")
        fixed_en = clean_info_text(info_en, "en")
        cursor.execute("""
            UPDATE cards_info
            SET card_info_ja = ?, card_info_en = ?
            WHERE cid = ?
        """, (fixed_ja, fixed_en, cid))
        logger.info("修正済: %s", cid)

    conn.commit()
    conn.close()
    logger.info("すべての card_info フィールドを修正しました。")

if __name__ == "__main__":
    import kivy
    logger = get_logger(__name__)
    logger.info(kivy.__version__)
    #fix_existing_info_fields()
