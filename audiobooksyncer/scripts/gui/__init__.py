import sys

from loguru import logger
from PyQt6.QtWidgets import (
    QApplication,
)

from .app import App

logger.remove()
logger.add(
    sys.stdout,
    format='<green>{time:HH:mm:ss}</green> | <cyan>{function}</cyan> | <level>{message}</level>',
)


def main():
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
