import sys
from PyQt6.QtCore import Qt, QPoint, QRectF, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QIcon, QFont, QRadialGradient, QLinearGradient
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
    QFrame,
    QStackedWidget,
    QMenuBar,
    QMenu,
    QFileDialog,
)

from game.gomoku import GomokuGame, Player
from game.xiangqi import XiangqiGame, Piece, PieceColor, PieceType
from gui.game_selector import GameSelector
from gui.xiangqi_widget import XiangqiBoardWidget
from gui.settings_dialog import SettingsDialog
from utils.config_manager import ConfigManager
from utils.theme_manager import ThemeManager
from utils.sound_manager import SoundManager
from utils.timer_manager import GameTimer


class BoardWidget(QWidget):
    MARGIN = 40
    CELL_SIZE = 40
    PIECE_RADIUS = 16

    def __init__(self, game: GomokuGame, parent=None):
        super().__init__(parent)
        self.game = game
        self.config = ConfigManager()
        self.theme_manager = ThemeManager()
        self.sound_manager = SoundManager()
        self.setMinimumSize(
            self.MARGIN * 2 + self.CELL_SIZE * (GomokuGame.BOARD_SIZE - 1) + 40,
            self.MARGIN * 2 + self.CELL_SIZE * (GomokuGame.BOARD_SIZE - 1) + 40,
        )
        self.setMouseTracking(True)
        self.hover_pos = None
        self.anim_progress = 0.0
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._update_animation)
        self.last_move_anim = None

    def _update_animation(self):
        self.anim_progress += 0.08
        if self.anim_progress >= 1.0:
            self.anim_progress = 1.0
            self.anim_timer.stop()
        self.update()

    def start_place_animation(self):
        self.anim_progress = 0.0
        self.anim_timer.start(16)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self._draw_board(painter)
        self._draw_pieces(painter)
        if self.config.get("show_last_move", True):
            self._draw_last_move_marker(painter)
        self._draw_hover(painter)

    def _draw_board(self, painter: QPainter):
        board_skin = self.theme_manager.get_board_skin()
        size = GomokuGame.BOARD_SIZE
        board_width = self.CELL_SIZE * (size - 1)
        board_height = self.CELL_SIZE * (size - 1)

        bg_rect = self.rect().adjusted(10, 10, -10, -10)
        gradient = QRadialGradient(
            bg_rect.center().x(), bg_rect.center().y(), bg_rect.width()
        )
        gradient.setColorAt(0, board_skin["bg_start"])
        gradient.setColorAt(1, board_skin["bg_end"])
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(board_skin["border"], 3))
        painter.drawRoundedRect(bg_rect, 10, 10)

        painter.setPen(QPen(board_skin["line"], 1, Qt.PenStyle.SolidLine))
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
        painter.setBrush(QBrush(board_skin["line"]))
        painter.setPen(Qt.PenStyle.NoPen)
        for row, col in star_points:
            x = self.MARGIN + 20 + col * self.CELL_SIZE
            y = self.MARGIN + 20 + row * self.CELL_SIZE
            painter.drawEllipse(QPoint(x, y), 4, 4)

    def _draw_pieces(self, painter: QPainter):
        piece_skin = self.theme_manager.get_piece_skin()
        last_move = self.game.get_last_move()

        for row in range(GomokuGame.BOARD_SIZE):
            for col in range(GomokuGame.BOARD_SIZE):
                piece = self.game.board[row][col]
                if piece != Player.EMPTY:
                    x = self.MARGIN + 20 + col * self.CELL_SIZE
                    y = self.MARGIN + 20 + row * self.CELL_SIZE

                    scale = 1.0
                    if last_move == (row, col) and self.anim_progress < 1.0:
                        scale = 0.8 + 0.2 * self.anim_progress

                    radius = self.PIECE_RADIUS * scale

                    if piece == Player.BLACK:
                        gradient = piece_skin["black_piece"]
                        highlight = piece_skin["black_highlight"]
                    else:
                        gradient = piece_skin["white_piece"]
                        highlight = piece_skin["white_highlight"]

                    painter.setPen(QPen(QColor(50, 50, 50), 1))
                    painter.setBrush(QBrush(gradient))
                    painter.drawEllipse(
                        QPoint(x, y), radius, radius
                    )

                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(QBrush(highlight))
                    painter.drawEllipse(
                        QPoint(x - 5, y - 5), radius // 3, radius // 3
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
                self.sound_manager.play_sfx("place_piece")
                self.start_place_animation()
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

    def refresh_theme(self):
        self.update()


class GomokuGamePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.game = GomokuGame()
        self.sound_manager = SoundManager()
        self.timer = GameTimer()
        self.timer.time_updated.connect(self._on_timer_updated)
        self.timer.time_out.connect(self._on_timer_out)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_label = QLabel("⚫ 五 子 棋 ⚪")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #4a3728;
            padding: 10px;
            background: transparent;
        """)
        main_layout.addWidget(title_label)

        timer_layout = QHBoxLayout()
        timer_layout.setSpacing(20)
        timer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.player1_timer_label = QLabel("⏱ 黑棋: 10:00")
        self.player1_timer_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 8px 16px;
            background-color: #fff8e7;
            border: 2px solid #34495e;
            border-radius: 8px;
        """)
        timer_layout.addWidget(self.player1_timer_label)

        self.player2_timer_label = QLabel("⏱ 白棋: 10:00")
        self.player2_timer_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #7f8c8d;
            padding: 8px 16px;
            background-color: #fff8e7;
            border: 2px solid #bdc3c7;
            border-radius: 8px;
        """)
        timer_layout.addWidget(self.player2_timer_label)

        main_layout.addLayout(timer_layout)

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
                color: #4a3728;
            }
        """)
        main_layout.addWidget(self.status_label)

        self.board_widget = BoardWidget(self.game)
        self.board_widget.setStyleSheet("background-color: #f5f0e6;")
        main_layout.addWidget(self.board_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.back_btn = QPushButton("🏠 返回大厅")
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
            QPushButton:pressed {
                background-color: #606c6d;
            }
        """)
        button_layout.addWidget(self.back_btn)

        self.undo_btn = QPushButton("↩ 悔棋")
        self.undo_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f1c40f;
            }
            QPushButton:pressed {
                background-color: #d68910;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.undo_btn.clicked.connect(self.undo_move)
        button_layout.addWidget(self.undo_btn)

        self.save_btn = QPushButton("💾 保存棋谱")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.save_btn.clicked.connect(self.save_record)
        button_layout.addWidget(self.save_btn)

        self.reset_btn = QPushButton("🔄 重新开始")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5a2b;
                color: white;
                border: none;
                padding: 10px 20px;
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
        """)
        button_layout.addWidget(self.reset_btn)

        main_layout.addLayout(button_layout)

        self.update_status()
        self._update_undo_button()

    def _on_timer_updated(self, player1_time: str, player2_time: str):
        self.player1_timer_label.setText(f"⏱ 黑棋: {player1_time}")
        self.player2_timer_label.setText(f"⏱ 白棋: {player2_time}")

        if self.timer.current_player == 1:
            self.player1_timer_label.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: white;
                padding: 8px 16px;
                background-color: #2c3e50;
                border: 2px solid #e74c3c;
                border-radius: 8px;
            """)
            self.player2_timer_label.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #7f8c8d;
                padding: 8px 16px;
                background-color: #fff8e7;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
            """)
        else:
            self.player1_timer_label.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px 16px;
                background-color: #fff8e7;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
            """)
            self.player2_timer_label.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: white;
                padding: 8px 16px;
                background-color: #ecf0f1;
                border: 2px solid #e74c3c;
                border-radius: 8px;
            """)

    def _on_timer_out(self, player: str):
        winner = "白棋" if player == "player1" else "黑棋"
        self.game.game_over = True
        self.game.winner = Player.WHITE if player == "player1" else Player.BLACK
        self.update_status()
        self.sound_manager.play_sfx("win")
        QMessageBox.information(
            self,
            "五子棋 - 游戏结束",
            f"⏱ 时间到！{winner} 获胜！",
        )

    def undo_move(self):
        if self.game.undo():
            self.sound_manager.play_sfx("undo")
            self.timer.switch_player()
            self.board_widget.update()
            self.update_status()
            self._update_undo_button()

    def _update_undo_button(self):
        self.undo_btn.setEnabled(self.game.can_undo())

    def save_record(self):
        filepath = self.game.save_record()
        if filepath:
            self.sound_manager.play_sfx("click")
            QMessageBox.information(
                self,
                "保存棋谱",
                f"棋谱已保存到：\n{filepath}",
            )
        else:
            QMessageBox.warning(
                self,
                "保存失败",
                "没有可保存的棋谱记录！",
            )

    def update_status(self):
        if self.game.game_over:
            if self.game.winner:
                text = f"🎉 游戏结束 - {self.game.get_player_name(self.game.winner)} 获胜！"
            else:
                text = "🤝 游戏结束 - 平局！"
            self.timer.stop()
        else:
            text = f"当前回合：{self.game.get_player_name(self.game.current_player)}"
        self.status_label.setText(text)
        self._update_undo_button()

    def check_game_end(self):
        if self.game.game_over:
            if self.game.winner:
                winner = self.game.get_player_name(self.game.winner)
                self.sound_manager.play_sfx("win")
                QMessageBox.information(
                    self,
                    "五子棋 - 游戏结束",
                    f"🎉 恭喜！{winner} 获胜！\n\n点击确定后可以重新开始游戏。",
                )
            else:
                QMessageBox.information(
                    self,
                    "五子棋 - 游戏结束",
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
            self.sound_manager.play_sfx("click")
            self.game.reset()
            if self.timer.is_enabled():
                self.timer.reset()
            self.board_widget.update()
            self.update_status()

    def start_game(self):
        if self.timer.is_enabled():
            self.timer.start()
            self._on_timer_updated(self.timer.get_player1_time(), self.timer.get_player2_time())

    def pause_game(self):
        self.timer.pause()

    def refresh_theme(self):
        self.board_widget.refresh_theme()


class XiangqiGamePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.game = XiangqiGame()
        self.sound_manager = SoundManager()
        self.timer = GameTimer()
        self.timer.time_updated.connect(self._on_timer_updated)
        self.timer.time_out.connect(self._on_timer_out)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_label = QLabel("🏯 中 国 象 棋 🏯")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #4a3728;
            padding: 10px;
            background: transparent;
        """)
        main_layout.addWidget(title_label)

        timer_layout = QHBoxLayout()
        timer_layout.setSpacing(20)
        timer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.player2_timer_label = QLabel("⏱ 黑方: 10:00")
        self.player2_timer_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 8px 16px;
            background-color: #fff8e7;
            border: 2px solid #34495e;
            border-radius: 8px;
        """)
        timer_layout.addWidget(self.player2_timer_label)

        self.player1_timer_label = QLabel("⏱ 红方: 10:00")
        self.player1_timer_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #c0392b;
            padding: 8px 16px;
            background-color: #fff8e7;
            border: 2px solid #e74c3c;
            border-radius: 8px;
        """)
        timer_layout.addWidget(self.player1_timer_label)

        main_layout.addLayout(timer_layout)

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
                color: #4a3728;
            }
        """)
        main_layout.addWidget(self.status_label)

        self.board_widget = XiangqiBoardWidget(self.game)
        self.board_widget.setStyleSheet("background-color: #f5f0e6;")
        main_layout.addWidget(self.board_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.back_btn = QPushButton("🏠 返回大厅")
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
            QPushButton:pressed {
                background-color: #606c6d;
            }
        """)
        button_layout.addWidget(self.back_btn)

        self.undo_btn = QPushButton("↩ 悔棋")
        self.undo_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f1c40f;
            }
            QPushButton:pressed {
                background-color: #d68910;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.undo_btn.clicked.connect(self.undo_move)
        button_layout.addWidget(self.undo_btn)

        self.save_btn = QPushButton("💾 保存棋谱")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.save_btn.clicked.connect(self.save_record)
        button_layout.addWidget(self.save_btn)

        self.reset_btn = QPushButton("🔄 重新开始")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        button_layout.addWidget(self.reset_btn)

        main_layout.addLayout(button_layout)

        self.update_status()
        self._update_undo_button()

    def _on_timer_updated(self, player1_time: str, player2_time: str):
        self.player1_timer_label.setText(f"⏱ 红方: {player1_time}")
        self.player2_timer_label.setText(f"⏱ 黑方: {player2_time}")

        if self.timer.current_player == 1:
            self.player1_timer_label.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: white;
                padding: 8px 16px;
                background-color: #c0392b;
                border: 2px solid #f39c12;
                border-radius: 8px;
            """)
            self.player2_timer_label.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px 16px;
                background-color: #fff8e7;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
            """)
        else:
            self.player1_timer_label.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #c0392b;
                padding: 8px 16px;
                background-color: #fff8e7;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
            """)
            self.player2_timer_label.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: white;
                padding: 8px 16px;
                background-color: #2c3e50;
                border: 2px solid #f39c12;
                border-radius: 8px;
            """)

    def _on_timer_out(self, player: str):
        winner = "黑方" if player == "player1" else "红方"
        self.game.game_over = True
        self.game.winner = PieceColor.BLACK if player == "player1" else PieceColor.RED
        self.update_status()
        self.sound_manager.play_sfx("win")
        QMessageBox.information(
            self,
            "中国象棋 - 游戏结束",
            f"⏱ 时间到！{winner} 获胜！",
        )

    def undo_move(self):
        if self.game.undo():
            self.sound_manager.play_sfx("undo")
            self.timer.switch_player()
            self.board_widget.update()
            self.update_status()
            self._update_undo_button()

    def _update_undo_button(self):
        self.undo_btn.setEnabled(self.game.can_undo())

    def save_record(self):
        filepath = self.game.save_record()
        if filepath:
            self.sound_manager.play_sfx("click")
            QMessageBox.information(
                self,
                "保存棋谱",
                f"棋谱已保存到：\n{filepath}",
            )
        else:
            QMessageBox.warning(
                self,
                "保存失败",
                "没有可保存的棋谱记录！",
            )

    def update_status(self):
        if self.game.game_over:
            if self.game.winner is not None:
                text = f"🎉 游戏结束 - {self.game.get_player_name(self.game.winner)} 获胜！"
            else:
                text = "🤝 游戏结束 - 平局！"
            self.timer.stop()
        else:
            status_text = f"当前回合：{self.game.get_current_player_name()}"
            if self.game.is_in_check:
                status_text += "  ⚠ 将军！"
            text = status_text
        self.status_label.setText(text)
        self._update_undo_button()

    def check_game_end(self):
        if self.game.game_over:
            if self.game.winner is not None:
                winner = self.game.get_player_name(self.game.winner)
                self.sound_manager.play_sfx("win")
                QMessageBox.information(
                    self,
                    "中国象棋 - 游戏结束",
                    f"🎉 恭喜！{winner} 获胜！\n\n点击确定后可以重新开始游戏。",
                )
            else:
                QMessageBox.information(
                    self,
                    "中国象棋 - 游戏结束",
                    "🤝 平局！\n\n点击确定后可以重新开始游戏。",
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
            self.sound_manager.play_sfx("click")
            self.game.reset()
            if self.timer.is_enabled():
                self.timer.reset()
            self.board_widget.update()
            self.update_status()

    def start_game(self):
        if self.timer.is_enabled():
            self.timer.start()
            self._on_timer_updated(self.timer.get_player1_time(), self.timer.get_player2_time())

    def pause_game(self):
        self.timer.pause()

    def refresh_theme(self):
        self.board_widget.refresh_theme()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.theme_manager = ThemeManager()
        self.sound_manager = SoundManager()
        self._init_ui()
        self._apply_window_settings()

    def _init_ui(self):
        self.setWindowTitle("棋类游戏大厅 - 五子棋 & 中国象棋")
        self.setMinimumSize(900, 700)

        self._create_menu()
        self._apply_theme()

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.game_selector = GameSelector()
        self.gomoku_page = GomokuGamePage()
        self.xiangqi_page = XiangqiGamePage()

        self.stacked_widget.addWidget(self.game_selector)
        self.stacked_widget.addWidget(self.gomoku_page)
        self.stacked_widget.addWidget(self.xiangqi_page)

        self.game_selector.game_selected.connect(self._on_game_selected)
        self.gomoku_page.back_btn.clicked.connect(self._back_to_selector)
        self.gomoku_page.reset_btn.clicked.connect(self.gomoku_page.reset_game)
        self.gomoku_page.board_widget.window = lambda: self
        self.xiangqi_page.back_btn.clicked.connect(self._back_to_selector)
        self.xiangqi_page.reset_btn.clicked.connect(self.xiangqi_page.reset_game)
        self.xiangqi_page.board_widget.window = lambda: self

        self.stacked_widget.setCurrentIndex(0)
        self.adjustSize()

        if self.sound_manager.is_sound_enabled():
            self.sound_manager.play_bgm()

    def _create_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("文件(&F)")

        new_game_action = file_menu.addAction("重新开始(&N)")
        new_game_action.setShortcut("Ctrl+N")
        new_game_action.triggered.connect(self._reset_current_game)

        save_action = file_menu.addAction("保存棋谱(&S)")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_current_record)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("退出(&Q)")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        view_menu = menubar.addMenu("视图(&V)")

        fullscreen_action = view_menu.addAction("全屏(&F)")
        fullscreen_action.setShortcut("F11")
        fullscreen_action.setCheckable(True)
        fullscreen_action.triggered.connect(self._toggle_fullscreen)

        view_menu.addSeparator()

        settings_action = view_menu.addAction("设置(&O)")
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self._open_settings)

        game_menu = menubar.addMenu("游戏(&G)")

        undo_action = game_menu.addAction("悔棋(&U)")
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self._undo_current_game)

        game_menu.addSeparator()

        gomoku_action = game_menu.addAction("五子棋(&G)")
        gomoku_action.triggered.connect(lambda: self._on_game_selected(0))

        xiangqi_action = game_menu.addAction("中国象棋(&X)")
        xiangqi_action.triggered.connect(lambda: self._on_game_selected(1))

        sound_menu = menubar.addMenu("声音(&A)")

        sound_toggle = sound_menu.addAction("静音(&M)")
        sound_toggle.setShortcut("Ctrl+M")
        sound_toggle.setCheckable(True)
        sound_toggle.setChecked(not self.sound_manager.is_sound_enabled())
        sound_toggle.triggered.connect(
            lambda checked: self.sound_manager.toggle_sound(not checked)
        )

        help_menu = menubar.addMenu("帮助(&H)")

        about_action = help_menu.addAction("关于(&A)")
        about_action.triggered.connect(self._show_about)

        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #8b5a2b;
                color: white;
                padding: 4px;
            }
            QMenuBar::item {
                padding: 6px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #a06230;
            }
            QMenu {
                background-color: #fff8e7;
                border: 2px solid #d4a574;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 4px;
                color: #4a3728;
            }
            QMenu::item:selected {
                background-color: #d4a574;
                color: white;
            }
        """)

    def _apply_theme(self):
        stylesheet = self.theme_manager.get_global_stylesheet()
        self.setStyleSheet(stylesheet)

    def _apply_window_settings(self):
        window_size = self.config.get("window_size", [1000, 800])
        self.resize(window_size[0], window_size[1])

        if self.config.get("fullscreen", False):
            self.showFullScreen()

    def _toggle_fullscreen(self, checked: bool):
        if checked:
            self.showFullScreen()
            self.config.set("fullscreen", True)
        else:
            self.showNormal()
            self.config.set("fullscreen", False)
        self.config.save_config()

    def _open_settings(self):
        dialog = SettingsDialog(self)
        dialog.settings_applied.connect(self._on_settings_applied)
        dialog.exec()

    def _on_settings_applied(self):
        self._apply_theme()
        self.gomoku_page.refresh_theme()
        self.xiangqi_page.refresh_theme()
        self.sound_manager.play_sfx("click")

    def _on_game_selected(self, game_index: int):
        self.sound_manager.play_sfx("click")
        if game_index == 0:
            self.gomoku_page.game.reset()
            self.gomoku_page.board_widget.update()
            self.gomoku_page.update_status()
            self.gomoku_page.start_game()
            self.xiangqi_page.pause_game()
            self.stacked_widget.setCurrentIndex(1)
        elif game_index == 1:
            self.xiangqi_page.game.reset()
            self.xiangqi_page.board_widget.update()
            self.xiangqi_page.update_status()
            self.xiangqi_page.start_game()
            self.gomoku_page.pause_game()
            self.stacked_widget.setCurrentIndex(2)
        self.adjustSize()

    def _back_to_selector(self):
        self.sound_manager.play_sfx("click")
        self.gomoku_page.pause_game()
        self.xiangqi_page.pause_game()
        self.stacked_widget.setCurrentIndex(0)
        self.adjustSize()

    def _reset_current_game(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index == 1:
            self.gomoku_page.reset_game()
        elif current_index == 2:
            self.xiangqi_page.reset_game()

    def _save_current_record(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index == 1:
            self.gomoku_page.save_record()
        elif current_index == 2:
            self.xiangqi_page.save_record()
        else:
            QMessageBox.information(
                self,
                "保存棋谱",
                "请先进入游戏后再保存棋谱！",
            )

    def _undo_current_game(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index == 1:
            self.gomoku_page.undo_move()
        elif current_index == 2:
            self.xiangqi_page.undo_move()

    def update_status(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index == 1:
            self.gomoku_page.update_status()
        elif current_index == 2:
            self.xiangqi_page.update_status()

    def check_game_end(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index == 1:
            self.gomoku_page.check_game_end()
        elif current_index == 2:
            self.xiangqi_page.check_game_end()

    def _show_about(self):
        QMessageBox.about(
            self,
            "关于",
            """<h2>🎮 棋类游戏大厅</h2>
            <p>一个基于 Python + PyQt6 的双人本地对战棋类游戏</p>
            <p><b>支持游戏：</b>五子棋、中国象棋</p>
            <p><b>特色功能：</b></p>
            <ul>
                <li>🎨 多种主题和皮肤可选</li>
                <li>🔊 背景音乐和音效</li>
                <li>⏱ 游戏计时功能</li>
                <li>↩ 悔棋功能</li>
                <li>💾 棋谱本地保存</li>
                <li>📺 全屏模式</li>
            </ul>
            <p><b>版本：</b>2.0</p>
            """,
        )

    def closeEvent(self, event):
        self.config.set("window_size", [self.width(), self.height()])
        self.config.save_config()
        self.sound_manager.stop_bgm()
        super().closeEvent(event)

    def resizeEvent(self, event):
        self.stacked_widget.currentWidget().adjustSize()
        super().resizeEvent(event)
