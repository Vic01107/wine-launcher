"""Bottle Service - High-level bottle management"""
import shutil
from pathlib import Path
from typing import Optional
from ..models import Bottle, BottleStatus, WinePrefix, PrefixArch, AppConfig
from .runner_manager import RunnerManager


class BottleService:
    """Service for managing bottles (create, delete, run, configure)"""

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or AppConfig.load()
        self.runner_manager = RunnerManager(config)
        self.config.ensure_dirs()

    def create_bottle(self, name: str, description: str = "",
                      runner_type: str = "system-wine", arch: PrefixArch = PrefixArch.WIN64,
                      runner_name: Optional[str] = None) -> Bottle:
        """Create a new bottle"""
        safe_name = self._sanitize_name(name)
        prefix_path = self.config.bottles_dir / safe_name

        if prefix_path.exists():
            raise ValueError(f"Bottle '{name}' already exists")

        runner_path = None
        if runner_name:
            runner = self.runner_manager.get_runner(runner_name)
            if runner:
                runner_path = runner.path

        bottle = Bottle.create_new(
            name=safe_name,
            prefix_path=prefix_path,
            description=description,
            runner_type=runner_type,
            arch=arch,
        )

        if runner_path:
            bottle.prefix.runner_path = runner_path
            if self.runner_manager.get_runner(runner_name):
                bottle.runner_version = self.runner_manager.get_runner(runner_name).version

        bottle.save(self.config.config_dir)
        return bottle

    def delete_bottle(self, name: str, remove_prefix: bool = True) -> bool:
        """Delete a bottle and optionally its prefix"""
        safe_name = self._sanitize_name(name)
        config_file = self.config.config_dir / f"{safe_name}.json"

        if not config_file.exists():
            return False

        bottle = Bottle.load(config_file)

        if remove_prefix and bottle.prefix.path.exists():
            shutil.rmtree(bottle.prefix.path, ignore_errors=True)

        config_file.unlink(missing_ok=True)
        return True

    def get_bottle(self, name: str) -> Optional[Bottle]:
        """Load a bottle by name"""
        safe_name = self._sanitize_name(name)
        config_file = self.config.config_dir / f"{safe_name}.json"
        if config_file.exists():
            return Bottle.load(config_file)
        return None

    def list_bottles(self) -> list[Bottle]:
        """List all bottles"""
        bottles = []
        for config_file in self.config.config_dir.glob("*.json"):
            if config_file.name != "config.json":
                try:
                    bottle = Bottle.load(config_file)
                    bottles.append(bottle)
                except Exception:
                    pass
        return sorted(bottles, key=lambda b: b.name.lower())

    def save_bottle(self, bottle: Bottle) -> None:
        """Save bottle changes"""
        bottle.save(self.config.config_dir)

    def run_executable(self, bottle: Bottle, executable: str, args: list[str] = None,
                       cwd: Path = None, env: dict = None):
        """Run an executable in the bottle's prefix"""
        from ..models.wine_prefix import ProcessResult

        bottle.status = BottleStatus.RUNNING
        self.save_bottle(bottle)

        try:
            run_env = bottle.prefix.get_env()
            run_env.update(bottle.env_vars)
            if env:
                run_env.update(env)

            launch_args = []
            if bottle.launch_options:
                launch_args.extend(bottle.launch_options.split())

            if args:
                launch_args.extend(args)

            result = bottle.prefix.run(executable, launch_args, cwd)
            return result
        finally:
            bottle.status = BottleStatus.STOPPED
            self.save_bottle(bottle)

    def run_app(self, bottle: Bottle, app_name: str):
        """Run an installed application by name"""
        app = bottle.get_app(app_name)
        if not app:
            raise ValueError(f"App '{app_name}' not found in bottle '{bottle.name}'")

        exe_path = app["exe_path"]
        args = app["args"].split() if app["args"] else []
        cwd = Path(app["working_dir"]) if app["working_dir"] else None

        return self.run_executable(bottle, exe_path, args, cwd)

    def install_app(self, bottle: Bottle, exe_path: Path, name: str = None,
                    args: str = "", working_dir: str = "") -> dict:
        """Register an installed application"""
        if name is None:
            name = exe_path.stem

        bottle.add_app(name, str(exe_path), args, working_dir)
        self.save_bottle(bottle)
        return bottle.get_app(name)

    def uninstall_app(self, bottle: Bottle, name: str) -> bool:
        """Unregister an application"""
        result = bottle.remove_app(name)
        if result:
            self.save_bottle(bottle)
        return result

    def apply_winetricks(self, bottle: Bottle, verbs: list[str]) -> bool:
        """Apply winetricks verbs to a bottle"""
        for verb in verbs:
            if verb not in bottle.winetricks:
                bottle.winetricks.append(verb)
        self.save_bottle(bottle)
        return True

    def enable_dxvk(self, bottle: Bottle, enabled: bool = True) -> None:
        """Enable/disable DXVK for a bottle"""
        bottle.dxvk_enabled = enabled
        self.save_bottle(bottle)

    def enable_vkd3d(self, bottle: Bottle, enabled: bool = True) -> None:
        """Enable/disable VKD3D for a bottle"""
        bottle.vkd3d_enabled = enabled
        self.save_bottle(bottle)

    def set_env_var(self, bottle: Bottle, key: str, value: str) -> None:
        """Set an environment variable for the bottle"""
        bottle.env_vars[key] = value
        self.save_bottle(bottle)

    def remove_env_var(self, bottle: Bottle, key: str) -> None:
        """Remove an environment variable"""
        bottle.env_vars.pop(key, None)
        self.save_bottle(bottle)

    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for filesystem"""
        import re
        return re.sub(r'[<>:"/\\|?*]', '_', name).strip()

    def get_bottle_size(self, bottle: Bottle) -> float:
        """Get bottle size in MB"""
        return bottle.prefix.size_mb

    def backup_bottle(self, bottle: Bottle, backup_dir: Path) -> Path:
        """Create a backup of a bottle (prefix + config)"""
        backup_dir.mkdir(parents=True, exist_ok=True)
        import tarfile
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{bottle.name}_{timestamp}.tar.gz"
        backup_path = backup_dir / backup_name

        with tarfile.open(backup_path, "w:gz") as tar:
            tar.add(bottle.prefix.path, arcname=f"{bottle.name}/prefix")
            config_file = self.config.config_dir / f"{bottle.name}.json"
            if config_file.exists():
                tar.add(config_file, arcname=f"{bottle.name}/config.json")

        return backup_path

    def restore_bottle(self, backup_path: Path, new_name: str = None) -> Bottle:
        """Restore a bottle from backup"""
        import tarfile

        with tarfile.open(backup_path, "r:gz") as tar:
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                tar.extractall(tmpdir)
                extracted = Path(tmpdir)
                prefix_src = extracted / backup_path.stem.replace(".tar.gz", "") / "prefix"
                config_src = extracted / backup_path.stem.replace(".tar.gz", "") / "config.json"

                if not prefix_src.exists():
                    raise ValueError("Invalid backup: prefix not found")

                name = new_name or prefix_src.parent.name
                safe_name = self._sanitize_name(name)
                prefix_dst = self.config.bottles_dir / safe_name

                if prefix_dst.exists():
                    raise ValueError(f"Bottle '{name}' already exists")

                shutil.copytree(prefix_src, prefix_dst)

                if config_src.exists():
                    import json
                    data = json.loads(config_src.read_text())
                    data["prefix"]["path"] = str(prefix_dst)
                    bottle = Bottle.from_dict(data)
                else:
                    bottle = Bottle.create_new(name, prefix_dst)

                bottle.save(self.config.config_dir)
                return bottle