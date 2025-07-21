# coding: utf-8
"""target パターン定義ファイル

Yu-Gi-Oh! のテキスト中のターゲット表現を簡易的にDSLへ変換するための
パターンを保持する。
"""

TARGET_PATTERNS = {
    r"1 monster from your GY": "player.graveyard.monster.choice(1)",
    r"1 Spell from your hand": "player.hand.spell.choice(1)",
}

__all__ = ["TARGET_PATTERNS"]
