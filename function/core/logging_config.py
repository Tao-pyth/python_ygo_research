import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(log_dir=os.path.join('data', 'log'), log_file='app.log'):
    """Configure root logger to log to a file under ``data/log``.

    Parameters
    ----------
    log_dir : str
        Directory where log files are stored.
    log_file : str
        Name of the log file.
    """
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    logger = logging.getLogger()
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    file_handler = RotatingFileHandler(
        log_path, maxBytes=1024*1024, backupCount=3, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger
