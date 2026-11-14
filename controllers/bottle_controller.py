"""Bottle Controller - Manages bottle operations"""
from typing import Optional, List
from ..models import Bottle, BottleStatus, WinePrefix, PrefixArch
from ..services import BottleService, WinetricksService


class BottleController:
    """Controller for bottle-related operations"""

    def __init__(self, main_controller):
        self.main = main_controller
        self.service = main_controller.bottle_service
        self.winetricks = WinetricksService()

    def list_bottles(self) -> List[Bottle]:
        """Get all bottles"""
        return self.service.list_bottles()

    def get_bottle(self, name: str) -> Optional[Bottle]:
        """Get a bottle by name"""
        return self.service.get_bottle(name)

    def create_bottle(self, name: str, description: str = "",
                      runner_type: str = "system-wine", arch: str = "win64",
                      runner_name: str = None) -> Bottle:
        """Create a new bottle"""
        arch_enum = PrefixArch.WIN64 if arch == "win64" else PrefixArch.WIN32
        return self.service.create_bottle(name, description, runner_type, arch_enum, runner_name)

    def delete_bottle(self, name: str, remove_prefix: bool = True) -> bool:
        """Delete a bottle"""
        return self.service.delete_bottle(name, remove_prefix)

    def rename_bottle(self, old_name: str, new_name: str) -> bool:
        """Rename a bottle (not fully implemented)"""
        return False

    def get_bottle_details(self, name: str) -> dict:
        """Get detailed info about a bottle"""
        bottle = self.get_bottle(name)
        if not bottle:
            return {}

        return {
            "name": bottle.name,
            "description": bottle.description,
            "status": bottle.status.value,
            "prefix_path": str(bottle.prefix.path),
            "prefix_size_mb": bottle.prefix.size_mb,
            "arch": bottle.prefix.arch.value,
            "runner_type": bottle.runner_type,
            "runner_version": bottle.runner_version,
            "created_at": bottle.created_at,
            "updated_at": bottle.updated_at,
            "installed_apps": bottle.installed_apps,
            "dxvk_enabled": bottle.dxvk_enabled,
            "vkd3d_enabled": bottle.vkd3d_enabled,
            "winetricks": bottle.winetricks,
            "env_vars": bottle.env_vars,
        }

    def run_app(self, bottle_name: str, app_name: str):
        """Run an installed app"""
        bottle = self.get_bottle(bottle_name)
        if not bottle:
            raise ValueError(f"Bottle '{bottle_name}' not found")
        return self.service.run_app(bottle, app_name)

    def run_executable(self, bottle_name: str, executable: str, args: list = None, cwd: str = None):
        """Run an arbitrary executable in the bottle"""
        bottle = self.get_bottle(bottle_name)
        if not bottle:
            raise ValueError(f"Bottle '{bottle_name}' not found")

        from pathlib import Path
        cwd_path = Path(cwd) if cwd else None
        return self.service.run_executable(bottle, executable, args, cwd_path)

    def install_app(self, bottle_name: str, exe_path: str, name: str = None,
                    args: str = "", working_dir: str = "") -> dict:
        """Register an installed application"""
        bottle = self.get_bottle(bottle_name)
        if not bottle:
            raise ValueError(f"Bottle '{bottle_name}' not found")

        from pathlib import Path
        return self.service.install_app(bottle, Path(exe_path), name, args, working_dir)

    def uninstall_app(self, bottle_name: str, app_name: str) -> bool:
        """Unregister an application"""
        bottle = self.get_bottle(bottle_name)
        if not bottle:
            raise ValueError(f"Bottle '{bottle_name}' not found")
        return self.service.uninstall_app(bottle, app_name)

    def get_installed_apps(self, bottle_name: str) -> list:
        """Get list of installed apps in a bottle"""
        bottle = self.get_bottle(bottle_name)
        if not bottle:
            return []
        return bottle.installed_apps

    def apply_winetricks(self, bottle_name: str, verbs: list[str]) -> bool:
        """Apply winetricks verbs to a bottle"""
        bottle = self.get_bottle(bottle_name)
        if not bottle:
            raise ValueError(f"Bottle '{bottle_name}' not found")
        return self.service.apply_winetricks(bottle, verbs)

    def get_wintricks_verbs(self, category: str = None) -> list[str]:
        """Get available winetricks verbs"""
        return self.winetricks.get_verbs(category)

    def get_wintricks_categories(self) -> list[str]:
        """Get winetricks categories"""
        return self.winetricks.get_categories()

    def run_winetricks_verb(self, bottle_name: str, verb: str):
        """Run a single winetricks verb"""
        bottle = self.get_bottle(bottle_name)
        if not bottle:
            raise ValueError(f"Bottle '{bottle_name}' not found")
        return self.winetricks.run_verb(bottle.prefix, verb)

    def list_installed_verbs(self, bottle_name: str) -> list[str]:
        """List installed winetricks verbs in a bottle"""
        bottle = self.get_bottle(bottle_name)
        if not bottle:
            return []
        return self.winetricks.list_installed(bottle.prefix)

    def enable_dxvk(self, bottle_name: str, enabled: bool = True):
        """Enable/disable DXVK"""
        bottle = self.get_bottle(bottle_name)
        if not bottle:
            raise ValueError(f"Bottle '{bottle_name}' not found")
        self.service.enable_dxvk(bottle, enabled)

    def enable_vkd3d(self, bottle_name: str, enabled: bool = True):
        """Enable/disable VKD3D"""
        bottle = self.get_bottle(bottle_name)
        if not bottle:
            raise ValueError(f"Bottle '{bottle_name}' not found")
        self.service.enable_vkd3d(bottle, enabled)

    def set_env_var(self, bottle_name: str, key: str, value: str):
        """Set environment variable"""
        bottle = self.get_bottle(bottle_name)
        if not bottle:
            raise ValueError(f"Bottle '{bottle_name}' not found")
        self.service.set_env_var(bottle, key, value)

    def remove_env_var(self, bottle_name: str, key: str):
        """Remove environment variable"""
        bottle = self.get_bottle(bottle_name)
        if not bottle:
            raise ValueError(f"Bottle '{bottle_name}' not found")
        self.service.remove_env_var(bottle, key)

    def get_env_vars(self, bottle_name: str) -> dict:
        """Get all environment variables for a bottle"""
        bottle = self.get_bottle(bottle_name)
        if not bottle:
            return {}
        return bottle.env_vars

    def backup_bottle(self, bottle_name: str, backup_dir: str = None) -> str:
        """Create a backup of a bottle"""
        bottle = self.get_bottle(bottle_name)
        if not bottle:
            raise ValueError(f"Bottle '{bottle_name}' not found")

        from pathlib import Path
        backup_path = Path(backup_dir) if backup_dir else self.main.config.config_dir / "backups"
        result = self.service.backup_bottle(bottle, backup_path)
        return str(result)

    def restore_bottle(self, backup_path: str, new_name: str = None) -> Bottle:
        """Restore a bottle from backup"""
        from pathlib import Path
        return self.service.restore_bottle(Path(backup_path), new_name)