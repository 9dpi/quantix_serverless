import os
import logging
from datetime import datetime

class SheetLogger:
    def __init__(self, sheets_util):
        self.sheets = sheets_util
        self.logger = logging.getLogger("QuantixLogger")
        self.logger.setLevel(logging.INFO)

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        try:
            # Ghi vào sheet 'logs'
            self.sheets.append_row("logs", [timestamp, message])
        except Exception as e:
            print(f"Failed to write log to sheet: {e}")

    def info(self, message):
        self.log(f"INFO: {message}")

    def error(self, message):
        self.log(f"ERROR: {message}")
