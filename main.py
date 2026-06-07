import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from gui.main_window import MainWindow


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("棋类游戏大厅")
    app.setOrganizationName("ChessGameHall")

    window = MainWindow()
    window.show()
    window.raise_()
    window.activateWindow()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
