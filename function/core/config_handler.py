import json
import os
from typing import Any, Dict

DEFAULT_FONT_PATH = r"C:\\Windows\\Fonts\\msgothic.ttc"

DEFAULT_CONFIG: Dict[str, Any] = {
    "animation_speed": 1.0,
    "max_display_cards": 50,
    "font_size_base": 16,
    "use_custom_font": False,
    "font_path": "",
    "theme_color": "Blue",
    "theme_style": "Light",
}

class ConfigHandler:
    def __init__(self, path: str = "external_resource/config/config.json"):
        self.path = path
        self.config: Dict[str, Any] = DEFAULT_CONFIG.copy()
        self.load()

    def load(self) -> None:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self.config.update(data)
            except Exception:
                pass
        else:
            self.save()

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def reset(self) -> None:
        self.config = DEFAULT_CONFIG.copy()
        self.save()
