from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QCheckBox,
    QSlider,
    QTabWidget,
    QGroupBox,
    QFormLayout,
    QSpinBox,
    QDialogButtonBox,
)

from utils.config_manager import ConfigManager
from utils.theme_manager import ThemeManager
from utils.sound_manager import SoundManager
from utils.timer_manager import GameTimer


class SettingsDialog(QDialog):
    settings_applied = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("游戏设置")
        self.setMinimumSize(500, 400)
        self.config = ConfigManager()
        self.theme_manager = ThemeManager()
        self.sound_manager = SoundManager()
        self.timer_manager = GameTimer()
        self._init_ui()
        self._load_settings()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self._create_ui_tab(), "界面设置")
        self.tab_widget.addTab(self._create_sound_tab(), "声音设置")
        self.tab_widget.addTab(self._create_game_tab(), "游戏设置")
        main_layout.addWidget(self.tab_widget)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Apply
            | QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self._apply_settings)
        button_box.button(QDialogButtonBox.StandardButton.Ok).clicked.connect(self._on_ok)
        button_box.button(QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.reject)
        main_layout.addWidget(button_box)

        self.setStyleSheet("""
            QDialog {
                background-color: #f5f0e6;
            }
            QTabWidget::pane {
                border: 2px solid #d4a574;
                border-radius: 8px;
                background-color: #fff8e7;
            }
            QTabBar::tab {
                background-color: #deb887;
                color: #4a3728;
                padding: 10px 20px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #8b5a2b;
                color: white;
            }
            QGroupBox {
                border: 2px solid #d4a574;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                font-weight: bold;
                color: #4a3728;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #4a3728;
            }
            QComboBox {
                padding: 8px;
                border: 2px solid #d4a574;
                border-radius: 6px;
                background-color: white;
                color: #4a3728;
            }
            QComboBox:hover {
                border-color: #8b5a2b;
            }
            QCheckBox {
                color: #4a3728;
                spacing: 8px;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #d4a574;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                width: 18px;
                height: 18px;
                background: #8b5a2b;
                border-radius: 9px;
                margin: -5px 0;
            }
            QSlider::sub-page:horizontal {
                background: #8b5a2b;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #8b5a2b;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a06230;
            }
            QPushButton:pressed {
                background-color: #6b4423;
            }
            QSpinBox {
                padding: 6px;
                border: 2px solid #d4a574;
                border-radius: 6px;
                background-color: white;
                color: #4a3728;
            }
        """)

    def _create_ui_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        theme_group = QGroupBox("主题设置")
        theme_layout = QFormLayout(theme_group)

        self.theme_combo = QComboBox()
        for key, name in self.theme_manager.get_theme_names().items():
            self.theme_combo.addItem(name, key)
        theme_layout.addRow("整体主题:", self.theme_combo)

        self.board_combo = QComboBox()
        for key, name in self.theme_manager.get_board_skin_names().items():
            self.board_combo.addItem(name, key)
        theme_layout.addRow("棋盘皮肤:", self.board_combo)

        self.piece_combo = QComboBox()
        for key, name in self.theme_manager.get_piece_skin_names().items():
            self.piece_combo.addItem(name, key)
        theme_layout.addRow("棋子皮肤:", self.piece_combo)

        layout.addWidget(theme_group)
        layout.addStretch()
        return widget

    def _create_sound_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        sound_group = QGroupBox("声音设置")
        sound_layout = QFormLayout(sound_group)

        self.sound_enabled = QCheckBox("启用声音")
        self.sound_enabled.toggled.connect(self._on_sound_toggled)
        sound_layout.addRow(self.sound_enabled)

        bgm_label = QLabel("背景音乐:")
        self.bgm_slider = QSlider(Qt.Orientation.Horizontal)
        self.bgm_slider.setRange(0, 100)
        self.bgm_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.bgm_slider.setTickInterval(10)
        self.bgm_value = QLabel("50%")
        self.bgm_slider.valueChanged.connect(lambda v: self.bgm_value.setText(f"{v}%"))
        bgm_layout = QHBoxLayout()
        bgm_layout.addWidget(self.bgm_slider)
        bgm_layout.addWidget(self.bgm_value)
        sound_layout.addRow(bgm_label, bgm_layout)

        sfx_label = QLabel("音效音量:")
        self.sfx_slider = QSlider(Qt.Orientation.Horizontal)
        self.sfx_slider.setRange(0, 100)
        self.sfx_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.sfx_slider.setTickInterval(10)
        self.sfx_value = QLabel("70%")
        self.sfx_slider.valueChanged.connect(lambda v: self.sfx_value.setText(f"{v}%"))
        sfx_layout = QHBoxLayout()
        sfx_layout.addWidget(self.sfx_slider)
        sfx_layout.addWidget(self.sfx_value)
        sound_layout.addRow(sfx_label, sfx_layout)

        test_sound_btn = QPushButton("🔊 测试音效")
        test_sound_btn.clicked.connect(lambda: self.sound_manager.play_sfx("click"))
        sound_layout.addRow("", test_sound_btn)

        layout.addWidget(sound_group)
        layout.addStretch()
        return widget

    def _create_game_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        timer_group = QGroupBox("计时设置")
        timer_layout = QFormLayout(timer_group)

        self.timer_enabled = QCheckBox("启用游戏计时")
        self.timer_enabled.toggled.connect(self._on_timer_toggled)
        timer_layout.addRow(self.timer_enabled)

        self.timer_minutes = QSpinBox()
        self.timer_minutes.setRange(1, 60)
        self.timer_minutes.setSuffix(" 分钟")
        timer_layout.addRow("每方时间:", self.timer_minutes)

        layout.addWidget(timer_group)

        display_group = QGroupBox("显示设置")
        display_layout = QFormLayout(display_group)

        self.fullscreen_check = QCheckBox("启动时全屏")
        display_layout.addRow(self.fullscreen_check)

        self.show_last_move = QCheckBox("显示最后落子标记")
        self.show_last_move.setChecked(True)
        display_layout.addRow(self.show_last_move)

        self.show_valid_moves = QCheckBox("显示可移动点位")
        self.show_valid_moves.setChecked(True)
        display_layout.addRow(self.show_valid_moves)

        layout.addWidget(display_group)
        layout.addStretch()
        return widget

    def _load_settings(self):
        theme = self.config.get("theme", "classic")
        board_skin = self.config.get("board_skin", "wood")
        piece_skin = self.config.get("piece_skin", "classic")

        index = self.theme_combo.findData(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

        index = self.board_combo.findData(board_skin)
        if index >= 0:
            self.board_combo.setCurrentIndex(index)

        index = self.piece_combo.findData(piece_skin)
        if index >= 0:
            self.piece_combo.setCurrentIndex(index)

        self.sound_enabled.setChecked(self.config.get("sound_enabled", True))
        self.bgm_slider.setValue(self.config.get("bgm_volume", 50))
        self.sfx_slider.setValue(self.config.get("sfx_volume", 70))

        self.timer_enabled.setChecked(self.config.get("timer_enabled", True))
        self.timer_minutes.setValue(self.config.get("timer_minutes", 10))

        self.fullscreen_check.setChecked(self.config.get("fullscreen", False))
        self.show_last_move.setChecked(self.config.get("show_last_move", True))
        self.show_valid_moves.setChecked(self.config.get("show_valid_moves", True))

        self._on_sound_toggled(self.sound_enabled.isChecked())
        self._on_timer_toggled(self.timer_enabled.isChecked())

    def _on_sound_toggled(self, enabled: bool):
        self.bgm_slider.setEnabled(enabled)
        self.sfx_slider.setEnabled(enabled)

    def _on_timer_toggled(self, enabled: bool):
        self.timer_minutes.setEnabled(enabled)

    def _apply_settings(self):
        self.theme_manager.set_theme(self.theme_combo.currentData())
        self.theme_manager.set_board_skin(self.board_combo.currentData())
        self.theme_manager.set_piece_skin(self.piece_combo.currentData())

        self.sound_manager.toggle_sound(self.sound_enabled.isChecked())
        self.sound_manager.set_bgm_volume(self.bgm_slider.value())
        self.sound_manager.set_sfx_volume(self.sfx_slider.value())

        self.timer_manager.set_timer_enabled(self.timer_enabled.isChecked())
        self.timer_manager.set_timer_minutes(self.timer_minutes.value())

        self.config.set("fullscreen", self.fullscreen_check.isChecked())
        self.config.set("show_last_move", self.show_last_move.isChecked())
        self.config.set("show_valid_moves", self.show_valid_moves.isChecked())
        self.config.save_config()

        self.settings_applied.emit()

    def _on_ok(self):
        self._apply_settings()
        self.accept()
