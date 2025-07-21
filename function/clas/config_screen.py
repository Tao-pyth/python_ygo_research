from kivymd.uix.screen import MDScreen
from kivymd.uix.picker import MDThemePicker
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from function.core.config_handler import ConfigHandler, DEFAULT_CONFIG

Builder.load_file("resource/theme/gui/ConfigScreen.kv")

class ConfigScreen(MDScreen):
    config_handler: ConfigHandler = ObjectProperty()
    _theme_menu = None

    def on_pre_enter(self, *args):
        self.load_values()

    def load_values(self) -> None:
        cfg = self.config_handler.config
        self.ids.animation_speed.text = str(cfg.get("animation_speed", ""))
        self.ids.max_display_cards.text = str(cfg.get("max_display_cards", ""))
        self.ids.font_size_base.text = str(cfg.get("font_size_base", ""))
        self.ids.theme_color_label.text = cfg.get("theme_color", "Blue")

    def open_theme_picker(self):
        picker = MDThemePicker()
        picker.bind(on_select_color=self.on_theme_selected)
        picker.open()

    def on_theme_selected(self, instance, value):
        palette = value.name.capitalize() if hasattr(value, "name") else str(value)
        self.ids.theme_color_label.text = palette
        MDApp.get_running_app().theme_cls.primary_palette = palette

    def save_config(self):
        cfg = self.config_handler.config
        cfg["animation_speed"] = float(self.ids.animation_speed.text or 0)
        cfg["max_display_cards"] = int(self.ids.max_display_cards.text or 0)
        cfg["font_size_base"] = float(self.ids.font_size_base.text or 0)
        cfg["theme_color"] = self.ids.theme_color_label.text
        self.config_handler.save()

    def reset_config(self):
        self.config_handler.reset()
        self.load_values()
        MDApp.get_running_app().theme_cls.primary_palette = DEFAULT_CONFIG["theme_color"]

    def go_back(self):
        self.manager.current = "menu"
