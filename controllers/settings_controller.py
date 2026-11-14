"""Settings Controller - Manages application settings"""
from pathlib import Path
from ..models import AppConfig


class SettingsController:
    """Controller for settings operations"""

    def __init__(self, main_controller):
        self.main = main_controller
        self.config = main_controller.config

    def get_config(self) -> AppConfig:
        """Get current configuration"""
        return self.config

    def update_paths(self, config_dir: str = None, bottles_dir: str = None,
                     runners_dir: str = None, backups_dir: str = None) -> bool:
        """Update directory paths"""
        try:
            if config_dir:
                self.config.config_dir = Path(config_dir).expanduser()
            if bottles_dir:
                self.config.bottles_dir = Path(bottles_dir).expanduser()
            if runners_dir:
                self.config.runners_dir = Path(runners_dir).expanduser()
            if backups_dir:
                self.config.backups_dir = Path(backups_dir).expanduser()

            self.config.ensure_dirs()
            self.config.save()
            return True
        except Exception:
            return False

    def set_default_runner(self, runner_name: str = None) -> bool:
        """Set default runner"""
        self.config.default_runner = runner_name
        self.config.save()
        return True

    def set_default_arch(self, arch: str) -> bool:
        """Set default architecture"""
        if arch in ("win64", "win32"):
            self.config.default_arch = arch
            self.config.save()
            return True
        return False

    def set_theme(self, theme: str) -> bool:
        """Set UI theme"""
        if theme in ("System", "Light", "Dark"):
            self.config.ui_theme = theme
            self.config.save()
            return True
        return False

    def set_font_size(self, size: int) -> bool:
        """Set UI font size"""
        if 8 <= size <= 24:
            self.config.font_size = size
            self.config.save()
            return True
        return False

    def toggle_setting(self, setting: str, value: bool) -> bool:
        """Toggle a boolean setting"""
        valid_settings = {
            "show_statusbar", "show_tooltips", "remember_geometry",
            "confirm_delete", "close_to_tray", "start_minimized", "wine_debug",
        }
        if setting in valid_settings:
            setattr(self.config, setting, value)
            self.config.save()
            return True
        return False

    def set_auto_refresh(self, interval: int) -> bool:
        """Set auto-refresh interval"""
        if 0 <= interval <= 3600:
            self.config.auto_refresh_interval = interval
            self.config.save()
            return True
        return False

    def set_max_log_lines(self, lines: int) -> bool:
        """Set max log lines"""
        if 100 <= lines <= 10000:
            self.config.max_log_lines = lines
            self.config.save()
            return True
        return False

    def reset_to_defaults(self) -> AppConfig:
        """Reset configuration to defaults"""
        self.config = AppConfig.get_default()
        self.main.config = self.config
        self.config.save()
        return self.config

    def validate_paths(self) -> dict:
        """Validate that configured paths exist and are writable"""
        results = {}
        for name, path in [
            ("config_dir", self.config.config_dir),
            ("bottles_dir", self.config.bottles_dir),
            ("runners_dir", self.config.runners_dir),
            ("backups_dir", self.config.backups_dir),
        ]:
            p = Path(path).expanduser()
            results[name] = {
                "path": str(p),
                "exists": p.exists(),
                "writable": p.exists() and p.is_dir() and p.stat().st_mode & 0o200,
            }
        return results