"""Bottle List Widget - Displays list of bottles with status"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QMenu, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QAction

from ..controllers import MainController
from ..models import Bottle, BottleStatus


class BottleListWidget(QWidget):
    """Widget for displaying and managing bottle list"""

    bottle_selected = Signal(str)
    bottle_deleted = Signal(str)

    STATUS_COLORS = {
        BottleStatus.STOPPED: "#666666",
        BottleStatus.RUNNING: "#4CAF50",
        BottleStatus.CREATING: "#FF9800",
        BottleStatus.ERROR: "#F44336",
        BottleStatus.UPDATING: "#2196F3",
    }

    def __init__(self, controller: MainController):
        super().__init__()
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.list_widget.currentItemChanged.connect(self._on_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self._on_double_click)

        layout.addWidget(self.list_widget)

    def refresh(self):
        """Refresh the bottle list from controller"""
        self.list_widget.clear()
        bottles = self.controller.bottle_controller.list_bottles()

        for bottle in bottles:
            item = self._create_bottle_item(bottle)
            self.list_widget.addItem(item)

        if bottles:
            self.list_widget.setCurrentRow(0)

    def _create_bottle_item(self, bottle: Bottle) -> QListWidgetItem:
        """Create a list item for a bottle"""
        item = QListWidgetItem()
        item.setData(Qt.UserRole, bottle.name)

        # Status indicator
        status_color = self.STATUS_COLORS.get(bottle.status, "#666666")
        pixmap = self._create_status_icon(status_color)
        item.setIcon(QIcon(pixmap))

        # Text with name and runner
        runner_name = bottle.runner_version or bottle.runner_type
        text = f"{bottle.name}\n  {runner_name} • {bottle.prefix.arch.value}"
        item.setText(text)
        item.setToolTip(
            f"Name: {bottle.name}\n"
            f"Status: {bottle.status.value}\n"
            f"Runner: {runner_name}\n"
            f"Arch: {bottle.prefix.arch.value}\n"
            f"Path: {bottle.prefix.path}\n"
            f"Apps: {len(bottle.installed_apps)}\n"
            f"Size: {bottle.prefix.size_mb:.1f} MB"
        )

        item.setSizeHint(QSize(0, 60))
        return item

    def _create_status_icon(self, color: str) -> QPixmap:
        """Create a small colored circle icon"""
        size = 16
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(2, 2, size - 4, size - 4)
        painter.end()

        return pixmap

    def _on_selection_changed(self, current: QListWidgetItem, previous: QListWidgetItem):
        """Handle selection change"""
        if current:
            name = current.data(Qt.UserRole)
            self.bottle_selected.emit(name)

    def _on_double_click(self, item: QListWidgetItem):
        """Handle double click - run default app"""
        name = item.data(Qt.UserRole)
        bottle = self.controller.bottle_controller.get_bottle(name)
        if bottle and bottle.installed_apps:
            self.controller.bottle_controller.run_app(name, bottle.installed_apps[0]["name"])

    def _show_context_menu(self, pos):
        """Show context menu for bottle"""
        item = self.list_widget.itemAt(pos)
        if not item:
            return

        name = item.data(Qt.UserRole)
        menu = QMenu(self)

        run_action = QAction("Run App...", self)
        run_action.triggered.connect(lambda: self._run_bottle(name))
        menu.addAction(run_action)

        run_exe_action = QAction("Run Executable...", self)
        run_exe_action.triggered.connect(lambda: self._run_executable(name))
        menu.addAction(run_exe_action)

        menu.addSeparator()

        winetricks_action = QAction("Winetricks...", self)
        winetricks_action.triggered.connect(lambda: self._winetricks(name))
        menu.addAction(winetricks_action)

        backup_action = QAction("Backup...", self)
        backup_action.triggered.connect(lambda: self._backup(name))
        menu.addAction(backup_action)

        menu.addSeparator()

        rename_action = QAction("Rename...", self)
        rename_action.triggered.connect(lambda: self._rename(name))
        menu.addAction(rename_action)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self._delete(name))
        menu.addAction(delete_action)

        menu.exec(self.list_widget.mapToGlobal(pos))

    def _run_bottle(self, name: str):
        """Run app in bottle"""
        bottle = self.controller.bottle_controller.get_bottle(name)
        if bottle and bottle.installed_apps:
            from .run_dialog import RunDialog
            from PySide6.QtWidgets import QDialog
            dialog = RunDialog(bottle.installed_apps, self)
            if dialog.exec() == QDialog.Accepted:
                app_name = dialog.get_selected_app()
                if app_name:
                    self.controller.bottle_controller.run_app(name, app_name)

    def _run_executable(self, name: str):
        """Run custom executable in bottle"""
        from .run_dialog import RunDialog
        from PySide6.QtWidgets import QDialog
        dialog = RunDialog([], self, allow_custom=True)
        if dialog.exec() == QDialog.Accepted:
            exe, args, cwd = dialog.get_custom_executable()
            if exe:
                self.controller.bottle_controller.run_executable(name, exe, args, cwd)

    def _winetricks(self, name: str):
        """Open winetricks for bottle"""
        from PySide6.QtWidgets import QInputDialog
        categories = self.controller.bottle_controller.get_wintricks_categories()
        category, ok = QInputDialog.getItem(self, "Winetricks", "Select category:", categories, 0, False)
        if not ok:
            return

        verbs = self.controller.bottle_controller.get_wintricks_verbs(category)
        verb, ok = QInputDialog.getItem(self, "Winetricks", f"Select verb ({category}):", verbs, 0, False)
        if not ok:
            return

        try:
            result = self.controller.bottle_controller.run_winetricks_verb(name, verb)
            if result.success:
                self.refresh()
            else:
                QMessageBox.warning(self, "Winetricks Failed", result.stderr or result.stdout)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run winetricks: {e}")

    def _backup(self, name: str):
        """Backup bottle"""
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        backup_dir = QFileDialog.getExistingDirectory(self, "Select Backup Directory")
        if backup_dir:
            try:
                path = self.controller.bottle_controller.backup_bottle(name, backup_dir)
                QMessageBox.information(self, "Success", f"Backup created: {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Backup failed: {e}")

    def _rename(self, name: str):
        """Rename bottle"""
        from PySide6.QtWidgets import QInputDialog, QMessageBox
        new_name, ok = QInputDialog.getText(self, "Rename Bottle", "New name:", text=name)
        if ok and new_name and new_name != name:
            try:
                # This would need implementation in controller
                QMessageBox.information(self, "Not Implemented", "Rename not yet implemented")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Rename failed: {e}")

    def _delete(self, name: str):
        """Delete bottle"""
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Delete Bottle",
            f"Delete bottle '{name}' and all its data?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.controller.bottle_controller.delete_bottle(name)
                self.bottle_deleted.emit(name)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete bottle: {e}")

    def get_selected_bottle(self) -> str:
        """Get currently selected bottle name"""
        item = self.list_widget.currentItem()
        if item:
            return item.data(Qt.UserRole)
        return None