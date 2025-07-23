from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from function.core.config_handler import ConfigHandler, DEFAULT_CONFIG
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
import logging
from typing import Optional
from function.core.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

Builder.load_file("resource/theme/gui/ConfigScreen.kv")

PALETTES = [
    "Red",
    "Pink",
    "Purple",
    "DeepPurple",
    "Indigo",
    "Blue",
    "LightBlue",
    "Cyan",
    "Teal",
    "Green",
    "LightGreen",
    "Lime",
    "Yellow",
    "Amber",
    "Orange",
    "DeepOrange",
    "Brown",
    "Gray",
    "BlueGray",
]


class ConfigScreen(MDScreen):
    config_handler: ConfigHandler = ObjectProperty()
    color_menu: Optional[MDDropdownMenu] = None

    def on_pre_enter(self, *args):
        self.load_values()

    def load_values(self) -> None:
        cfg = self.config_handler.config
        self.ids.animation_speed.text = str(cfg.get("animation_speed", ""))
        self.ids.max_display_cards.text = str(cfg.get("max_display_cards", ""))
        self.ids.font_size_base.text = str(cfg.get("font_size_base", ""))
        self.ids.theme_color_label.text = cfg.get("theme_color", "Blue")
        self.ids.theme_style_label.text = cfg.get("theme_style", "Light")

    def open_color_menu(self):
        if not self.color_menu:
            menu_items = [
                {
                    "text": palette,
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=palette: self.set_theme_color(x),
                }
                for palette in PALETTES
            ]
            self.color_menu = MDDropdownMenu(
                caller=self.ids.color_menu_btn,
                items=menu_items,
                width_mult=4,
            )
        self.color_menu.open()

    def set_theme_color(self, palette: str):
        self.ids.theme_color_label.text = palette
        MDApp.get_running_app().theme_cls.primary_palette = palette
        if self.color_menu:
            self.color_menu.dismiss()

    def save_config(self):
        cfg = self.config_handler.config
        cfg["animation_speed"] = float(self.ids.animation_speed.text or 0)
        cfg["max_display_cards"] = int(self.ids.max_display_cards.text or 0)
        cfg["font_size_base"] = float(self.ids.font_size_base.text or 0)
        cfg["theme_color"] = self.ids.theme_color_label.text
        cfg["theme_style"] = self.ids.theme_style_label.text
        self.config_handler.save()

    def reset_config(self):
        self.config_handler.reset()
        self.load_values()
        MDApp.get_running_app().theme_cls.primary_palette = DEFAULT_CONFIG["theme_color"]
        MDApp.get_running_app().theme_cls.theme_style = DEFAULT_CONFIG["theme_style"]

    def toggle_theme_style(self):
        current = self.ids.theme_style_label.text
        new_style = "Dark" if current == "Light" else "Light"
        self.ids.theme_style_label.text = new_style
        MDApp.get_running_app().theme_cls.theme_style = new_style

    def _show_dialog(self, title: str, text: str) -> None:
        Clock.schedule_once(
            lambda dt: MDDialog(title=title, text=text, size_hint=(0.8, 0.4)).open()
        )

    def go_back(self):
        self.manager.current = "menu"
