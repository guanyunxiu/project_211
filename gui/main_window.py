from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QIcon
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
    QFrame,
)

from game.gomoku import GomokuGame, Player


class BoardWidget(QWidget):
    MARGIN = 40
    CELL_SIZE = 40
    PIECE_RADIUS = 16

    def __init__(self, game: GomokuGame, parent=None):
        super().__init__(parent)
        self.game = game
        self.setMinimumSize(
            self.MARGIN * 2 + self.CELL_SIZE * (GomokuGame.BOARD_SIZE - 1) + 40,
            self.MARGIN * 2 + self.CELL_SIZE * (GomokuGame.BOARD_SIZE - 1) + 40,
        )
        self.setMouseTracking(True)
        self.hover_pos = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self._draw_board(painter)
        self._draw_pieces(painter)
        self._draw_last_move_marker(painter)
        self._draw_hover(painter)

    def _draw_board(self, painter: QPainter):
        size = GomokuGame.BOARD_SIZE
        board_width = self.CELL_SIZE * (size - 1)
        board_height = self.CELL_SIZE * (size - 1)

        bg_rect = self.rect().adjusted(10, 10, -10, -10)
        painter.setBrush(QBrush(QColor(222, 184, 135)))
        painter.setPen(QPen(QColor(139, 90, 43), 3))
        painter.drawRoundedRect(bg_rect, 10, 10)

        painter.setPen(QPen(QColor(80, 50, 20), 1, Qt.PenStyle.SolidLine))
        for i in range(size):
            start_x = self.MARGIN + 20
            start_y = self.MARGIN + 20
            painter.drawLine(
                start_x,
                start_y + i * self.CELL_SIZE,
                start_x + board_width,
                start_y + i * self.CELL_SIZE,
            )
            painter.drawLine(
                start_x + i * self.CELL_SIZE,
                start_y,
                start_x + i * self.CELL_SIZE,
                start_y + board_height,
            )

        star_points = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
        painter.setBrush(QBrush(QColor(80, 50, 20)))
        painter.setPen(Qt.PenStyle.NoPen)
        for row, col in star_points:
            x = self.MARGIN + 20 + col * self.CELL_SIZE
            y = self.MARGIN + 20 + row * self.CELL_SIZE
            painter.drawEllipse(QPoint(x, y), 4, 4)

    def _draw_pieces(self, painter: QPainter):
        for row in range(GomokuGame.BOARD_SIZE):
            for col in range(GomokuGame.BOARD_SIZE):
                piece = self.game.board[row][col]
                if piece != Player.EMPTY:
                    x = self.MARGIN + 20 + col * self.CELL_SIZE
                    y = self.MARGIN + 20 + row * self.CELL_SIZE

                    if piece == Player.BLACK:
                        gradient = QColor(20, 20, 20)
                        highlight = QColor(80, 80, 80)
                    else:
                        gradient = QColor(240, 240, 240)
                        highlight = QColor(255, 255, 255)

                    painter.setPen(QPen(QColor(50, 50, 50), 1))
                    painter.setBrush(QBrush(gradient))
                    painter.drawEllipse(
                        QPoint(x, y), self.PIECE_RADIUS, self.PIECE_RADIUS
                    )

                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(QBrush(highlight))
                    painter.drawEllipse(
                        QPoint(x - 5, y - 5), self.PIECE_RADIUS // 3, self.PIECE_RADIUS // 3
                    )

    def _draw_last_move_marker(self, painter: QPainter):
        last_move = self.game.get_last_move()
        if last_move:
            row, col = last_move
            x = self.MARGIN + 20 + col * self.CELL_SIZE
            y = self.MARGIN + 20 + row * self.CELL_SIZE
            painter.setPen(QPen(QColor(255, 0, 0), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPoint(x, y), 6, 6)

    def _draw_hover(self, painter: QPainter):
        if self.hover_pos and not self.game.game_over:
            row, col = self.hover_pos
            if self.game.is_valid_position(row, col) and not self.game.is_occupied(row, col):
                x = self.MARGIN + 20 + col * self.CELL_SIZE
                y = self.MARGIN + 20 + row * self.CELL_SIZE

                if self.game.current_player == Player.BLACK:
                    color = QColor(0, 0, 0, 80)
                else:
                    color = QColor(255, 255, 255, 120)

                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(color))
                painter.drawEllipse(
                    QPoint(x, y), self.PIECE_RADIUS, self.PIECE_RADIUS
                )

    def mouseMoveEvent(self, event):
        pos = event.position()
        row, col = self._pixel_to_board(pos.x(), pos.y())
        if self.game.is_valid_position(row, col):
            self.hover_pos = (row, col)
        else:
            self.hover_pos = None
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.game.game_over:
            pos = event.position()
            row, col = self._pixel_to_board(pos.x(), pos.y())
            if self.game.place_piece(row, col):
                self.hover_pos = None
                self.update()
                self.window().update_status()
                self.window().check_game_end()

    def leaveEvent(self, event):
        self.hover_pos = None
        self.update()

    def _pixel_to_board(self, x: float, y: float) -> tuple[int, int]:
        col = round((x - self.MARGIN - 20) / self.CELL_SIZE)
        row = round((y - self.MARGIN - 20) / self.CELL_SIZE)
        return int(row), int(col)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game = GomokuGame()
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("五子棋 - 单机版")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f0e6;
            }
            QPushButton {
                background-color: #8b5a2b;
                color: white;
                border: none;
                padding: 10px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a06230;
            }
            QPushButton:pressed {
                background-color: #6b4423;
            }
            QLabel {
                font-size: 16px;
                color: #4a3728;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_label = QLabel("五 子 棋")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #4a3728;
            padding: 10px;
        """)
        main_layout.addWidget(title_label)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #fff8e7;
                border: 2px solid #d4a574;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(self.status_label)

        self.board_widget = BoardWidget(self.game)
        self.board_widget.setStyleSheet("background-color: #f5f0e6;")
        main_layout.addWidget(self.board_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        self.reset_btn = QPushButton("🔄 重新开始")
        self.reset_btn.clicked.connect(self.reset_game)
        button_layout.addWidget(self.reset_btn)

        self.exit_btn = QPushButton("🚪 退出游戏")
        self.exit_btn.clicked.connect(self.close)
        button_layout.addWidget(self.exit_btn)

        main_layout.addLayout(button_layout)

        self.update_status()
        self.adjustSize()

    def update_status(self):
        if self.game.game_over:
            if self.game.winner:
                text = f"🎉 游戏结束 - {self.game.get_player_name(self.game.winner)} 获胜！"
            else:
                text = "🤝 游戏结束 - 平局！"
        else:
            text = f"当前回合：{self.game.get_player_name(self.game.current_player)}"
        self.status_label.setText(text)

    def check_game_end(self):
        if self.game.game_over:
            if self.game.winner:
                winner = self.game.get_player_name(self.game.winner)
                QMessageBox.information(
                    self,
                    "游戏结束",
                    f"🎉 恭喜！{winner} 获胜！\n\n点击确定后可以重新开始游戏。",
                )
            else:
                QMessageBox.information(
                    self,
                    "游戏结束",
                    "🤝 平局！棋盘已满。\n\n点击确定后可以重新开始游戏。",
                )

    def reset_game(self):
        reply = QMessageBox.question(
            self,
            "确认重置",
            "确定要重新开始游戏吗？\n当前棋局将会被清空。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.game.reset()
            self.board_widget.update()
            self.update_status()
