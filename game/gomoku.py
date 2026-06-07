from enum import Enum
from typing import List, Optional, Tuple, Dict, Any

from utils.record_manager import RecordManager


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
        self.undo_stack: List[Dict[str, Any]] = []
        self.record_manager = RecordManager()
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
        self.undo_stack.clear()

    def can_undo(self) -> bool:
        return len(self.move_history) > 0

    def undo(self) -> bool:
        if not self.can_undo():
            return False

        if self.undo_stack:
            state = self.undo_stack.pop()
            self.board = state["board"]
            self.current_player = state["current_player"]
            self.winner = state["winner"]
            self.game_over = state["game_over"]
            self.move_history.pop()
            return True
        return False

    def _save_state(self) -> None:
        state = {
            "board": [row[:] for row in self.board],
            "current_player": self.current_player,
            "winner": self.winner,
            "game_over": self.game_over,
        }
        self.undo_stack.append(state)

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

        self._save_state()

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

    def save_record(self, format: str = "json") -> Optional[str]:
        if not self.move_history:
            return None

        winner_name = "平局"
        if self.winner:
            winner_name = self.get_player_name(self.winner)

        return self.record_manager.save_gomoku_record(
            self.move_history,
            winner_name,
            self.get_player_name(Player.BLACK),
            self.get_player_name(Player.WHITE),
            format
        )
