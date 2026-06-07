import os
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from utils.config_manager import ConfigManager


class SoundManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.config = ConfigManager()
        self.bgm_player = QMediaPlayer()
        self.bgm_output = QAudioOutput()
        self.bgm_player.setAudioOutput(self.bgm_output)
        self.bgm_player.setLoops(QMediaPlayer.Loops.Infinite)

        self.sfx_player = QMediaPlayer()
        self.sfx_output = QAudioOutput()
        self.sfx_player.setAudioOutput(self.sfx_output)

        self._update_volumes()
        self._load_sounds()

    def _update_volumes(self):
        bgm_volume = self.config.get("bgm_volume", 50) / 100.0
        sfx_volume = self.config.get("sfx_volume", 70) / 100.0
        self.bgm_output.setVolume(bgm_volume)
        self.sfx_output.setVolume(sfx_volume)

    def _load_sounds(self):
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sounds")
        os.makedirs(assets_dir, exist_ok=True)

        self.sounds = {
            "place_piece": os.path.join(assets_dir, "place.wav"),
            "capture": os.path.join(assets_dir, "capture.wav"),
            "move": os.path.join(assets_dir, "move.wav"),
            "check": os.path.join(assets_dir, "check.wav"),
            "win": os.path.join(assets_dir, "win.wav"),
            "bgm": os.path.join(assets_dir, "bgm.mp3"),
            "click": os.path.join(assets_dir, "click.wav"),
            "undo": os.path.join(assets_dir, "undo.wav"),
        }

    def play_sfx(self, sound_name: str):
        if not self.config.get("sound_enabled", True):
            return

        sound_path = self.sounds.get(sound_name)
        if not sound_path:
            return

        if os.path.exists(sound_path):
            self._update_volumes()
            self.sfx_player.stop()
            self.sfx_player.setSource(QUrl.fromLocalFile(sound_path))
            self.sfx_player.play()
        else:
            print(f"Sound file not found: {sound_path}")

    def play_bgm(self):
        if not self.config.get("sound_enabled", True):
            return

        bgm_path = self.sounds.get("bgm")
        if bgm_path and os.path.exists(bgm_path):
            self._update_volumes()
            self.bgm_player.setSource(QUrl.fromLocalFile(bgm_path))
            self.bgm_player.play()

    def stop_bgm(self):
        self.bgm_player.stop()

    def toggle_bgm(self, play: bool):
        if play:
            self.play_bgm()
        else:
            self.stop_bgm()

    def toggle_sound(self, enabled: bool):
        self.config.set("sound_enabled", enabled)
        self.config.save_config()
        if not enabled:
            self.stop_bgm()
        else:
            self.play_bgm()

    def set_bgm_volume(self, volume: int):
        self.config.set("bgm_volume", max(0, min(100, volume)))
        self.config.save_config()
        self._update_volumes()

    def set_sfx_volume(self, volume: int):
        self.config.set("sfx_volume", max(0, min(100, volume)))
        self.config.save_config()
        self._update_volumes()

    def is_sound_enabled(self) -> bool:
        return self.config.get("sound_enabled", True)
