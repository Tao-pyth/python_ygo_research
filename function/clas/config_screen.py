from kivymd.uix.screen import MDScreen
from kivymd.uix.picker import MDThemePicker
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from function.core.config_handler import ConfigHandler, DEFAULT_CONFIG, DEFAULT_FONT_PATH
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
import os
import shutil
import logging
from function.core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

Builder.load_file("resource/theme/gui/ConfigScreen.kv")

class ConfigScreen(MDScreen):
    config_handler: ConfigHandler = ObjectProperty()
    _theme_menu = None
    file_manager: MDFileManager | None = None

    def on_pre_enter(self, *args):
        self.load_values()

    def load_values(self) -> None:
        cfg = self.config_handler.config
        self.ids.animation_speed.text = str(cfg.get("animation_speed", ""))
        self.ids.max_display_cards.text = str(cfg.get("max_display_cards", ""))
        self.ids.font_size_base.text = str(cfg.get("font_size_base", ""))
        self.ids.use_custom_font.active = bool(cfg.get("use_custom_font", False))
        self.ids.font_path_label.text = cfg.get("font_path", "")
        self.toggle_font_inputs(self.ids.use_custom_font.active)
        self.ids.theme_color_label.text = cfg.get("theme_color", "Blue")
        self.ids.theme_style_label.text = cfg.get("theme_style", "Light")

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
        cfg["use_custom_font"] = self.ids.use_custom_font.active
        if self.ids.use_custom_font.active:
            cfg["font_path"] = self.ids.font_path_label.text
        else:
            cfg["font_path"] = ""
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

    def toggle_font_inputs(self, active: bool):
        self.ids.font_upload_btn.disabled = not active

    def open_file_manager(self):
        if not self.file_manager:
            self.file_manager = MDFileManager(select_path=self.select_font,
                                              exit_manager=self.close_file_manager)
        self.file_manager.show(os.getcwd())

    def close_file_manager(self, *args):
        if self.file_manager:
            self.file_manager.close()

    def select_font(self, path: str):
        dest_dir = os.path.join("resource", "theme", "font")
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, os.path.basename(path))
        try:
            shutil.copy(path, dest_path)
            self.ids.font_path_label.text = dest_path
            self.ids.use_custom_font.active = True
        except Exception as e:
            logger.exception(f"Font copy failed: {e}")
            self._show_dialog("エラー", "フォントファイルのコピーに失敗しました。")
        self.close_file_manager()

    def _show_dialog(self, title: str, text: str) -> None:
        Clock.schedule_once(
            lambda dt: MDDialog(title=title, text=text, size_hint=(0.8, 0.4)).open()
        )

    def go_back(self):
        self.manager.current = "menu"
