from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont, QLinearGradient
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
)


class GameCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self, title, subtitle, icon_text, gradient_start, gradient_end, parent=None):
        super().__init__(parent)
        self.title = title
        self.subtitle = subtitle
        self.icon_text = icon_text
        self.gradient_start = gradient_start
        self.gradient_end = gradient_end
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFixedSize(280, 360)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        icon_label = QLabel(self.icon_text)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("""
            font-size: 80px;
            color: white;
            background: transparent;
        """)
        layout.addWidget(icon_label)

        title_label = QLabel(self.title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: white;
            background: transparent;
        """)
        layout.addWidget(title_label)

        subtitle_label = QLabel(self.subtitle)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setWordWrap(True)
        subtitle_label.setStyleSheet("""
            font-size: 14px;
            color: rgba(255, 255, 255, 0.9);
            background: transparent;
            padding: 0 10px;
        """)
        layout.addWidget(subtitle_label)

        layout.addStretch()

        start_btn = QPushButton("开始游戏 →")
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid white;
                border-radius: 20px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.4);
            }
        """)
        start_btn.clicked.connect(self.clicked.emit)
        layout.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(self.gradient_start))
        gradient.setColorAt(1, QColor(self.gradient_end))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 20, 20)

        painter.setBrush(QBrush(QColor(255, 255, 255, 30)))
        painter.drawEllipse(self.width() - 80, -30, 120, 120)
        painter.drawEllipse(-20, self.height() - 60, 100, 100)


class GameSelector(QWidget):
    game_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(10)

        title_label = QLabel("🎮 游戏大厅")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 42px;
            font-weight: bold;
            color: #2c3e50;
            background: transparent;
        """)
        title_layout.addWidget(title_label)

        subtitle_label = QLabel("选择你想玩的游戏，双人对战，其乐无穷")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            font-size: 16px;
            color: #7f8c8d;
            background: transparent;
        """)
        title_layout.addWidget(subtitle_label)

        main_layout.addLayout(title_layout)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(40)
        cards_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        gomoku_card = GameCard(
            "五子棋",
            "双人对弈，五子连珠\n经典策略棋类游戏",
            "⚫⚪",
            "#667eea",
            "#764ba2",
        )
        gomoku_card.clicked.connect(lambda: self.game_selected.emit(0))
        cards_layout.addWidget(gomoku_card)

        xiangqi_card = GameCard(
            "中国象棋",
            "楚河汉界，将帅对垒\n中华国粹智慧博弈",
            "🏯",
            "#f093fb",
            "#f5576c",
        )
        xiangqi_card.clicked.connect(lambda: self.game_selected.emit(1))
        cards_layout.addWidget(xiangqi_card)

        main_layout.addLayout(cards_layout)
        main_layout.addStretch()

        footer_label = QLabel("Python + PyQt6  |  双人本地对战")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("""
            font-size: 12px;
            color: #95a5a6;
            background: transparent;
        """)
        main_layout.addWidget(footer_label)
