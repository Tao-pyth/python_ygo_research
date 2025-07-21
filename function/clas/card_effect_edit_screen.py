from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
import os

class CardEffectEditScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cid = None
        self.dialog = None

    def load_yaml(self, cid: str):
        """Load YAML file for the given card id and display it."""
        self.cid = cid
        path = os.path.join("external_resource", "effect_yaml", f"{cid}.yaml")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()
        except FileNotFoundError:
            data = ""
        self.ids.yaml_field.text = data
        self.ids.file_path_input.text = path

    def reload_yaml(self):
        if self.cid:
            self.load_yaml(self.cid)

    def save_yaml(self):
        if not self.cid:
            return
        path = os.path.join("external_resource", "effect_yaml", f"{self.cid}.yaml")
        text = self.ids.yaml_field.text
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        self._show_dialog("保存", "YAMLを保存しました")

    def import_yaml(self):
        path = self.ids.file_path_input.text.strip()
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            self.ids.yaml_field.text = text
        except Exception as e:
            self._show_dialog("エラー", str(e))

    def export_yaml(self):
        path = self.ids.file_path_input.text.strip()
        if not path:
            return
        text = self.ids.yaml_field.text
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            self._show_dialog("エクスポート", "YAMLを書き出しました")
        except Exception as e:
            self._show_dialog("エラー", str(e))

    def _show_dialog(self, title: str, text: str):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(title=title, text=text)
        self.dialog.open()
