"""Settings Dialog - Application settings configuration"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QFormLayout,
    QLineEdit, QCheckBox, QComboBox, QDialogButtonBox,
    QFileDialog, QMessageBox, QPushButton, QHBoxLayout,
    QSpinBox, QLabel
)
from PySide6.QtCore import Qt
from pathlib import Path

from ..controllers import MainController
from ..models import AppConfig


class SettingsDialog(QDialog):
    """Application settings dialog"""

    def __init__(self, controller: MainController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.config = controller.config
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(550, 450)
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self._create_general_tab()
        self._create_appearance_tab()
        self._create_advanced_tab()

        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        self.buttons.accepted.connect(self._save_and_accept)
        self.buttons.rejected.connect(self.reject)
        self.buttons.button(QDialogButtonBox.Apply).clicked.connect(self._apply_settings)
        layout.addWidget(self.buttons)

    def _create_general_tab(self):
        """General paths tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setLabelAlignment(Qt.AlignRight)

        # Config directory
        self.config_dir = QLineEdit()
        self.config_dir.setReadOnly(True)
        browse_config = QPushButton("Browse...")
        browse_config.clicked.connect(lambda: self._browse_dir(self.config_dir))
        config_layout = QHBoxLayout()
        config_layout.addWidget(self.config_dir)
        config_layout.addWidget(browse_config)
        layout.addRow("Config Directory:", config_layout)

        # Bottles directory
        self.bottles_dir = QLineEdit()
        browse_bottles = QPushButton("Browse...")
        browse_bottles.clicked.connect(lambda: self._browse_dir(self.bottles_dir))
        bottles_layout = QHBoxLayout()
        bottles_layout.addWidget(self.bottles_dir)
        bottles_layout.addWidget(browse_bottles)
        layout.addRow("Bottles Directory:", bottles_layout)

        # Runners directory
        self.runners_dir = QLineEdit()
        browse_runners = QPushButton("Browse...")
        browse_runners.clicked.connect(lambda: self._browse_dir(self.runners_dir))
        runners_layout = QHBoxLayout()
        runners_layout.addWidget(self.runners_dir)
        runners_layout.addWidget(browse_runners)
        layout.addRow("Runners Directory:", runners_layout)

        # Backups directory
        self.backups_dir = QLineEdit()
        browse_backups = QPushButton("Browse...")
        browse_backups.clicked.connect(lambda: self._browse_dir(self.backups_dir))
        backups_layout = QHBoxLayout()
        backups_layout.addWidget(self.backups_dir)
        backups_layout.addWidget(browse_backups)
        layout.addRow("Backups Directory:", backups_layout)

        # Default runner
        self.default_runner = QComboBox()
        self.default_runner.addItem("Auto-detect", "")
        runners = self.controller.runner_controller.list_runners()
        for runner in runners:
            self.default_runner.addItem(f"{runner.name} ({runner.runner_type.value})", runner.name)
        layout.addRow("Default Runner:", self.default_runner)

        # Default architecture
        self.default_arch = QComboBox()
        self.default_arch.addItems(["win64", "win32"])
        layout.addRow("Default Architecture:", self.default_arch)

        self.tabs.addTab(widget, "General")

    def _create_appearance_tab(self):
        """Appearance tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setLabelAlignment(Qt.AlignRight)

        # Theme
        self.theme = QComboBox()
        self.theme.addItems(["System", "Light", "Dark"])
        layout.addRow("Theme:", self.theme)

        # Language
        self.language = QComboBox()
        self.language.addItems(["English", "Spanish", "French", "German", "Chinese", "Japanese"])
        layout.addRow("Language:", self.language)

        # Show status bar
        self.show_statusbar = QCheckBox()
        layout.addRow("Show Status Bar:", self.show_statusbar)

        # Show tooltips
        self.show_tooltips = QCheckBox()
        layout.addRow("Show Tooltips:", self.show_tooltips)

        # Window geometry
        self.remember_geometry = QCheckBox()
        layout.addRow("Remember Window Size/Position:", self.remember_geometry)

        # Font size
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setSuffix(" pt")
        layout.addRow("UI Font Size:", self.font_size)

        self.tabs.addTab(widget, "Appearance")

    def _create_advanced_tab(self):
        """Advanced settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setLabelAlignment(Qt.AlignRight)

        # Auto-refresh interval
        self.auto_refresh = QSpinBox()
        self.auto_refresh.setRange(0, 3600)
        self.auto_refresh.setSuffix(" sec (0 = disabled)")
        layout.addRow("Auto Refresh Interval:", self.auto_refresh)

        # Max log lines
        self.max_log_lines = QSpinBox()
        self.max_log_lines.setRange(100, 10000)
        self.max_log_lines.setSingleStep(100)
        layout.addRow("Max Log Lines:", self.max_log_lines)

        # Confirm on delete
        self.confirm_delete = QCheckBox()
        layout.addRow("Confirm Before Deleting:", self.confirm_delete)

        # Close to tray
        self.close_to_tray = QCheckBox()
        layout.addRow("Minimize to Tray on Close:", self.close_to_tray)

        # Start minimized
        self.start_minimized = QCheckBox()
        layout.addRow("Start Minimized:", self.start_minimized)

        # Wine debug
        self.wine_debug = QCheckBox()
        layout.addRow("Enable Wine Debug Output:", self.wine_debug)

        # Reset button
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self._reset_defaults)
        layout.addRow("", reset_btn)

        self.tabs.addTab(widget, "Advanced")

    def _browse_dir(self, line_edit: QLineEdit):
        """Browse for directory"""
        current = line_edit.text() or str(Path.home())
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory", current)
        if dir_path:
            line_edit.setText(dir_path)

    def _load_settings(self):
        """Load settings from config"""
        self.config_dir.setText(str(self.config.config_dir))
        self.bottles_dir.setText(str(self.config.bottles_dir))
        self.runners_dir.setText(str(self.config.runners_dir))
        self.backups_dir.setText(str(self.config.backups_dir))

        # Load defaults from config
        if self.config.default_runner:
            idx = self.default_runner.findData(self.config.default_runner)
            if idx >= 0:
                self.default_runner.setCurrentIndex(idx)

        self.default_arch.setCurrentText(self.config.default_arch)

        # Appearance
        self.theme.setCurrentText(self.config.ui_theme)
        self.show_statusbar.setChecked(self.config.show_statusbar)
        self.show_tooltips.setChecked(self.config.show_tooltips)
        self.remember_geometry.setChecked(self.config.remember_geometry)
        self.font_size.setValue(self.config.font_size)

        # Advanced
        self.auto_refresh.setValue(self.config.auto_refresh_interval)
        self.max_log_lines.setValue(self.config.max_log_lines)
        self.confirm_delete.setChecked(self.config.confirm_delete)
        self.close_to_tray.setChecked(self.config.close_to_tray)
        self.start_minimized.setChecked(self.config.start_minimized)
        self.wine_debug.setChecked(self.config.wine_debug)

    def _apply_settings(self):
        """Apply settings without closing"""
        self._save_settings()
        QMessageBox.information(self, "Settings", "Settings applied")

    def _save_and_accept(self):
        """Save settings and close"""
        if self._save_settings():
            self.accept()

    def _save_settings(self) -> bool:
        """Save settings to config"""
        # Validate directories
        bottles_path = Path(self.bottles_dir.text().strip())
        if not bottles_path.exists():
            try:
                bottles_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Cannot create bottles directory: {e}")
                return False

        runners_path = Path(self.runners_dir.text().strip())
        if not runners_path.exists():
            try:
                runners_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Cannot create runners directory: {e}")
                return False

        backups_path = Path(self.backups_dir.text().strip())
        if not backups_path.exists():
            try:
                backups_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Cannot create backups directory: {e}")
                return False

        # Save to config
        self.config.bottles_dir = bottles_path
        self.config.runners_dir = runners_path
        self.config.backups_dir = backups_path
        self.config.default_runner = self.default_runner.currentData() or None
        self.config.default_arch = self.default_arch.currentText()

        self.config.ui_theme = self.theme.currentText()
        self.config.show_statusbar = self.show_statusbar.isChecked()
        self.config.show_tooltips = self.show_tooltips.isChecked()
        self.config.remember_geometry = self.remember_geometry.isChecked()
        self.config.font_size = self.font_size.value()

        self.config.auto_refresh_interval = self.auto_refresh.value()
        self.config.max_log_lines = self.max_log_lines.value()
        self.config.confirm_delete = self.confirm_delete.isChecked()
        self.config.close_to_tray = self.close_to_tray.isChecked()
        self.config.start_minimized = self.start_minimized.isChecked()
        self.config.wine_debug = self.wine_debug.isChecked()

        self.config.save()
        return True

    def _reset_defaults(self):
        """Reset to default settings"""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.config = AppConfig.get_default()
            self.controller.config = self.config
            self._load_settings()