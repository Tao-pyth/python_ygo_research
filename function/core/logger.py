from pathlib import Path
import logging
from datetime import datetime

# Determine project root (two levels up from this file)
ROOT_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT_DIR / 'data' / 'log'
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / f"{datetime.now():%Y%m%d}.log"

LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'

# Configure root logger only once
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def get_logger(name: str = __name__) -> logging.Logger:
    """Return a logger configured for this application."""
    return logging.getLogger(name)
