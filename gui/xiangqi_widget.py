from PyQt6.QtCore import Qt, QPoint, QRectF, QTimer
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QRadialGradient, QLinearGradient
from PyQt6.QtWidgets import QWidget

from game.xiangqi import XiangqiGame, Piece, PieceColor, PieceType
from utils.config_manager import ConfigManager
from utils.theme_manager import ThemeManager
from utils.sound_manager import SoundManager


class XiangqiBoardWidget(QWidget):
    MARGIN = 40
    CELL_SIZE = 50
    PIECE_RADIUS = 22

    def __init__(self, game: XiangqiGame, parent=None):
        super().__init__(parent)
        self.game = game
        self.config = ConfigManager()
        self.theme_manager = ThemeManager()
        self.sound_manager = SoundManager()
        self.setMinimumSize(
            self.MARGIN * 2 + self.CELL_SIZE * (XiangqiGame.COLS - 1) + 60,
            self.MARGIN * 2 + self.CELL_SIZE * (XiangqiGame.ROWS - 1) + 60,
        )
        self.setMouseTracking(True)
        self.hover_pos = None
        self.anim_progress = 0.0
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._update_animation)

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

        self._draw_board_background(painter)
        self._draw_board_lines(painter)
        self._draw_river(painter)
        self._draw_palace(painter)
        if self.config.get("show_valid_moves", True):
            self._draw_valid_moves(painter)
        self._draw_selected_piece(painter)
        self._draw_pieces(painter)
        if self.config.get("show_last_move", True):
            self._draw_last_move_marker(painter)
        self._draw_hover(painter)

    def _draw_board_background(self, painter: QPainter):
        board_skin = self.theme_manager.get_board_skin()
        bg_rect = self.rect().adjusted(10, 10, -10, -10)
        gradient = QRadialGradient(
            bg_rect.center().x(), bg_rect.center().y(), bg_rect.width()
        )
        gradient.setColorAt(0, board_skin["bg_start"])
        gradient.setColorAt(1, board_skin["bg_end"])
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(board_skin["border"], 4))
        painter.drawRoundedRect(bg_rect, 15, 15)

        inner_rect = bg_rect.adjusted(15, 15, -15, -15)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(board_skin["border"].lighter(120), 2))
        painter.drawRoundedRect(inner_rect, 10, 10)

    def _draw_board_lines(self, painter: QPainter):
        board_skin = self.theme_manager.get_board_skin()
        painter.setPen(QPen(board_skin["line"], 2, Qt.PenStyle.SolidLine))

        start_x = self.MARGIN + 30
        start_y = self.MARGIN + 30
        board_width = self.CELL_SIZE * (XiangqiGame.COLS - 1)
        board_height = self.CELL_SIZE * (XiangqiGame.ROWS - 1)

        for row in range(XiangqiGame.ROWS):
            y = start_y + row * self.CELL_SIZE
            painter.drawLine(start_x, y, start_x + board_width, y)

        for col in range(XiangqiGame.COLS):
            x = start_x + col * self.CELL_SIZE
            if col == 0 or col == XiangqiGame.COLS - 1:
                painter.drawLine(x, start_y, x, start_y + board_height)
            else:
                painter.drawLine(x, start_y, x, start_y + self.CELL_SIZE * 4)
                painter.drawLine(
                    x,
                    start_y + self.CELL_SIZE * 5,
                    x,
                    start_y + board_height,
                )

    def _draw_river(self, painter: QPainter):
        board_skin = self.theme_manager.get_board_skin()
        start_x = self.MARGIN + 30
        start_y = self.MARGIN + 30
        board_width = self.CELL_SIZE * (XiangqiGame.COLS - 1)

        river_y = start_y + self.CELL_SIZE * 4
        river_height = self.CELL_SIZE

        painter.setBrush(QBrush(board_skin["river"]))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(start_x, river_y, board_width, river_height)

        painter.setPen(QPen(board_skin["river_text"], 1))
        font = QFont("KaiTi", 24, QFont.Weight.Bold)
        painter.setFont(font)

        text_rect1 = QRectF(
            start_x + 40,
            river_y,
            board_width / 2 - 60,
            river_height,
        )
        painter.drawText(
            text_rect1,
            Qt.AlignmentFlag.AlignCenter,
            "楚 河",
        )

        text_rect2 = QRectF(
            start_x + board_width / 2 + 20,
            river_y,
            board_width / 2 - 60,
            river_height,
        )
        painter.drawText(
            text_rect2,
            Qt.AlignmentFlag.AlignCenter,
            "汉 界",
        )

    def _draw_palace(self, painter: QPainter):
        board_skin = self.theme_manager.get_board_skin()
        painter.setPen(QPen(board_skin["line"], 2, Qt.PenStyle.SolidLine))

        start_x = self.MARGIN + 30
        start_y = self.MARGIN + 30

        top_palace_x = start_x + self.CELL_SIZE * 3
        top_palace_y = start_y

        painter.drawLine(
            top_palace_x,
            top_palace_y,
            top_palace_x + self.CELL_SIZE * 2,
            top_palace_y + self.CELL_SIZE * 2,
        )
        painter.drawLine(
            top_palace_x + self.CELL_SIZE * 2,
            top_palace_y,
            top_palace_x,
            top_palace_y + self.CELL_SIZE * 2,
        )

        bottom_palace_y = start_y + self.CELL_SIZE * 7

        painter.drawLine(
            top_palace_x,
            bottom_palace_y,
            top_palace_x + self.CELL_SIZE * 2,
            bottom_palace_y + self.CELL_SIZE * 2,
        )
        painter.drawLine(
            top_palace_x + self.CELL_SIZE * 2,
            bottom_palace_y,
            top_palace_x,
            bottom_palace_y + self.CELL_SIZE * 2,
        )

    def _draw_valid_moves(self, painter: QPainter):
        if not self.game.valid_moves:
            return

        start_x = self.MARGIN + 30
        start_y = self.MARGIN + 30

        for row, col in self.game.valid_moves:
            x = start_x + col * self.CELL_SIZE
            y = start_y + row * self.CELL_SIZE

            target = self.game.board[row][col]
            if target:
                painter.setPen(QPen(QColor(255, 0, 0), 3))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(
                    QPoint(x, y), self.PIECE_RADIUS + 4, self.PIECE_RADIUS + 4
                )
            else:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor(0, 180, 0, 120)))
                painter.drawEllipse(QPoint(x, y), 8, 8)

    def _draw_selected_piece(self, painter: QPainter):
        if not self.game.selected_pos:
            return

        row, col = self.game.selected_pos
        start_x = self.MARGIN + 30
        start_y = self.MARGIN + 30
        x = start_x + col * self.CELL_SIZE
        y = start_y + row * self.CELL_SIZE

        painter.setPen(QPen(QColor(255, 200, 0), 4))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(
            x - self.PIECE_RADIUS - 4,
            y - self.PIECE_RADIUS - 4,
            (self.PIECE_RADIUS + 4) * 2,
            (self.PIECE_RADIUS + 4) * 2,
        )

    def _draw_pieces(self, painter: QPainter):
        piece_skin = self.theme_manager.get_piece_skin()
        start_x = self.MARGIN + 30
        start_y = self.MARGIN + 30

        last_move = None
        if self.game.move_history:
            _, (to_row, to_col), _ = self.game.move_history[-1]
            last_move = (to_row, to_col)

        for row in range(XiangqiGame.ROWS):
            for col in range(XiangqiGame.COLS):
                piece = self.game.board[row][col]
                if piece:
                    x = start_x + col * self.CELL_SIZE
                    y = start_y + row * self.CELL_SIZE

                    scale = 1.0
                    if last_move == (row, col) and self.anim_progress < 1.0:
                        scale = 0.8 + 0.2 * self.anim_progress

                    self._draw_piece(painter, x, y, piece, piece_skin, scale)

    def _draw_piece(self, painter: QPainter, x: int, y: int, piece: Piece, piece_skin: dict, scale: float = 1.0):
        radius = self.PIECE_RADIUS * scale

        if piece.color == PieceColor.RED:
            bg_color = piece_skin["red_bg"]
            border_color = piece_skin["red_border"]
            text_color = piece_skin["red_text"]
        else:
            bg_color = piece_skin["black_bg"]
            border_color = piece_skin["black_border"]
            text_color = piece_skin["black_text"]

        gradient = QRadialGradient(x - 5, y - 5, radius + 10)
        gradient.setColorAt(0, QColor(255, 253, 240))
        gradient.setColorAt(1, bg_color)

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(border_color, 2))
        painter.drawEllipse(QPoint(x, y), radius, radius)

        painter.setPen(QPen(border_color, 1))
        painter.drawEllipse(
            QPoint(x, y), radius - 3, radius - 3
        )

        font = QFont("KaiTi", int(22 * scale), QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QPen(text_color, 1))
        painter.setBrush(QBrush(text_color))
        painter.drawText(
            QRectF(
                x - radius,
                y - radius,
                radius * 2,
                radius * 2,
            ),
            Qt.AlignmentFlag.AlignCenter,
            piece.get_display_name(),
        )

    def _draw_last_move_marker(self, painter: QPainter):
        if not self.game.move_history:
            return

        _, (to_row, to_col), _ = self.game.move_history[-1]
        start_x = self.MARGIN + 30
        start_y = self.MARGIN + 30
        x = start_x + to_col * self.CELL_SIZE
        y = start_y + to_row * self.CELL_SIZE

        painter.setPen(QPen(QColor(0, 120, 255), 3))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPoint(x, y), self.PIECE_RADIUS + 2, self.PIECE_RADIUS + 2)

    def _draw_hover(self, painter: QPainter):
        if not self.hover_pos or self.game.game_over:
            return

        row, col = self.hover_pos
        if not self.game.is_valid_position(row, col):
            return

        piece = self.game.board[row][col]

        if self.game.selected_pos:
            if (row, col) in self.game.valid_moves:
                start_x = self.MARGIN + 30
                start_y = self.MARGIN + 30
                x = start_x + col * self.CELL_SIZE
                y = start_y + row * self.CELL_SIZE

                if piece:
                    painter.setPen(QPen(QColor(255, 0, 0, 150), 2))
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    painter.drawEllipse(
                        QPoint(x, y), self.PIECE_RADIUS + 4, self.PIECE_RADIUS + 4
                    )
                else:
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(QBrush(QColor(0, 200, 0, 80)))
                    painter.drawEllipse(QPoint(x, y), 10, 10)
        else:
            if piece and piece.color == self.game.current_player:
                start_x = self.MARGIN + 30
                start_y = self.MARGIN + 30
                x = start_x + col * self.CELL_SIZE
                y = start_y + row * self.CELL_SIZE

                painter.setPen(QPen(QColor(255, 200, 0, 150), 3))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRect(
                    x - self.PIECE_RADIUS - 4,
                    y - self.PIECE_RADIUS - 4,
                    (self.PIECE_RADIUS + 4) * 2,
                    (self.PIECE_RADIUS + 4) * 2,
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
        if event.button() != Qt.MouseButton.LeftButton:
            return

        if self.game.game_over:
            return

        pos = event.position()
        row, col = self._pixel_to_board(pos.x(), pos.y())

        if not self.game.is_valid_position(row, col):
            return

        if self.game.selected_pos:
            if (row, col) in self.game.valid_moves:
                from_row, from_col = self.game.selected_pos
                captured = self.game.board[row][col]
                if self.game.move_piece(row, col):
                    if captured:
                        self.sound_manager.play_sfx("capture")
                    else:
                        self.sound_manager.play_sfx("move")
                    self.start_place_animation()
                    self.hover_pos = None
                    self.update()
                    if hasattr(self, 'window') and callable(self.window):
                        self.window().update_status()
                        self.window().check_game_end()
                        try:
                            self.window().timer.switch_player()
                        except:
                            pass
                    return

            clicked_piece = self.game.board[row][col]
            if clicked_piece and clicked_piece.color == self.game.current_player:
                self.sound_manager.play_sfx("click")
                self.game.select_piece(row, col)
                self.update()
                return

            self.game.selected_pos = None
            self.game.valid_moves = []
            self.update()
        else:
            if self.game.select_piece(row, col):
                self.sound_manager.play_sfx("click")
                self.update()

    def leaveEvent(self, event):
        self.hover_pos = None
        self.update()

    def _pixel_to_board(self, x: float, y: float) -> tuple[int, int]:
        col = round((x - self.MARGIN - 30) / self.CELL_SIZE)
        row = round((y - self.MARGIN - 30) / self.CELL_SIZE)
        return int(row), int(col)

    def refresh_theme(self):
        self.update()
