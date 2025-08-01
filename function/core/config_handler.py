import json
import os
import shutil
import logging
from typing import Any, Dict
from function.core.logging_config import setup_logging


setup_logging()
logger = logging.getLogger(__name__)


DEFAULT_CONFIG: Dict[str, Any] = {
    "animation_speed": 1.0,
    "max_display_cards": 50,
    "font_size_base": 16,
    "theme_color": "Blue",
    "theme_style": "Light",
    "accent_color": "Amber",
}

DEFAULT_CONFIG_PATH = os.path.join("resource", "json", "config.json")


class ConfigHandler:
    def __init__(self, path: str = "external_resource/config/config.json"):
        self.path = path
        self.config: Dict[str, Any] = DEFAULT_CONFIG.copy()
        self._ensure_config()
        self.load()

    def _ensure_config(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            if os.path.exists(DEFAULT_CONFIG_PATH):
                shutil.copy(DEFAULT_CONFIG_PATH, self.path)
            else:
                self.save()

    def load(self) -> None:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self.config.update(data)
            except Exception as e:
                logger.exception(f"Failed to load config: {e}")
        else:
            self.save()

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.exception(f"Failed to save config: {e}")

    def reset(self) -> None:
        self.config = DEFAULT_CONFIG.copy()
        self.save()
