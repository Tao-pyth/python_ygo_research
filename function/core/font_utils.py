import os
import logging
from PIL import ImageFont
from function.core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# Candidate default fonts that contain Japanese glyphs
DEFAULT_FONT_CANDIDATES = [
    r"C:\\Windows\\Fonts\\msgothic.ttc",
    "/usr/share/fonts/truetype/mgenplus/mgenplus-1m-regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
]

def find_default_font() -> str:
    """Return the first existing default font path."""
    for path in DEFAULT_FONT_CANDIDATES:
        if os.path.exists(path):
            return path
    return ""

def font_contains_japanese(path: str) -> bool:
    """Check whether the given font file contains basic Japanese characters."""
    try:
        font = ImageFont.truetype(path, 40)
        for ch in "あいうえお":
            if font.getmask(ch).getbbox() is None:
                return False
        return True
    except Exception as e:
        logger.exception(f"font_contains_japanese failed: {e}")
        return False
