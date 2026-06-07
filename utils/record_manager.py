import json
import os
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any


class RecordManager:
    _instance = None
    _records_dir = os.path.join(os.path.expanduser("~"), ".chess_game", "records")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            os.makedirs(cls._records_dir, exist_ok=True)
        return cls._instance

    def save_gomoku_record(
        self,
        move_history: List[Tuple[int, int]],
        winner: str,
        player1: str = "黑棋",
        player2: str = "白棋",
        format: str = "json"
    ) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gomoku_{timestamp}"

        record_data = {
            "game_type": "gomoku",
            "timestamp": timestamp,
            "players": {
                "player1": player1,
                "player2": player2,
            },
            "winner": winner,
            "total_moves": len(move_history),
            "moves": [
                {
                    "move_num": i + 1,
                    "player": player1 if i % 2 == 0 else player2,
                    "row": move[0],
                    "col": move[1],
                }
                for i, move in enumerate(move_history)
            ]
        }

        return self._save_record(filename, record_data, format)

    def save_xiangqi_record(
        self,
        move_history: List[Tuple[Tuple[int, int], Tuple[int, int], Optional[Any]]],
        winner: str,
        player1: str = "红方",
        player2: str = "黑方",
        format: str = "json"
    ) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"xiangqi_{timestamp}"

        moves = []
        for i, move in enumerate(move_history):
            from_pos, to_pos, captured = move
            move_data = {
                "move_num": i + 1,
                "player": player1 if i % 2 == 0 else player2,
                "from": {"row": from_pos[0], "col": from_pos[1]},
                "to": {"row": to_pos[0], "col": to_pos[1]},
            }
            if captured:
                move_data["captured"] = captured.get_display_name()
            moves.append(move_data)

        record_data = {
            "game_type": "xiangqi",
            "timestamp": timestamp,
            "players": {
                "player1": player1,
                "player2": player2,
            },
            "winner": winner,
            "total_moves": len(move_history),
            "moves": moves
        }

        return self._save_record(filename, record_data, format)

    def _save_record(self, filename: str, record_data: Dict, format: str) -> str:
        if format == "json":
            filepath = os.path.join(self._records_dir, f"{filename}.json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(record_data, f, ensure_ascii=False, indent=4)
        else:
            filepath = os.path.join(self._records_dir, f"{filename}.txt")
            self._save_as_text(filepath, record_data)

        return filepath

    def _save_as_text(self, filepath: str, record_data: Dict) -> None:
        lines = []
        lines.append("=" * 50)
        lines.append(f"游戏类型: {record_data['game_type']}")
        lines.append(f"时间: {record_data['timestamp']}")
        lines.append(f"玩家1: {record_data['players']['player1']}")
        lines.append(f"玩家2: {record_data['players']['player2']}")
        lines.append(f"胜者: {record_data['winner']}")
        lines.append(f"总步数: {record_data['total_moves']}")
        lines.append("=" * 50)
        lines.append("")

        for move in record_data["moves"]:
            if "from" in move:
                line = f"第{move['move_num']:3d}步 {move['player']:4s}: ({move['from']['row']},{move['from']['col']}) -> ({move['to']['row']},{move['to']['col']})"
                if "captured" in move:
                    line += f"  吃子: {move['captured']}"
            else:
                line = f"第{move['move_num']:3d}步 {move['player']:4s}: ({move['row']},{move['col']})"
            lines.append(line)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def list_records(self, game_type: str = None) -> List[str]:
        if not os.path.exists(self._records_dir):
            return []

        files = []
        for f in os.listdir(self._records_dir):
            if f.endswith(".json") or f.endswith(".txt"):
                if game_type:
                    if f.startswith(game_type):
                        files.append(f)
                else:
                    files.append(f)

        return sorted(files, reverse=True)

    def load_record(self, filename: str) -> Optional[Dict]:
        filepath = os.path.join(self._records_dir, filename)
        if not os.path.exists(filepath):
            return None

        try:
            if filepath.endswith(".json"):
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                return None
        except (json.JSONDecodeError, IOError):
            return None

    def delete_record(self, filename: str) -> bool:
        filepath = os.path.join(self._records_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    def get_records_dir(self) -> str:
        return self._records_dir
