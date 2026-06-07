import json
import os
from typing import Any, Dict


class ConfigManager:
    _instance = None
    _config: Dict[str, Any] = {}
    _config_dir = os.path.join(os.path.expanduser("~"), ".chess_game")
    _config_file = os.path.join(_config_dir, "config.json")

    DEFAULT_CONFIG = {
        "theme": "classic",
        "board_skin": "wood",
        "piece_skin": "classic",
        "sound_enabled": True,
        "bgm_volume": 50,
        "sfx_volume": 70,
        "timer_enabled": True,
        "timer_minutes": 10,
        "fullscreen": False,
        "window_size": [1000, 800],
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self) -> None:
        if not os.path.exists(self._config_dir):
            os.makedirs(self._config_dir, exist_ok=True)

        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._config = self.DEFAULT_CONFIG.copy()
        else:
            self._config = self.DEFAULT_CONFIG.copy()

        for key, value in self.DEFAULT_CONFIG.items():
            if key not in self._config:
                self._config[key] = value

    def save_config(self) -> None:
        try:
            if not os.path.exists(self._config_dir):
                os.makedirs(self._config_dir, exist_ok=True)
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default if default is not None else self.DEFAULT_CONFIG.get(key))

    def set(self, key: str, value: Any) -> None:
        self._config[key] = value

    def get_all(self) -> Dict[str, Any]:
        return self._config.copy()

    def reset_to_defaults(self) -> None:
        self._config = self.DEFAULT_CONFIG.copy()
        self.save_config()
