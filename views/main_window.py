"""Main Window - Primary application window"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QToolBar, QStatusBar, QMessageBox, QFileDialog,
    QInputDialog, QDialog
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QAction, QIcon, QKeySequence

from .bottle_list import BottleListWidget
from .bottle_detail import BottleDetailWidget
from .create_bottle_dialog import CreateBottleDialog
from .run_dialog import RunDialog
from .settings_dialog import SettingsDialog

from ..controllers import MainController
from ..models import Bottle


class MainWindow(QMainWindow):
    """Main application window with split view"""

    bottle_selected = Signal(str)
    bottle_created = Signal()
    bottle_deleted = Signal(str)

    def __init__(self, controller: MainController):
        super().__init__()
        self.controller = controller
        self.current_bottle_name = None

        self.setWindowTitle("Wine Launcher")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        self._setup_ui()
        self._setup_menus()
        self._setup_toolbar()
        self._setup_statusbar()
        self._connect_signals()

        self._refresh_bottles()

    def _setup_ui(self):
        """Setup the main UI layout"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        # Main splitter
        self.splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(self.splitter)

        # Left panel - Bottle list
        self.bottle_list = BottleListWidget(self.controller)
        self.splitter.addWidget(self.bottle_list)

        # Right panel - Bottle details
        self.bottle_detail = BottleDetailWidget(self.controller)
        self.splitter.addWidget(self.bottle_detail)

        # Set initial splitter sizes (30% list, 70% detail)
        self.splitter.setSizes([300, 900])

    def _setup_menus(self):
        """Setup application menus"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New Bottle", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self._on_new_bottle)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        backup_action = QAction("&Backup Bottle...", self)
        backup_action.setShortcut(QKeySequence("Ctrl+B"))
        backup_action.triggered.connect(self._on_backup_bottle)
        file_menu.addAction(backup_action)

        restore_action = QAction("&Restore Bottle...", self)
        restore_action.triggered.connect(self._on_restore_bottle)
        file_menu.addAction(restore_action)

        file_menu.addSeparator()

        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self._on_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Bottle menu
        bottle_menu = menubar.addMenu("&Bottle")

        run_action = QAction("&Run App...", self)
        run_action.setShortcut(QKeySequence("Ctrl+R"))
        run_action.triggered.connect(self._on_run_app)
        bottle_menu.addAction(run_action)

        run_exe_action = QAction("Run &Executable...", self)
        run_exe_action.setShortcut(QKeySequence("Ctrl+E"))
        run_exe_action.triggered.connect(self._on_run_executable)
        bottle_menu.addAction(run_exe_action)

        bottle_menu.addSeparator()

        winetricks_action = QAction("&Winetricks...", self)
        winetricks_action.setShortcut(QKeySequence("Ctrl+W"))
        winetricks_action.triggered.connect(self._on_winetricks)
        bottle_menu.addAction(winetricks_action)

        bottle_menu.addSeparator()

        delete_action = QAction("&Delete Bottle", self)
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.triggered.connect(self._on_delete_bottle)
        bottle_menu.addAction(delete_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self):
        """Setup toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        new_btn = QAction("New Bottle", self)
        new_btn.triggered.connect(self._on_new_bottle)
        toolbar.addAction(new_btn)

        toolbar.addSeparator()

        run_btn = QAction("Run App", self)
        run_btn.triggered.connect(self._on_run_app)
        toolbar.addAction(run_btn)

        run_exe_btn = QAction("Run Executable", self)
        run_exe_btn.triggered.connect(self._on_run_executable)
        toolbar.addAction(run_exe_btn)

        toolbar.addSeparator()

        winetricks_btn = QAction("Winetricks", self)
        winetricks_btn.triggered.connect(self._on_winetricks)
        toolbar.addAction(winetricks_btn)

        toolbar.addSeparator()

        settings_btn = QAction("Settings", self)
        settings_btn.triggered.connect(self._on_settings)
        toolbar.addAction(settings_btn)

    def _setup_statusbar(self):
        """Setup status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Runner info label
        self.runner_label = QWidget()
        self.status_bar.addPermanentWidget(self.runner_label)

    def _connect_signals(self):
        """Connect signals between components"""
        self.bottle_list.bottle_selected.connect(self._on_bottle_selected)
        self.bottle_list.bottle_deleted.connect(self._on_bottle_deleted)
        self.bottle_detail.run_app_requested.connect(self._on_run_app)
        self.bottle_detail.run_exe_requested.connect(self._on_run_executable)
        self.bottle_detail.winetricks_requested.connect(self._on_winetricks)

    def _refresh_bottles(self):
        """Refresh the bottle list"""
        self.bottle_list.refresh()
        runners = self.controller.runner_controller.list_runners()
        default_runner = self.controller.runner_controller.get_default_runner()
        if default_runner:
            self.status_bar.showMessage(f"Default runner: {default_runner.name} ({default_runner.version})")

    def _on_bottle_selected(self, name: str):
        """Handle bottle selection"""
        self.current_bottle_name = name
        self.bottle_detail.load_bottle(name)

    def _on_bottle_deleted(self, name: str):
        """Handle bottle deletion"""
        self.bottle_deleted.emit(name)
        self.bottle_detail.clear()
        self.current_bottle_name = None
        self._refresh_bottles()

    def _on_new_bottle(self):
        """Create a new bottle"""
        dialog = CreateBottleDialog(self.controller, self)
        if dialog.exec() == QDialog.Accepted:
            name, desc, runner_type, arch, runner_name = dialog.get_data()
            try:
                self.controller.bottle_controller.create_bottle(
                    name, desc, runner_type, arch, runner_name
                )
                self._refresh_bottles()
                self.bottle_created.emit()
                self.status_bar.showMessage(f"Created bottle: {name}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create bottle: {e}")

    def _on_delete_bottle(self):
        """Delete selected bottle"""
        if not self.current_bottle_name:
            return

        reply = QMessageBox.question(
            self, "Delete Bottle",
            f"Delete bottle '{self.current_bottle_name}' and all its data?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.controller.bottle_controller.delete_bottle(self.current_bottle_name)
                self._refresh_bottles()
                self.status_bar.showMessage("Bottle deleted", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete bottle: {e}")

    def _on_run_app(self):
        """Run an installed app in the selected bottle"""
        if not self.current_bottle_name:
            QMessageBox.warning(self, "No Bottle", "Please select a bottle first")
            return

        bottle = self.controller.bottle_controller.get_bottle(self.current_bottle_name)
        if not bottle or not bottle.installed_apps:
            QMessageBox.information(self, "No Apps", "No apps installed in this bottle")
            return

        dialog = RunDialog(bottle.installed_apps, self)
        if dialog.exec() == QDialog.Accepted:
            app_name = dialog.get_selected_app()
            if app_name:
                try:
                    self.controller.bottle_controller.run_app(self.current_bottle_name, app_name)
                    self.status_bar.showMessage(f"Running {app_name}...", 3000)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to run app: {e}")

    def _on_run_executable(self):
        """Run a custom executable in the selected bottle"""
        if not self.current_bottle_name:
            QMessageBox.warning(self, "No Bottle", "Please select a bottle first")
            return

        dialog = RunDialog([], self, allow_custom=True)
        if dialog.exec() == QDialog.Accepted:
            exe, args, cwd = dialog.get_custom_executable()
            if exe:
                try:
                    self.controller.bottle_controller.run_executable(
                        self.current_bottle_name, exe, args, cwd
                    )
                    self.status_bar.showMessage(f"Running {exe}...", 3000)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to run executable: {e}")

    def _on_winetricks(self):
        """Open winetricks dialog"""
        if not self.current_bottle_name:
            QMessageBox.warning(self, "No Bottle", "Please select a bottle first")
            return

        # Show winetricks category selection
        categories = self.controller.bottle_controller.get_wintricks_categories()
        category, ok = QInputDialog.getItem(
            self, "Winetricks", "Select category:", categories, 0, False
        )
        if not ok:
            return

        verbs = self.controller.bottle_controller.get_wintricks_verbs(category)
        verb, ok = QInputDialog.getItem(
            self, "Winetricks", f"Select verb ({category}):", verbs, 0, False
        )
        if not ok:
            return

        try:
            result = self.controller.bottle_controller.run_winetricks_verb(
                self.current_bottle_name, verb
            )
            if result.success:
                self.status_bar.showMessage(f"Winetricks {verb} completed", 3000)
                self.bottle_detail.refresh()
            else:
                QMessageBox.warning(self, "Winetricks Failed", result.stderr or result.stdout)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run winetricks: {e}")

    def _on_backup_bottle(self):
        """Backup selected bottle"""
        if not self.current_bottle_name:
            QMessageBox.warning(self, "No Bottle", "Please select a bottle first")
            return

        backup_dir = QFileDialog.getExistingDirectory(self, "Select Backup Directory")
        if backup_dir:
            try:
                path = self.controller.bottle_controller.backup_bottle(
                    self.current_bottle_name, backup_dir
                )
                QMessageBox.information(self, "Success", f"Backup created: {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Backup failed: {e}")

    def _on_restore_bottle(self):
        """Restore a bottle from backup"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Backup File", "", "Tarball (*.tar.gz *.tgz)"
        )
        if file_path:
            name, ok = QInputDialog.getText(
                self, "Restore Bottle", "New bottle name (empty = original):"
            )
            if ok:
                try:
                    new_name = name if name else None
                    self.controller.bottle_controller.restore_bottle(file_path, new_name)
                    self._refresh_bottles()
                    QMessageBox.information(self, "Success", "Bottle restored")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Restore failed: {e}")

    def _on_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.controller, self)
        dialog.exec()
        self._refresh_bottles()

    def _on_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About Wine Launcher",
            "Wine Launcher - Run Windows apps on Linux\n\n"
            "MVC Architecture with PySide6\n"
            "Supports Wine, Proton, Wine-GE runners\n"
            "Winetricks integration for dependencies"
        )

    def closeEvent(self, event):
        """Handle window close"""
        self.controller.shutdown()
        event.accept()