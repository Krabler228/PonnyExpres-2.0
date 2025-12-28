import logging
import logging.handlers
from pathlib import Path
from .formatters import JSONFormatter


def setup_logging(app=None):
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log", maxBytes=10 * 1024 * 1024, backupCount=7, encoding="utf-8"
    )

    console_handler = logging.StreamHandler()
    json_formatter = JSONFormatter()

    file_handler.setFormatter(json_formatter)
    console_handler.setFormatter(json_formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    print("Logging: logs/app.log (10MB×7 дней)")
