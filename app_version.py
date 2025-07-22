"""アプリのバージョン情報を管理するモジュール"""

import subprocess

__version__ = "0.0.1"


def get_version_info() -> str:
    """git情報を含む詳細バージョンを返す"""
    try:
        desc = (
            subprocess.check_output(
                ["git", "describe", "--tags", "--dirty"],
                stderr=subprocess.STDOUT,
            )
            .decode()
            .strip()
        )
        if desc:
            return f"{__version__} ({desc})"
    except Exception:
        pass
    return __version__
