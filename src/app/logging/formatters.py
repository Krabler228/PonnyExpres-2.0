import json
import logging
from datetime import datetime


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
            "session_id": getattr(record, "session_id", None),
        }
        return json.dumps(log)
