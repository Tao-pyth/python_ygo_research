from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivy.properties import StringProperty

import logging
import os
from function.core.logging_config import setup_logging
from app_version import get_version_info

# Ensure external_resource directory exists and initialize logging
os.makedirs("external_resource", exist_ok=True)
setup_logging()
logger = logging.getLogger(__name__)

from function.clas.deck_manager import DeckManagerScreen
from function.clas.card_list_screen import CardListScreen
from function.clas.card_get_screen import CardInfoScreen  # ← 追加
from function.clas.card_detail_screen import CardDetailScreen
from function.clas.card_effect_edit_screen import CardEffectEditScreen
from function.clas.config_screen import ConfigScreen
from function.core.config_handler import ConfigHandler

# Load configuration handler
config_handler = ConfigHandler()

# CardInfoScreen, DeckManagerScreen の .kv ファイル読み込み
Builder.load_file("resource/theme/gui/CardInfoScreen.kv")
Builder.load_file("resource/theme/gui/DeckManagerScreen.kv")
Builder.load_file("resource/theme/gui/CardDetailScreen.kv")
Builder.load_file("resource/theme/gui/CardEffectEditScreen.kv")
Builder.load_file("resource/theme/gui/ConfigScreen.kv")
Builder.load_file("resource/theme/gui/CardListScreen.kv")
Builder.load_file("resource/theme/gui/MenuScreen.kv")
Builder.load_file("resource/theme/gui/MatchRegisterScreen.kv")
Builder.load_file("resource/theme/gui/StatsScreen.kv")

class MenuScreen(MDScreen):
    version_text = StringProperty(get_version_info())
    changelog_dialog = None

    def change_screen(self, screen_name):
        self.manager.current = screen_name

    def exit_app(self, instance):
        MDApp.get_running_app().stop()
        Window.close()

    def show_changelog(self):
        try:
            with open(os.path.join("doc", "CHANGELOG.md"), encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            text = f"更新履歴を読み込めませんでした: {e}"
        label = MDLabel(text=text, halign="left", size_hint_y=None)
        label.bind(texture_size=lambda i, s: setattr(i, "height", s[1]))
        scroll = ScrollView()
        scroll.add_widget(label)
        self.changelog_dialog = MDDialog(
            title="更新履歴",
            type="custom",
            content_cls=scroll,
            size_hint=(0.9, 0.9),
        )
        self.changelog_dialog.open()

class MatchRegisterScreen(MDScreen):
    def change_screen(self, screen_name):
        self.manager.current = screen_name

class StatsScreen(MDScreen):
    def change_screen(self, screen_name):
        self.manager.current = screen_name

class DeckAnalyzerApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config_handler = config_handler

    def build(self):
        cfg = self.config_handler.config
        self.theme_cls.primary_palette = cfg.get("theme_color", "Blue")
        self.theme_cls.theme_style = cfg.get("theme_style", "Light")
        sm = MDScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(CardInfoScreen(name="card_info"))  # ← 追加
        sm.add_widget(DeckManagerScreen(name="deck"))
        sm.add_widget(CardListScreen(name="card_list"))
        sm.add_widget(CardDetailScreen(name="card_detail"))
        sm.add_widget(CardEffectEditScreen(name="card_effect_edit"))
        sm.add_widget(MatchRegisterScreen(name="match"))
        sm.add_widget(StatsScreen(name="stats"))
        config_screen = ConfigScreen(name="config")
        config_screen.config_handler = self.config_handler
        sm.add_widget(config_screen)
        return sm

if __name__ == '__main__':
    logger.info('Starting DeckAnalyzerApp')
    DeckAnalyzerApp().run()
