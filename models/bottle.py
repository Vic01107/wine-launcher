"""Bottle model - High-level application container (like Bottles flatpak)"""
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional
import json
from .wine_prefix import WinePrefix, PrefixArch


class BottleStatus(Enum):
    """Status of a bottle"""
    STOPPED = "stopped"
    RUNNING = "running"
    ERROR = "error"
    CREATING = "creating"
    UPDATING = "updating"


@dataclass
class Bottle:
    """
    A Bottle is a user-friendly container for a Wine prefix.
    It adds metadata, application tracking, and runner management.
    """
    name: str
    prefix: WinePrefix
    description: str = ""
    status: BottleStatus = BottleStatus.STOPPED
    created_at: str = field(default_factory=lambda: __import__('datetime').datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: __import__('datetime').datetime.now().isoformat())

    # Runner configuration
    runner_type: str = "wine"
    runner_version: str = ""
    custom_runner_path: Optional[Path] = None

    # Application tracking
    installed_apps: list[dict] = field(default_factory=list)
    default_executable: Optional[str] = None

    # Options
    dxvk_enabled: bool = True
    vkd3d_enabled: bool = True
    dgvoodoo2_enabled: bool = False
    winetricks: list[str] = field(default_factory=list)

    # Environment
    env_vars: dict = field(default_factory=dict)
    launch_options: str = ""

    def __post_init__(self):
        if self.custom_runner_path:
            self.custom_runner_path = Path(self.custom_runner_path).expanduser().resolve()
        if isinstance(self.status, str):
            self.status = BottleStatus(self.status)
        if isinstance(self.prefix, dict):
            self.prefix = WinePrefix.from_dict(self.prefix)

    @property
    def runner_path(self) -> Optional[Path]:
        """Get the effective runner path"""
        if self.runner_type == "custom" and self.custom_runner_path:
            return self.custom_runner_path
        return self.prefix.runner_path

    @property
    def is_running(self) -> bool:
        return self.status == BottleStatus.RUNNING

    def add_app(self, name: str, exe_path: str, args: str = "", working_dir: str = "") -> None:
        """Add an installed application to this bottle"""
        app = {
            "name": name,
            "exe_path": exe_path,
            "args": args,
            "working_dir": working_dir,
            "installed_at": __import__('datetime').datetime.now().isoformat(),
        }
        self.installed_apps.append(app)
        self.updated_at = __import__('datetime').datetime.now().isoformat()

    def remove_app(self, name: str) -> bool:
        """Remove an application by name"""
        for i, app in enumerate(self.installed_apps):
            if app["name"] == name:
                self.installed_apps.pop(i)
                self.updated_at = __import__('datetime').datetime.now().isoformat()
                return True
        return False

    def get_app(self, name: str) -> Optional[dict]:
        """Get app config by name"""
        for app in self.installed_apps:
            if app["name"] == name:
                return app
        return None

    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            "name": self.name,
            "prefix": self.prefix.to_dict(),
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "runner_type": self.runner_type,
            "runner_version": self.runner_version,
            "custom_runner_path": str(self.custom_runner_path) if self.custom_runner_path else None,
            "installed_apps": self.installed_apps,
            "default_executable": self.default_executable,
            "dxvk_enabled": self.dxvk_enabled,
            "vkd3d_enabled": self.vkd3d_enabled,
            "dgvoodoo2_enabled": self.dgvoodoo2_enabled,
            "winetricks": self.winetricks,
            "env_vars": self.env_vars,
            "launch_options": self.launch_options,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Bottle":
        """Deserialize from dictionary"""
        data = data.copy()
        data["prefix"] = WinePrefix.from_dict(data["prefix"])
        if data.get("custom_runner_path"):
            data["custom_runner_path"] = Path(data["custom_runner_path"])
        return cls(**data)

    def save(self, config_dir: Path) -> None:
        """Save bottle to config directory"""
        config_dir.mkdir(parents=True, exist_ok=True)
        self.updated_at = __import__('datetime').datetime.now().isoformat()
        config_file = config_dir / f"{self.name}.json"
        config_file.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, config_file: Path) -> "Bottle":
        """Load bottle from config file"""
        data = json.loads(config_file.read_text())
        return cls.from_dict(data)

    @classmethod
    def create_new(cls, name: str, prefix_path: Path, description: str = "",
                   runner_type: str = "wine", arch: PrefixArch = PrefixArch.WIN64) -> "Bottle":
        """Create a new bottle with a fresh prefix"""
        prefix = WinePrefix.create_new(prefix_path, name, arch)
        return cls(
            name=name,
            prefix=prefix,
            description=description,
            runner_type=runner_type,
        )