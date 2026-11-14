"""Bottle Detail Widget - Detailed view of a bottle with tabs"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QScrollArea,
    QLabel, QPushButton, QHBoxLayout, QFormLayout,
    QLineEdit, QCheckBox, QTextEdit, QListWidget, QListWidgetItem,
    QMessageBox, QInputDialog, QDialog, QFileDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ..controllers import MainController
from ..models import Bottle, BottleStatus, PrefixArch


class BottleDetailWidget(QWidget):
    """Widget showing detailed bottle information with tabs"""

    run_app_requested = Signal()
    run_exe_requested = Signal()
    winetricks_requested = Signal()

    def __init__(self, controller: MainController):
        super().__init__()
        self.controller = controller
        self.current_bottle_name = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Create tabs
        self._create_general_tab()
        self._create_apps_tab()
        self._create_config_tab()
        self._create_winetricks_tab()
        self._create_env_tab()

        # Initially disabled
        self.tab_widget.setEnabled(False)

    def _create_general_tab(self):
        """General info tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QFormLayout(content)
        layout.setLabelAlignment(Qt.AlignRight)

        # Name
        self.name_label = QLabel()
        layout.addRow("Name:", self.name_label)

        # Description
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(80)
        self.desc_edit.textChanged.connect(self._on_desc_changed)
        layout.addRow("Description:", self.desc_edit)

        # Status
        self.status_label = QLabel()
        layout.addRow("Status:", self.status_label)

        # Architecture
        self.arch_label = QLabel()
        layout.addRow("Architecture:", self.arch_label)

        # Runner
        self.runner_label = QLabel()
        layout.addRow("Runner:", self.runner_label)

        # Runner version
        self.runner_version_label = QLabel()
        layout.addRow("Runner Version:", self.runner_version_label)

        # Prefix path
        self.path_label = QLabel()
        self.path_label.setWordWrap(True)
        self.path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addRow("Prefix Path:", self.path_label)

        # Size
        self.size_label = QLabel()
        layout.addRow("Size:", self.size_label)

        # Created/Updated
        self.created_label = QLabel()
        layout.addRow("Created:", self.created_label)

        self.updated_label = QLabel()
        layout.addRow("Updated:", self.updated_label)

        # DXVK/VKD3D
        self.dxvk_check = QCheckBox("Enable DXVK")
        self.dxvk_check.toggled.connect(self._on_dxvk_changed)
        layout.addRow("", self.dxvk_check)

        self.vkd3d_check = QCheckBox("Enable VKD3D")
        self.vkd3d_check.toggled.connect(self._on_vkd3d_changed)
        layout.addRow("", self.vkd3d_check)

        scroll.setWidget(content)
        self.tab_widget.addTab(scroll, "General")

    def _create_apps_tab(self):
        """Installed applications tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Toolbar
        toolbar = QHBoxLayout()
        self.add_app_btn = QPushButton("Add App...")
        self.add_app_btn.clicked.connect(self._add_app)
        toolbar.addWidget(self.add_app_btn)

        self.remove_app_btn = QPushButton("Remove App")
        self.remove_app_btn.clicked.connect(self._remove_app)
        toolbar.addWidget(self.remove_app_btn)

        self.run_app_btn = QPushButton("Run Selected")
        self.run_app_btn.clicked.connect(self._run_selected_app)
        toolbar.addWidget(self.run_app_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # App list
        self.apps_list = QListWidget()
        self.apps_list.itemDoubleClicked.connect(self._run_selected_app)
        layout.addWidget(self.apps_list)

        self.tab_widget.addTab(widget, "Apps")

    def _create_config_tab(self):
        """Configuration tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QFormLayout(content)
        layout.setLabelAlignment(Qt.AlignRight)

        # Launch options
        self.launch_options = QLineEdit()
        self.launch_options.setPlaceholderText("e.g., -windowed -noborder")
        self.launch_options.editingFinished.connect(self._on_launch_options_changed)
        layout.addRow("Launch Options:", self.launch_options)

        # Working directory
        self.working_dir = QLineEdit()
        self.working_dir.setPlaceholderText("Leave empty for default")
        self.working_dir.editingFinished.connect(self._on_working_dir_changed)
        layout.addRow("Working Dir:", self.working_dir)

        # Windows version
        self.win_version = QComboBox()
        self.win_version.addItems(["win10", "win81", "win8", "win7", "vista", "xp"])
        self.win_version.currentTextChanged.connect(self._on_win_version_changed)
        layout.addRow("Windows Version:", self.win_version)

        # Virtual desktop
        self.virtual_desktop = QCheckBox("Enable Virtual Desktop")
        self.virtual_desktop.toggled.connect(self._on_virtual_desktop_changed)
        layout.addRow("", self.virtual_desktop)

        # Desktop size
        self.desktop_size = QLineEdit()
        self.desktop_size.setPlaceholderText("e.g., 1920x1080")
        self.desktop_size.editingFinished.connect(self._on_desktop_size_changed)
        layout.addRow("Desktop Size:", self.desktop_size)

        scroll.setWidget(content)
        self.tab_widget.addTab(scroll, "Config")

    def _create_winetricks_tab(self):
        """Winetricks management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Category selector
        cat_layout = QHBoxLayout()
        cat_layout.addWidget(QLabel("Category:"))
        self.verb_category = QComboBox()
        self.verb_category.addItems(self.controller.bottle_controller.get_wintricks_categories())
        self.verb_category.currentTextChanged.connect(self._load_verbs)
        cat_layout.addWidget(self.verb_category)
        cat_layout.addStretch()
        layout.addLayout(cat_layout)

        # Verb list
        self.verbs_list = QListWidget()
        self.verbs_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.verbs_list)

        # Buttons
        btn_layout = QHBoxLayout()
        self.install_verb_btn = QPushButton("Install Selected")
        self.install_verb_btn.clicked.connect(self._install_selected_verb)
        btn_layout.addWidget(self.install_verb_btn)

        self.refresh_verbs_btn = QPushButton("Refresh Installed")
        self.refresh_verbs_btn.clicked.connect(self._refresh_installed_verbs)
        btn_layout.addWidget(self.refresh_verbs_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Installed verbs
        layout.addWidget(QLabel("Installed:"))
        self.installed_verbs = QListWidget()
        layout.addWidget(self.installed_verbs)

        self.tab_widget.addTab(widget, "Winetricks")

    def _create_env_tab(self):
        """Environment variables tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Env table
        self.env_table = QTableWidget(0, 2)
        self.env_table.setHorizontalHeaderLabels(["Variable", "Value"])
        self.env_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.env_table)

        # Buttons
        btn_layout = QHBoxLayout()
        self.add_env_btn = QPushButton("Add Variable")
        self.add_env_btn.clicked.connect(self._add_env_var)
        btn_layout.addWidget(self.add_env_btn)

        self.remove_env_btn = QPushButton("Remove Variable")
        self.remove_env_btn.clicked.connect(self._remove_env_var)
        btn_layout.addWidget(self.remove_env_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.tab_widget.addTab(widget, "Environment")

    def load_bottle(self, name: str):
        """Load bottle data into the UI"""
        self.current_bottle_name = name
        bottle = self.controller.bottle_controller.get_bottle(name)
        if not bottle:
            self.clear()
            return

        self.tab_widget.setEnabled(True)

        # General tab
        self.name_label.setText(bottle.name)
        self.desc_edit.setPlainText(bottle.description)
        self.status_label.setText(bottle.status.value)
        self.arch_label.setText(bottle.prefix.arch.value)
        self.runner_label.setText(bottle.runner_type)
        self.runner_version_label.setText(bottle.runner_version or "Unknown")
        self.path_label.setText(str(bottle.prefix.path))
        self.size_label.setText(f"{bottle.prefix.size_mb:.1f} MB")
        self.created_label.setText(bottle.created_at)
        self.updated_label.setText(bottle.updated_at)
        self.dxvk_check.setChecked(bottle.dxvk_enabled)
        self.vkd3d_check.setChecked(bottle.vkd3d_enabled)

        # Apps tab
        self._load_apps(bottle)

        # Config tab
        self.launch_options.setText(bottle.launch_options)
        self.working_dir.setText(bottle.working_dir or "")
        if bottle.windows_version:
            idx = self.win_version.findText(bottle.windows_version)
            if idx >= 0:
                self.win_version.setCurrentIndex(idx)
        self.virtual_desktop.setChecked(bottle.virtual_desktop)
        self.desktop_size.setText(bottle.desktop_size or "")

        # Winetricks tab
        self._load_verbs(self.verb_category.currentText())
        self._refresh_installed_verbs()

        # Env tab
        self._load_env_vars(bottle)

    def _load_apps(self, bottle: Bottle):
        """Load installed apps list"""
        self.apps_list.clear()
        for app in bottle.installed_apps:
            item = QListWidgetItem(f"{app['name']} ({app['exe_path']})")
            item.setData(Qt.UserRole, app['name'])
            self.apps_list.addItem(item)

    def _load_verbs(self, category: str):
        """Load verbs for selected category"""
        self.verbs_list.clear()
        verbs = self.controller.bottle_controller.get_wintricks_verbs(category)
        for verb in verbs:
            self.verbs_list.addItem(verb)

    def _refresh_installed_verbs(self):
        """Refresh list of installed verbs"""
        if not self.current_bottle_name:
            return
        self.installed_verbs.clear()
        verbs = self.controller.bottle_controller.list_installed_verbs(self.current_bottle_name)
        for verb in verbs:
            self.installed_verbs.addItem(verb)

    def _load_env_vars(self, bottle: Bottle):
        """Load environment variables"""
        self.env_table.setRowCount(0)
        for key, value in bottle.env_vars.items():
            row = self.env_table.rowCount()
            self.env_table.insertRow(row)
            self.env_table.setItem(row, 0, QTableWidgetItem(key))
            self.env_table.setItem(row, 1, QTableWidgetItem(value))

    def clear(self):
        """Clear all data"""
        self.current_bottle_name = None
        self.name_label.clear()
        self.desc_edit.clear()
        self.status_label.clear()
        self.arch_label.clear()
        self.runner_label.clear()
        self.runner_version_label.clear()
        self.path_label.clear()
        self.size_label.clear()
        self.created_label.clear()
        self.updated_label.clear()
        self.dxvk_check.setChecked(False)
        self.vkd3d_check.setChecked(False)
        self.apps_list.clear()
        self.launch_options.clear()
        self.working_dir.clear()
        self.win_version.setCurrentIndex(0)
        self.virtual_desktop.setChecked(False)
        self.desktop_size.clear()
        self.verbs_list.clear()
        self.installed_verbs.clear()
        self.env_table.setRowCount(0)
        self.tab_widget.setEnabled(False)

    def refresh(self):
        """Refresh current bottle"""
        if self.current_bottle_name:
            self.load_bottle(self.current_bottle_name)

    # Event handlers
    def _on_desc_changed(self):
        if self.current_bottle_name:
            bottle = self.controller.bottle_controller.get_bottle(self.current_bottle_name)
            if bottle:
                bottle.description = self.desc_edit.toPlainText()
                self.controller.bottle_controller.save_bottle(bottle)

    def _on_dxvk_changed(self, enabled: bool):
        if self.current_bottle_name:
            self.controller.bottle_controller.enable_dxvk(self.current_bottle_name, enabled)

    def _on_vkd3d_changed(self, enabled: bool):
        if self.current_bottle_name:
            self.controller.bottle_controller.enable_vkd3d(self.current_bottle_name, enabled)

    def _on_launch_options_changed(self):
        if self.current_bottle_name:
            bottle = self.controller.bottle_controller.get_bottle(self.current_bottle_name)
            if bottle:
                bottle.launch_options = self.launch_options.text()
                self.controller.bottle_controller.save_bottle(bottle)

    def _on_working_dir_changed(self):
        if self.current_bottle_name:
            bottle = self.controller.bottle_controller.get_bottle(self.current_bottle_name)
            if bottle:
                bottle.working_dir = self.working_dir.text() or None
                self.controller.bottle_controller.save_bottle(bottle)

    def _on_win_version_changed(self, version: str):
        if self.current_bottle_name:
            bottle = self.controller.bottle_controller.get_bottle(self.current_bottle_name)
            if bottle:
                bottle.windows_version = version
                self.controller.bottle_controller.save_bottle(bottle)
                # Apply via winetricks
                self.controller.bottle_controller.run_winetricks_verb(self.current_bottle_name, version)

    def _on_virtual_desktop_changed(self, enabled: bool):
        if self.current_bottle_name:
            bottle = self.controller.bottle_controller.get_bottle(self.current_bottle_name)
            if bottle:
                bottle.virtual_desktop = enabled
                self.controller.bottle_controller.save_bottle(bottle)
                verb = "virtualdesktop" if enabled else "novirtualdesktop"
                self.controller.bottle_controller.run_winetricks_verb(self.current_bottle_name, verb)

    def _on_desktop_size_changed(self):
        if self.current_bottle_name:
            bottle = self.controller.bottle_controller.get_bottle(self.current_bottle_name)
            if bottle:
                bottle.desktop_size = self.desktop_size.text() or None
                self.controller.bottle_controller.save_bottle(bottle)

    def _add_app(self):
        """Add a new app"""
        from PySide6.QtWidgets import QFileDialog, QInputDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Executable", "", "Windows Executables (*.exe);;All Files (*)"
        )
        if not file_path:
            return

        name, ok = QInputDialog.getText(self, "App Name", "Name for this app:", text=file_path.split("/")[-1].split(".")[0])
        if not ok or not name:
            return

        args, ok = QInputDialog.getText(self, "Arguments", "Command line arguments (optional):")
        if not ok:
            args = ""

        working_dir, ok = QInputDialog.getText(self, "Working Directory", "Working directory (optional):")
        if not ok:
            working_dir = ""

        try:
            self.controller.bottle_controller.install_app(
                self.current_bottle_name, file_path, name, args, working_dir
            )
            self._load_apps(self.controller.bottle_controller.get_bottle(self.current_bottle_name))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add app: {e}")

    def _remove_app(self):
        """Remove selected app"""
        item = self.apps_list.currentItem()
        if not item:
            return
        app_name = item.data(Qt.UserRole)
        try:
            self.controller.bottle_controller.uninstall_app(self.current_bottle_name, app_name)
            self._load_apps(self.controller.bottle_controller.get_bottle(self.current_bottle_name))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove app: {e}")

    def _run_selected_app(self):
        """Run the selected app"""
        item = self.apps_list.currentItem()
        if not item:
            return
        app_name = item.data(Qt.UserRole)
        try:
            self.controller.bottle_controller.run_app(self.current_bottle_name, app_name)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run app: {e}")

    def _install_selected_verb(self):
        """Install selected winetricks verbs"""
        items = self.verbs_list.selectedItems()
        if not items:
            return
        verbs = [item.text() for item in items]
        try:
            self.controller.bottle_controller.apply_winetricks(self.current_bottle_name, verbs)
            self._refresh_installed_verbs()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to install verbs: {e}")

    def _add_env_var(self):
        """Add environment variable"""
        from PySide6.QtWidgets import QInputDialog
        key, ok = QInputDialog.getText(self, "Add Variable", "Variable name:")
        if not ok or not key:
            return
        value, ok = QInputDialog.getText(self, "Add Variable", f"Value for {key}:")
        if not ok:
            return
        try:
            self.controller.bottle_controller.set_env_var(self.current_bottle_name, key, value)
            self._load_env_vars(self.controller.bottle_controller.get_bottle(self.current_bottle_name))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add variable: {e}")

    def _remove_env_var(self):
        """Remove environment variable"""
        row = self.env_table.currentRow()
        if row < 0:
            return
        key = self.env_table.item(row, 0).text()
        try:
            self.controller.bottle_controller.remove_env_var(self.current_bottle_name, key)
            self._load_env_vars(self.controller.bottle_controller.get_bottle(self.current_bottle_name))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove variable: {e}")