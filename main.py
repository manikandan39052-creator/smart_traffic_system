from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import configure_logging
if __name__ == '__main__':
    configure_logging(); app=QApplication(sys.argv); window=MainWindow(); window.show(); sys.exit(app.exec())
