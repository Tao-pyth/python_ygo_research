from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.core.window import Window
from kivy.lang import Builder

import logging
from function.core.logging_config import setup_logging

# Initialize logging to output under data/log
setup_logging()
logger = logging.getLogger(__name__)

from function.clas.deck_manager import DeckManagerScreen
from function.clas.card_list_screen import CardListScreen
from function.clas.card_get_screen import CardInfoScreen  # ← 追加
from function.clas.card_detail_screen import CardDetailScreen
from function.clas.card_effect_edit_screen import CardEffectEditScreen
from function.clas.config_screen import ConfigScreen
from function.core.config_handler import ConfigHandler

# 日本語フォント設定
LabelBase.register(DEFAULT_FONT, r'resource\\theme\\font\\mgenplus-1c-regular.ttf')

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
    def change_screen(self, screen_name):
        self.manager.current = screen_name

    def exit_app(self, instance):
        MDApp.get_running_app().stop()
        Window.close()

class MatchRegisterScreen(MDScreen):
    def change_screen(self, screen_name):
        self.manager.current = screen_name

class StatsScreen(MDScreen):
    def change_screen(self, screen_name):
        self.manager.current = screen_name

class DeckAnalyzerApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config_handler = ConfigHandler()

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
