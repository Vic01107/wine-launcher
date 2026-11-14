"""Create Bottle Dialog - Dialog for creating new bottles"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QComboBox, QDialogButtonBox, QLabel
)
from PySide6.QtCore import Qt

from ..controllers import MainController


class CreateBottleDialog(QDialog):
    """Dialog for creating a new bottle"""

    def __init__(self, controller: MainController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Create New Bottle")
        self.setModal(True)
        self.resize(400, 350)
        self._setup_ui()
        self._load_runners()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("My Bottle")
        form.addRow("Name:", self.name_edit)

        # Description
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(80)
        self.desc_edit.setPlaceholderText("Optional description...")
        form.addRow("Description:", self.desc_edit)

        # Architecture
        self.arch_combo = QComboBox()
        self.arch_combo.addItems(["win64 (64-bit)", "win32 (32-bit)"])
        form.addRow("Architecture:", self.arch_combo)

        # Runner type
        self.runner_type_combo = QComboBox()
        self.runner_type_combo.addItems([
            "system-wine (System Wine)",
            "proton (Steam Proton)",
            "proton-ge (Proton-GE)",
            "wine-ge (Wine-GE / Lutris)",
            "custom (Custom runner)",
        ])
        form.addRow("Runner Type:", self.runner_type_combo)

        # Runner selection
        self.runner_combo = QComboBox()
        self.runner_combo.addItem("Auto-detect (Default)", None)
        form.addRow("Runner:", self.runner_combo)

        layout.addLayout(form)

        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.buttons.accepted.connect(self._validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _load_runners(self):
        """Load available runners into combo box"""
        runners = self.controller.runner_controller.list_runners()
        for runner in runners:
            display = f"{runner.name} ({runner.runner_type.value})"
            self.runner_combo.addItem(display, runner.name)

    def _validate_and_accept(self):
        """Validate input before accepting"""
        name = self.name_edit.text().strip()
        if not name:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid Name", "Please enter a bottle name")
            return
        self.accept()

    def get_data(self):
        """Get dialog data"""
        name = self.name_edit.text().strip()
        description = self.desc_edit.toPlainText().strip()
        arch = "win64" if self.arch_combo.currentIndex() == 0 else "win32"

        runner_type_map = {
            0: "system-wine",
            1: "proton",
            2: "proton-ge",
            3: "wine-ge",
            4: "custom",
        }
        runner_type = runner_type_map.get(self.runner_type_combo.currentIndex(), "system-wine")

        runner_name = self.runner_combo.currentData()
        if runner_name is None:
            runner_name = None  # Will use default

        return name, description, runner_type, arch, runner_name