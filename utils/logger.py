import logging
import sys
import os
from config import Config

def setup_logger(name=__name__):
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # File handler – always UTF-8 so special chars never crash
        file_handler = logging.FileHandler(Config.LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console handler – force UTF-8 on Windows (avoids CP1252 UnicodeEncodeError)
        console_stream = open(
            sys.stdout.fileno(),
            mode="w",
            encoding="utf-8",
            errors="replace",   # replace unrenderable chars with '?' instead of crashing
            buffering=1,
            closefd=False,
        )
        console_handler = logging.StreamHandler(console_stream)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
