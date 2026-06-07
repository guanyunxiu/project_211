from enum import Enum
from typing import List, Optional, Tuple


class Player(Enum):
    EMPTY = 0
    BLACK = 1
    WHITE = 2


class GomokuGame:
    BOARD_SIZE = 15
    WIN_COUNT = 5

    def __init__(self):
        self.board: List[List[Player]] = []
        self.current_player: Player = Player.BLACK
        self.winner: Optional[Player] = None
        self.game_over: bool = False
        self.move_history: List[Tuple[int, int]] = []
        self._init_board()

    def _init_board(self) -> None:
        self.board = [
            [Player.EMPTY for _ in range(self.BOARD_SIZE)]
            for _ in range(self.BOARD_SIZE)
        ]

    def reset(self) -> None:
        self._init_board()
        self.current_player = Player.BLACK
        self.winner = None
        self.game_over = False
        self.move_history.clear()

    def is_valid_position(self, row: int, col: int) -> bool:
        return 0 <= row < self.BOARD_SIZE and 0 <= col < self.BOARD_SIZE

    def is_occupied(self, row: int, col: int) -> bool:
        if not self.is_valid_position(row, col):
            return False
        return self.board[row][col] != Player.EMPTY

    def place_piece(self, row: int, col: int) -> bool:
        if self.game_over or not self.is_valid_position(row, col):
            return False
        if self.is_occupied(row, col):
            return False

        self.board[row][col] = self.current_player
        self.move_history.append((row, col))

        if self._check_win(row, col):
            self.winner = self.current_player
            self.game_over = True
        elif len(self.move_history) == self.BOARD_SIZE * self.BOARD_SIZE:
            self.game_over = True
        else:
            self._switch_player()

        return True

    def _switch_player(self) -> None:
        self.current_player = Player.WHITE if self.current_player == Player.BLACK else Player.BLACK

    def _check_win(self, row: int, col: int) -> bool:
        directions = [
            (0, 1),
            (1, 0),
            (1, 1),
            (1, -1),
        ]

        player = self.board[row][col]

        for dr, dc in directions:
            count = 1

            r, c = row + dr, col + dc
            while self.is_valid_position(r, c) and self.board[r][c] == player:
                count += 1
                r += dr
                c += dc

            r, c = row - dr, col - dc
            while self.is_valid_position(r, c) and self.board[r][c] == player:
                count += 1
                r -= dr
                c -= dc

            if count >= self.WIN_COUNT:
                return True

        return False

    def get_last_move(self) -> Optional[Tuple[int, int]]:
        if self.move_history:
            return self.move_history[-1]
        return None

    def get_player_name(self, player: Player) -> str:
        if player == Player.BLACK:
            return "黑棋"
        elif player == Player.WHITE:
            return "白棋"
        return "空"
