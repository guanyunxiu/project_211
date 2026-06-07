from PyQt6.QtCore import QTimer, pyqtSignal, QObject

from utils.config_manager import ConfigManager


class GameTimer(QObject):
    time_updated = pyqtSignal(str, str)
    time_out = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timeout)
        self.timer.setInterval(1000)

        self.total_time = 0
        self.player1_time = 0
        self.player2_time = 0
        self.current_player = 1
        self.is_running = False

    def start(self, minutes: int = None):
        if minutes is None:
            minutes = self.config.get("timer_minutes", 10)

        total_seconds = minutes * 60
        self.player1_time = total_seconds
        self.player2_time = total_seconds
        self.total_time = total_seconds
        self.current_player = 1
        self.is_running = True
        self.timer.start()
        self._emit_time()

    def pause(self):
        self.is_running = False
        self.timer.stop()

    def resume(self):
        if self.total_time > 0:
            self.is_running = True
            self.timer.start()

    def stop(self):
        self.is_running = False
        self.timer.stop()

    def switch_player(self):
        if self.current_player == 1:
            self.current_player = 2
        else:
            self.current_player = 1

    def reset(self, minutes: int = None):
        self.stop()
        self.start(minutes)

    def _on_timeout(self):
        if not self.is_running:
            return

        if self.current_player == 1:
            self.player1_time -= 1
            if self.player1_time <= 0:
                self.player1_time = 0
                self._emit_time()
                self.timer.stop()
                self.time_out.emit("player1")
                return
        else:
            self.player2_time -= 1
            if self.player2_time <= 0:
                self.player2_time = 0
                self._emit_time()
                self.timer.stop()
                self.time_out.emit("player2")
                return

        self._emit_time()

    def _emit_time(self):
        self.time_updated.emit(
            self._format_time(self.player1_time),
            self._format_time(self.player2_time)
        )

    def _format_time(self, seconds: int) -> str:
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def get_player1_time(self) -> str:
        return self._format_time(self.player1_time)

    def get_player2_time(self) -> str:
        return self._format_time(self.player2_time)

    def is_enabled(self) -> bool:
        return self.config.get("timer_enabled", True)

    def set_timer_enabled(self, enabled: bool):
        self.config.set("timer_enabled", enabled)
        self.config.save_config()
        if not enabled:
            self.stop()

    def set_timer_minutes(self, minutes: int):
        self.config.set("timer_minutes", max(1, min(60, minutes)))
        self.config.save_config()
