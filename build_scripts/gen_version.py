"""Git情報からapp_version.pyを生成するスクリプト"""

import subprocess
from datetime import datetime
from pathlib import Path

OUTPUT = Path(__file__).resolve().parent.parent / "app_version.py"


def get_git_desc() -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "describe", "--tags", "--dirty"], stderr=subprocess.STDOUT
            )
            .decode()
            .strip()
        )
    except Exception:
        return ""


def main() -> None:
    desc = get_git_desc()
    base_version = desc.split("-")[0].lstrip("v") if desc else "0.0.1"
    now = datetime.now().isoformat()
    content = f'''"""自動生成されたバージョン情報"""

__version__ = "{base_version}"
_git_version = "{desc}"
_build_time = "{now}"


def get_version_info() -> str:
    if _git_version:
        return f"{base_version} ({desc})"
    return __version__
'''
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"generated {OUTPUT}")


if __name__ == "__main__":
    main()
