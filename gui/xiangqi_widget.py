from PyQt6.QtCore import Qt, QPoint, QRectF
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QRadialGradient
from PyQt6.QtWidgets import QWidget

from game.xiangqi import XiangqiGame, Piece, PieceColor, PieceType


class XiangqiBoardWidget(QWidget):
    MARGIN = 40
    CELL_SIZE = 50
    PIECE_RADIUS = 22

    def __init__(self, game: XiangqiGame, parent=None):
        super().__init__(parent)
        self.game = game
        self.setMinimumSize(
            self.MARGIN * 2 + self.CELL_SIZE * (XiangqiGame.COLS - 1) + 60,
            self.MARGIN * 2 + self.CELL_SIZE * (XiangqiGame.ROWS - 1) + 60,
        )
        self.setMouseTracking(True)
        self.hover_pos = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self._draw_board_background(painter)
        self._draw_board_lines(painter)
        self._draw_river(painter)
        self._draw_palace(painter)
        self._draw_valid_moves(painter)
        self._draw_selected_piece(painter)
        self._draw_pieces(painter)
        self._draw_last_move_marker(painter)
        self._draw_hover(painter)

    def _draw_board_background(self, painter: QPainter):
        bg_rect = self.rect().adjusted(10, 10, -10, -10)
        gradient = QRadialGradient(
            bg_rect.center().x(), bg_rect.center().y(), bg_rect.width()
        )
        gradient.setColorAt(0, QColor(255, 248, 220))
        gradient.setColorAt(1, QColor(222, 184, 135))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(139, 90, 43), 4))
        painter.drawRoundedRect(bg_rect, 15, 15)

        inner_rect = bg_rect.adjusted(15, 15, -15, -15)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(160, 82, 45), 2))
        painter.drawRoundedRect(inner_rect, 10, 10)

    def _draw_board_lines(self, painter: QPainter):
        painter.setPen(QPen(QColor(80, 50, 20), 2, Qt.PenStyle.SolidLine))

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
        start_x = self.MARGIN + 30
        start_y = self.MARGIN + 30
        board_width = self.CELL_SIZE * (XiangqiGame.COLS - 1)

        river_y = start_y + self.CELL_SIZE * 4
        river_height = self.CELL_SIZE

        painter.setBrush(QBrush(QColor(173, 216, 230, 50)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(start_x, river_y, board_width, river_height)

        painter.setPen(QPen(QColor(70, 130, 180), 1))
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
        painter.setPen(QPen(QColor(80, 50, 20), 2, Qt.PenStyle.SolidLine))

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
        start_x = self.MARGIN + 30
        start_y = self.MARGIN + 30

        for row in range(XiangqiGame.ROWS):
            for col in range(XiangqiGame.COLS):
                piece = self.game.board[row][col]
                if piece:
                    x = start_x + col * self.CELL_SIZE
                    y = start_y + row * self.CELL_SIZE
                    self._draw_piece(painter, x, y, piece)

    def _draw_piece(self, painter: QPainter, x: int, y: int, piece: Piece):
        if piece.color == PieceColor.RED:
            bg_color = QColor(255, 248, 220)
            border_color = QColor(180, 0, 0)
            text_color = QColor(200, 0, 0)
        else:
            bg_color = QColor(255, 248, 220)
            border_color = QColor(30, 30, 30)
            text_color = QColor(20, 20, 20)

        gradient = QRadialGradient(x - 5, y - 5, self.PIECE_RADIUS + 10)
        gradient.setColorAt(0, QColor(255, 253, 240))
        gradient.setColorAt(1, bg_color)

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(border_color, 2))
        painter.drawEllipse(QPoint(x, y), self.PIECE_RADIUS, self.PIECE_RADIUS)

        painter.setPen(QPen(border_color, 1))
        painter.drawEllipse(
            QPoint(x, y), self.PIECE_RADIUS - 3, self.PIECE_RADIUS - 3
        )

        font = QFont("KaiTi", 22, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QPen(text_color, 1))
        painter.setBrush(QBrush(text_color))
        painter.drawText(
            QRectF(
                x - self.PIECE_RADIUS,
                y - self.PIECE_RADIUS,
                self.PIECE_RADIUS * 2,
                self.PIECE_RADIUS * 2,
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
                if self.game.move_piece(row, col):
                    self.hover_pos = None
                    self.update()
                    self.window().update_status()
                    self.window().check_game_end()
                    return

            clicked_piece = self.game.board[row][col]
            if clicked_piece and clicked_piece.color == self.game.current_player:
                self.game.select_piece(row, col)
                self.update()
                return

            self.game.selected_pos = None
            self.game.valid_moves = []
            self.update()
        else:
            if self.game.select_piece(row, col):
                self.update()

    def leaveEvent(self, event):
        self.hover_pos = None
        self.update()

    def _pixel_to_board(self, x: float, y: float) -> tuple[int, int]:
        col = round((x - self.MARGIN - 30) / self.CELL_SIZE)
        row = round((y - self.MARGIN - 30) / self.CELL_SIZE)
        return int(row), int(col)
