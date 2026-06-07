from enum import Enum
from typing import List, Optional, Tuple, Dict, Any

from utils.record_manager import RecordManager


class PieceType(Enum):
    KING = "将"
    ADVISOR = "士"
    ELEPHANT = "象"
    HORSE = "马"
    CHARIOT = "车"
    CANNON = "炮"
    PAWN = "兵"


class PieceColor(Enum):
    RED = 0
    BLACK = 1


class Piece:
    def __init__(self, piece_type: PieceType, color: PieceColor):
        self.type = piece_type
        self.color = color
        self.has_moved = False

    def get_display_name(self) -> str:
        if self.color == PieceColor.RED:
            name_map = {
                PieceType.KING: "帅",
                PieceType.ADVISOR: "仕",
                PieceType.ELEPHANT: "相",
                PieceType.HORSE: "马",
                PieceType.CHARIOT: "车",
                PieceType.CANNON: "炮",
                PieceType.PAWN: "兵",
            }
        else:
            name_map = {
                PieceType.KING: "将",
                PieceType.ADVISOR: "士",
                PieceType.ELEPHANT: "象",
                PieceType.HORSE: "马",
                PieceType.CHARIOT: "车",
                PieceType.CANNON: "炮",
                PieceType.PAWN: "卒",
            }
        return name_map[self.type]

    def get_color_name(self) -> str:
        return "红方" if self.color == PieceColor.RED else "黑方"

    def copy(self) -> 'Piece':
        new_piece = Piece(self.type, self.color)
        new_piece.has_moved = self.has_moved
        return new_piece


class XiangqiGame:
    ROWS = 10
    COLS = 9
    RIVER_ROW = 4

    def __init__(self):
        self.board: List[List[Optional[Piece]]] = []
        self.current_player: PieceColor = PieceColor.RED
        self.winner: Optional[PieceColor] = None
        self.game_over: bool = False
        self.move_history: List[Tuple[Tuple[int, int], Tuple[int, int], Optional[Piece]]] = []
        self.undo_stack: List[Dict[str, Any]] = []
        self.selected_pos: Optional[Tuple[int, int]] = None
        self.valid_moves: List[Tuple[int, int]] = []
        self.is_in_check: bool = False
        self.record_manager = RecordManager()
        self._init_board()

    def _init_board(self) -> None:
        self.board = [[None for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self._place_initial_pieces()

    def _place_initial_pieces(self) -> None:
        black_back_row = [
            PieceType.CHARIOT,
            PieceType.HORSE,
            PieceType.ELEPHANT,
            PieceType.ADVISOR,
            PieceType.KING,
            PieceType.ADVISOR,
            PieceType.ELEPHANT,
            PieceType.HORSE,
            PieceType.CHARIOT,
        ]
        for col, piece_type in enumerate(black_back_row):
            self.board[0][col] = Piece(piece_type, PieceColor.BLACK)

        self.board[2][1] = Piece(PieceType.CANNON, PieceColor.BLACK)
        self.board[2][7] = Piece(PieceType.CANNON, PieceColor.BLACK)

        for col in [0, 2, 4, 6, 8]:
            self.board[3][col] = Piece(PieceType.PAWN, PieceColor.BLACK)

        red_back_row = [
            PieceType.CHARIOT,
            PieceType.HORSE,
            PieceType.ELEPHANT,
            PieceType.ADVISOR,
            PieceType.KING,
            PieceType.ADVISOR,
            PieceType.ELEPHANT,
            PieceType.HORSE,
            PieceType.CHARIOT,
        ]
        for col, piece_type in enumerate(red_back_row):
            self.board[9][col] = Piece(piece_type, PieceColor.RED)

        self.board[7][1] = Piece(PieceType.CANNON, PieceColor.RED)
        self.board[7][7] = Piece(PieceType.CANNON, PieceColor.RED)

        for col in [0, 2, 4, 6, 8]:
            self.board[6][col] = Piece(PieceType.PAWN, PieceColor.RED)

    def reset(self) -> None:
        self._init_board()
        self.current_player = PieceColor.RED
        self.winner = None
        self.game_over = False
        self.move_history.clear()
        self.undo_stack.clear()
        self.selected_pos = None
        self.valid_moves = []
        self.is_in_check = False

    def can_undo(self) -> bool:
        return len(self.move_history) > 0

    def _save_state(self) -> None:
        state = {
            "board": [[piece.copy() if piece else None for piece in row] for row in self.board],
            "current_player": self.current_player,
            "winner": self.winner,
            "game_over": self.game_over,
            "is_in_check": self.is_in_check,
        }
        self.undo_stack.append(state)

    def undo(self) -> bool:
        if not self.can_undo() or not self.undo_stack:
            return False

        state = self.undo_stack.pop()
        self.board = state["board"]
        self.current_player = state["current_player"]
        self.winner = state["winner"]
        self.game_over = state["game_over"]
        self.is_in_check = state["is_in_check"]
        self.move_history.pop()
        self.selected_pos = None
        self.valid_moves = []

        return True

    def is_valid_position(self, row: int, col: int) -> bool:
        return 0 <= row < self.ROWS and 0 <= col < self.COLS

    def is_in_palace(self, row: int, col: int, color: PieceColor) -> bool:
        if color == PieceColor.RED:
            return 7 <= row <= 9 and 3 <= col <= 5
        else:
            return 0 <= row <= 2 and 3 <= col <= 5

    def has_crossed_river(self, row: int, color: PieceColor) -> bool:
        if color == PieceColor.RED:
            return row <= self.RIVER_ROW
        else:
            return row > self.RIVER_ROW

    def _get_valid_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        piece = self.board[row][col]
        if not piece:
            return []

        moves = []
        piece_type = piece.type
        color = piece.color

        if piece_type == PieceType.KING:
            moves = self._get_king_moves(row, col, color)
        elif piece_type == PieceType.ADVISOR:
            moves = self._get_advisor_moves(row, col, color)
        elif piece_type == PieceType.ELEPHANT:
            moves = self._get_elephant_moves(row, col, color)
        elif piece_type == PieceType.HORSE:
            moves = self._get_horse_moves(row, col, color)
        elif piece_type == PieceType.CHARIOT:
            moves = self._get_chariot_moves(row, col, color)
        elif piece_type == PieceType.CANNON:
            moves = self._get_cannon_moves(row, col, color)
        elif piece_type == PieceType.PAWN:
            moves = self._get_pawn_moves(row, col, color)

        valid_moves = []
        for r, c in moves:
            if self._is_move_legal(row, col, r, c, color):
                valid_moves.append((r, c))

        return valid_moves

    def _get_king_moves(self, row: int, col: int, color: PieceColor) -> List[Tuple[int, int]]:
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if self.is_in_palace(nr, nc, color):
                target = self.board[nr][nc]
                if not target or target.color != color:
                    moves.append((nr, nc))
        return moves

    def _get_advisor_moves(self, row: int, col: int, color: PieceColor) -> List[Tuple[int, int]]:
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if self.is_in_palace(nr, nc, color):
                target = self.board[nr][nc]
                if not target or target.color != color:
                    moves.append((nr, nc))
        return moves

    def _get_elephant_moves(self, row: int, col: int, color: PieceColor) -> List[Tuple[int, int]]:
        moves = []
        directions = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        block_directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for (dr, dc), (br, bc) in zip(directions, block_directions):
            nr, nc = row + dr, col + dc
            if not self.is_valid_position(nr, nc):
                continue
            if self.has_crossed_river(nr, color):
                continue
            block_r, block_c = row + br, col + bc
            if self.board[block_r][block_c]:
                continue
            target = self.board[nr][nc]
            if not target or target.color != color:
                moves.append((nr, nc))
        return moves

    def _get_horse_moves(self, row: int, col: int, color: PieceColor) -> List[Tuple[int, int]]:
        moves = []
        directions = [
            (-2, -1, -1, 0),
            (-2, 1, -1, 0),
            (2, -1, 1, 0),
            (2, 1, 1, 0),
            (-1, -2, 0, -1),
            (1, -2, 0, -1),
            (-1, 2, 0, 1),
            (1, 2, 0, 1),
        ]
        for dr, dc, br, bc in directions:
            nr, nc = row + dr, col + dc
            if not self.is_valid_position(nr, nc):
                continue
            block_r, block_c = row + br, col + bc
            if self.board[block_r][block_c]:
                continue
            target = self.board[nr][nc]
            if not target or target.color != color:
                moves.append((nr, nc))
        return moves

    def _get_chariot_moves(self, row: int, col: int, color: PieceColor) -> List[Tuple[int, int]]:
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            while self.is_valid_position(nr, nc):
                target = self.board[nr][nc]
                if not target:
                    moves.append((nr, nc))
                else:
                    if target.color != color:
                        moves.append((nr, nc))
                    break
                nr += dr
                nc += dc
        return moves

    def _get_cannon_moves(self, row: int, col: int, color: PieceColor) -> List[Tuple[int, int]]:
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            jumped = False
            while self.is_valid_position(nr, nc):
                target = self.board[nr][nc]
                if not jumped:
                    if not target:
                        moves.append((nr, nc))
                    else:
                        jumped = True
                else:
                    if target:
                        if target.color != color:
                            moves.append((nr, nc))
                        break
                nr += dr
                nc += dc
        return moves

    def _get_pawn_moves(self, row: int, col: int, color: PieceColor) -> List[Tuple[int, int]]:
        moves = []
        if color == PieceColor.RED:
            forward = -1
        else:
            forward = 1

        nr, nc = row + forward, col
        if self.is_valid_position(nr, nc):
            target = self.board[nr][nc]
            if not target or target.color != color:
                moves.append((nr, nc))

        if self.has_crossed_river(row, color):
            for dc in [-1, 1]:
                nr, nc = row, col + dc
                if self.is_valid_position(nr, nc):
                    target = self.board[nr][nc]
                    if not target or target.color != color:
                        moves.append((nr, nc))

        return moves

    def _is_move_legal(self, from_row: int, from_col: int, to_row: int, to_col: int, color: PieceColor) -> bool:
        temp_board = [[piece.copy() if piece else None for piece in row] for row in self.board]

        moving_piece = temp_board[from_row][from_col]
        temp_board[to_row][to_col] = moving_piece
        temp_board[from_row][from_col] = None

        if self._is_king_in_check(temp_board, color):
            return False

        if moving_piece and moving_piece.type == PieceType.KING:
            if self._is_king_facing_king(temp_board, color):
                return False

        return True

    def _find_king(self, board: List[List[Optional[Piece]]], color: PieceColor) -> Optional[Tuple[int, int]]:
        for row in range(self.ROWS):
            for col in range(self.COLS):
                piece = board[row][col]
                if piece and piece.type == PieceType.KING and piece.color == color:
                    return (row, col)
        return None

    def _is_king_facing_king(self, board: List[List[Optional[Piece]]], color: PieceColor) -> bool:
        king_pos = self._find_king(board, color)
        if not king_pos:
            return False
        kr, kc = king_pos

        opponent_color = PieceColor.BLACK if color == PieceColor.RED else PieceColor.RED
        opp_king_pos = self._find_king(board, opponent_color)
        if not opp_king_pos:
            return False

        okr, okc = opp_king_pos

        if kc != okc:
            return False

        min_row = min(kr, okr)
        max_row = max(kr, okr)
        for row in range(min_row + 1, max_row):
            if board[row][kc]:
                return False

        return True

    def _is_king_in_check(self, board: List[List[Optional[Piece]]], color: PieceColor) -> bool:
        king_pos = self._find_king(board, color)
        if not king_pos:
            return True

        kr, kc = king_pos
        opponent_color = PieceColor.BLACK if color == PieceColor.RED else PieceColor.RED

        for row in range(self.ROWS):
            for col in range(self.COLS):
                piece = board[row][col]
                if piece and piece.color == opponent_color:
                    if self._can_piece_attack(board, row, col, kr, kc, opponent_color):
                        return True

        return False

    def _can_piece_attack(self, board: List[List[Optional[Piece]]], row: int, col: int, target_row: int, target_col: int, color: PieceColor) -> bool:
        piece = board[row][col]
        if not piece:
            return False

        piece_type = piece.type
        dr = target_row - row
        dc = target_col - col

        if piece_type == PieceType.KING:
            if (abs(dr) == 1 and dc == 0) or (abs(dc) == 1 and dr == 0):
                return self.is_in_palace(target_row, target_col, color)

        elif piece_type == PieceType.ADVISOR:
            if abs(dr) == 1 and abs(dc) == 1:
                return self.is_in_palace(target_row, target_col, color)

        elif piece_type == PieceType.ELEPHANT:
            if abs(dr) == 2 and abs(dc) == 2:
                if self.has_crossed_river(target_row, color):
                    return False
                block_r = row + dr // 2
                block_c = col + dc // 2
                return not board[block_r][block_c]

        elif piece_type == PieceType.HORSE:
            if (abs(dr) == 2 and abs(dc) == 1) or (abs(dr) == 1 and abs(dc) == 2):
                if abs(dr) == 2:
                    block_r = row + dr // 2
                    block_c = col
                else:
                    block_r = row
                    block_c = col + dc // 2
                return not board[block_r][block_c]

        elif piece_type == PieceType.CHARIOT:
            if dr == 0 or dc == 0:
                if dr == 0:
                    step = 1 if dc > 0 else -1
                    for c in range(col + step, target_col, step):
                        if board[row][c]:
                            return False
                else:
                    step = 1 if dr > 0 else -1
                    for r in range(row + step, target_row, step):
                        if board[r][col]:
                            return False
                return True

        elif piece_type == PieceType.CANNON:
            if dr == 0 or dc == 0:
                count = 0
                if dr == 0:
                    step = 1 if dc > 0 else -1
                    for c in range(col + step, target_col, step):
                        if board[row][c]:
                            count += 1
                else:
                    step = 1 if dr > 0 else -1
                    for r in range(row + step, target_row, step):
                        if board[r][col]:
                            count += 1
                target = board[target_row][target_col]
                if target:
                    return count == 1
                else:
                    return count == 0

        elif piece_type == PieceType.PAWN:
            if color == PieceColor.RED:
                forward = -1
            else:
                forward = 1

            if dr == forward and dc == 0:
                return True
            if self.has_crossed_river(row, color) and dr == 0 and abs(dc) == 1:
                return True

        return False

    def _is_king_facing_king_check(self) -> bool:
        return self._is_king_facing_king(self.board, self.current_player)

    def select_piece(self, row: int, col: int) -> bool:
        if self.game_over:
            return False

        piece = self.board[row][col]
        if piece and piece.color == self.current_player:
            self.selected_pos = (row, col)
            self.valid_moves = self._get_valid_moves(row, col)
            return True
        return False

    def move_piece(self, to_row: int, to_col: int) -> bool:
        if self.game_over or not self.selected_pos:
            return False

        from_row, from_col = self.selected_pos
        if (to_row, to_col) not in self.valid_moves:
            return False

        piece = self.board[from_row][from_col]
        if not piece:
            return False

        captured_piece = self.board[to_row][to_col]

        self._save_state()

        self.move_history.append(((from_row, from_col), (to_row, to_col), captured_piece))

        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        piece.has_moved = True

        if captured_piece and captured_piece.type == PieceType.KING:
            self.winner = self.current_player
            self.game_over = True

        opponent_color = self._get_opponent_color()
        self.is_in_check = self._is_king_in_check(self.board, opponent_color)
        if self.is_in_check:
            if not self._has_legal_moves(opponent_color):
                self.winner = self.current_player
                self.game_over = True

        self.selected_pos = None
        self.valid_moves = []

        if not self.game_over:
            self._switch_player()

        return True

    def save_record(self, format: str = "json") -> Optional[str]:
        if not self.move_history:
            return None

        winner_name = "平局"
        if self.winner is not None:
            winner_name = self.get_player_name(self.winner)

        return self.record_manager.save_xiangqi_record(
            self.move_history,
            winner_name,
            self.get_player_name(PieceColor.RED),
            self.get_player_name(PieceColor.BLACK),
            format
        )

    def _get_opponent_color(self) -> PieceColor:
        return PieceColor.BLACK if self.current_player == PieceColor.RED else PieceColor.RED

    def _has_legal_moves(self, color: PieceColor) -> bool:
        for row in range(self.ROWS):
            for col in range(self.COLS):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    moves = self._get_valid_moves(row, col)
                    if moves:
                        return True
        return False

    def _switch_player(self) -> None:
        self.current_player = self._get_opponent_color()

    def get_player_name(self, color: PieceColor) -> str:
        return "红方" if color == PieceColor.RED else "黑方"

    def get_current_player_name(self) -> str:
        return self.get_player_name(self.current_player)
