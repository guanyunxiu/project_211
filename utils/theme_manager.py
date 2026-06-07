from typing import Dict, Tuple
from PyQt6.QtGui import QColor

from utils.config_manager import ConfigManager


class ThemeManager:
    _instance = None

    BOARD_SKINS = {
        "wood": {
            "name": "原木棋盘",
            "bg_start": QColor(255, 248, 220),
            "bg_end": QColor(222, 184, 135),
            "border": QColor(139, 90, 43),
            "line": QColor(80, 50, 20),
            "river": QColor(173, 216, 230, 50),
            "river_text": QColor(70, 130, 180),
        },
        "jade": {
            "name": "翡翠棋盘",
            "bg_start": QColor(240, 255, 240),
            "bg_end": QColor(144, 238, 144),
            "border": QColor(34, 139, 34),
            "line": QColor(0, 100, 0),
            "river": QColor(135, 206, 250, 80),
            "river_text": QColor(25, 25, 112),
        },
        "marble": {
            "name": "大理石棋盘",
            "bg_start": QColor(245, 245, 245),
            "bg_end": QColor(169, 169, 169),
            "border": QColor(105, 105, 105),
            "line": QColor(47, 79, 79),
            "river": QColor(176, 224, 230, 100),
            "river_text": QColor(72, 61, 139),
        },
        "paper": {
            "name": "宣纸棋盘",
            "bg_start": QColor(255, 250, 240),
            "bg_end": QColor(245, 222, 179),
            "border": QColor(160, 82, 45),
            "line": QColor(101, 67, 33),
            "river": QColor(255, 218, 185, 80),
            "river_text": QColor(139, 69, 19),
        },
    }

    PIECE_SKINS = {
        "classic": {
            "name": "经典棋子",
            "black_piece": QColor(20, 20, 20),
            "black_highlight": QColor(80, 80, 80),
            "white_piece": QColor(240, 240, 240),
            "white_highlight": QColor(255, 255, 255),
            "red_bg": QColor(255, 248, 220),
            "red_border": QColor(180, 0, 0),
            "red_text": QColor(200, 0, 0),
            "black_bg": QColor(255, 248, 220),
            "black_border": QColor(30, 30, 30),
            "black_text": QColor(20, 20, 20),
        },
        "jade": {
            "name": "翡翠棋子",
            "black_piece": QColor(25, 25, 112),
            "black_highlight": QColor(65, 105, 225),
            "white_piece": QColor(255, 228, 196),
            "white_highlight": QColor(255, 250, 240),
            "red_bg": QColor(255, 240, 245),
            "red_border": QColor(178, 34, 34),
            "red_text": QColor(220, 20, 60),
            "black_bg": QColor(240, 255, 255),
            "black_border": QColor(0, 100, 0),
            "black_text": QColor(0, 128, 0),
        },
        "gold": {
            "name": "鎏金棋子",
            "black_piece": QColor(47, 79, 79),
            "black_highlight": QColor(143, 188, 143),
            "white_piece": QColor(255, 215, 0),
            "white_highlight": QColor(255, 248, 220),
            "red_bg": QColor(255, 248, 220),
            "red_border": QColor(218, 165, 32),
            "red_text": QColor(255, 69, 0),
            "black_bg": QColor(245, 245, 220),
            "black_border": QColor(72, 61, 139),
            "black_text": QColor(72, 61, 139),
        },
    }

    THEMES = {
        "classic": {
            "name": "经典主题",
            "bg_color": "#f5f0e6",
            "primary_color": "#8b5a2b",
            "secondary_color": "#7f8c8d",
            "text_color": "#4a3728",
            "accent_color": "#c0392b",
        },
        "dark": {
            "name": "深色主题",
            "bg_color": "#2c3e50",
            "primary_color": "#3498db",
            "secondary_color": "#95a5a6",
            "text_color": "#ecf0f1",
            "accent_color": "#e74c3c",
        },
        "modern": {
            "name": "现代主题",
            "bg_color": "#f8f9fa",
            "primary_color": "#007bff",
            "secondary_color": "#6c757d",
            "text_color": "#212529",
            "accent_color": "#dc3545",
        },
        "elegant": {
            "name": "优雅主题",
            "bg_color": "#fdf6e3",
            "primary_color": "#657b83",
            "secondary_color": "#93a1a1",
            "text_color": "#586e75",
            "accent_color": "#d33682",
        },
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.config = ConfigManager()
        return cls._instance

    def get_board_skin(self, skin_name: str = None) -> Dict:
        if skin_name is None:
            skin_name = self.config.get("board_skin", "wood")
        return self.BOARD_SKINS.get(skin_name, self.BOARD_SKINS["wood"])

    def get_piece_skin(self, skin_name: str = None) -> Dict:
        if skin_name is None:
            skin_name = self.config.get("piece_skin", "classic")
        return self.PIECE_SKINS.get(skin_name, self.PIECE_SKINS["classic"])

    def get_theme(self, theme_name: str = None) -> Dict:
        if theme_name is None:
            theme_name = self.config.get("theme", "classic")
        return self.THEMES.get(theme_name, self.THEMES["classic"])

    def set_board_skin(self, skin_name: str) -> None:
        if skin_name in self.BOARD_SKINS:
            self.config.set("board_skin", skin_name)
            self.config.save_config()

    def set_piece_skin(self, skin_name: str) -> None:
        if skin_name in self.PIECE_SKINS:
            self.config.set("piece_skin", skin_name)
            self.config.save_config()

    def set_theme(self, theme_name: str) -> None:
        if theme_name in self.THEMES:
            self.config.set("theme", theme_name)
            self.config.save_config()

    def get_board_skin_names(self) -> Dict[str, str]:
        return {key: value["name"] for key, value in self.BOARD_SKINS.items()}

    def get_piece_skin_names(self) -> Dict[str, str]:
        return {key: value["name"] for key, value in self.PIECE_SKINS.items()}

    def get_theme_names(self) -> Dict[str, str]:
        return {key: value["name"] for key, value in self.THEMES.items()}

    def get_global_stylesheet(self) -> str:
        theme = self.get_theme()
        return f"""
            QMainWindow {{
                background-color: {theme["bg_color"]};
            }}
            QWidget {{
                background-color: {theme["bg_color"]};
            }}
            QLabel {{
                color: {theme["text_color"]};
            }}
            QPushButton {{
                background-color: {theme["primary_color"]};
                color: white;
                border: none;
                padding: 10px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self._adjust_color(theme["primary_color"], 20)};
            }}
            QPushButton:pressed {{
                background-color: {self._adjust_color(theme["primary_color"], -20)};
            }}
            QFrame[frameShape="1"] {{
                background-color: #fff8e7;
                border: 2px solid #d4a574;
                border-radius: 8px;
            }}
        """

    def _adjust_color(self, hex_color: str, amount: int) -> str:
        color = QColor(hex_color)
        r = max(0, min(255, color.red() + amount))
        g = max(0, min(255, color.green() + amount))
        b = max(0, min(255, color.blue() + amount))
        return QColor(r, g, b).name()
