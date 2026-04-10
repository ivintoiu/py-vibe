# logger.py
# -----------------------------------------------------------------------
# Logging configuration.
# Call setup_logging() once at application startup (done in main.py).
# Every other module obtains its logger with:
#   import logging
#   logger = logging.getLogger(__name__)
# -----------------------------------------------------------------------

import logging
import sys
from logging.handlers import RotatingFileHandler

LOG_FILE = "py-vibe.log"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 5 MB per file, keep 3 rotated backups
_MAX_BYTES = 5 * 1024 * 1024
_BACKUP_COUNT = 3


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure the root logger with a rotating file handler and a console
    handler. Safe to call multiple times — duplicate handlers are not added.
    """
    root = logging.getLogger()
    if root.handlers:
        return  # already configured

    root.setLevel(logging.DEBUG)  # root captures everything; handlers filter

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # File handler — DEBUG and above, rotates at 5 MB
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console handler — INFO and above (or whatever level was passed)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    root.addHandler(file_handler)
    root.addHandler(console_handler)
