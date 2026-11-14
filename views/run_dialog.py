"""Run Dialog - Dialog for selecting app or custom executable to run"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QFileDialog, QDialogButtonBox, QRadioButton,
    QButtonGroup, QGroupBox, QFormLayout, QPushButton
)
from PySide6.QtCore import Qt


class RunDialog(QDialog):
    """Dialog for running an app or custom executable"""

    def __init__(self, apps: list, parent=None, allow_custom: bool = True):
        super().__init__(parent)
        self.apps = apps
        self.allow_custom = allow_custom
        self.setWindowTitle("Run Application")
        self.setModal(True)
        self.resize(500, 300)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Mode selection
        mode_group = QGroupBox("Run Mode")
        mode_layout = QHBoxLayout(mode_group)

        self.app_radio = QRadioButton("Installed App")
        self.app_radio.setChecked(True)
        self.app_radio.toggled.connect(self._on_mode_changed)
        mode_layout.addWidget(self.app_radio)

        self.custom_radio = QRadioButton("Custom Executable")
        self.custom_radio.setEnabled(self.allow_custom and len(self.apps) == 0)
        self.custom_radio.toggled.connect(self._on_mode_changed)
        mode_layout.addWidget(self.custom_radio)

        mode_layout.addStretch()
        layout.addWidget(mode_group)

        # App selection
        self.app_group = QGroupBox("Select App")
        app_layout = QFormLayout(self.app_group)

        self.app_combo = QComboBox()
        for app in self.apps:
            self.app_combo.addItem(f"{app['name']} ({app['exe_path']})", app['name'])
        app_layout.addRow("Application:", self.app_combo)

        layout.addWidget(self.app_group)

        # Custom executable
        self.custom_group = QGroupBox("Custom Executable")
        self.custom_group.setEnabled(False)
        custom_layout = QFormLayout(self.custom_group)

        exe_layout = QHBoxLayout()
        self.exe_edit = QLineEdit()
        self.exe_edit.setPlaceholderText("Path to .exe file")
        exe_layout.addWidget(self.exe_edit)

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_executable)
        exe_layout.addWidget(self.browse_btn)
        custom_layout.addRow("Executable:", exe_layout)

        self.args_edit = QLineEdit()
        self.args_edit.setPlaceholderText("Command line arguments")
        custom_layout.addRow("Arguments:", self.args_edit)

        self.cwd_edit = QLineEdit()
        self.cwd_edit.setPlaceholderText("Working directory (optional)")
        custom_layout.addRow("Working Dir:", self.cwd_edit)

        layout.addWidget(self.custom_group)

        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _on_mode_changed(self):
        """Handle mode radio button changes"""
        use_app = self.app_radio.isChecked()
        self.app_group.setEnabled(use_app)
        self.custom_group.setEnabled(not use_app)

    def _browse_executable(self):
        """Browse for executable file"""
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Executable", "", "Windows Executables (*.exe);;All Files (*)"
        )
        if file_path:
            self.exe_edit.setText(file_path)

    def get_selected_app(self) -> str:
        """Get selected app name"""
        return self.app_combo.currentData()

    def get_custom_executable(self):
        """Get custom executable info"""
        exe = self.exe_edit.text().strip()
        if not exe:
            return None, [], None
        args = self.args_edit.text().strip().split() if self.args_edit.text().strip() else []
        cwd = self.cwd_edit.text().strip() or None
        return exe, args, cwd