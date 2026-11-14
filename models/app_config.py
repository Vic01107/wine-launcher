"""App Config model - Application configuration and runner types"""
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional
import json


class RunnerType(Enum):
    """Types of Wine runners"""
    SYSTEM_WINE = "system-wine"
    PROTON = "proton"
    PROTON_GE = "proton-ge"
    WINE_GE = "wine-ge"
    CUSTOM = "custom"


@dataclass
class AppConfig:
    """Global application configuration"""
    # Paths
    bottles_dir: Path = field(default_factory=lambda: Path.home() / ".local" / "share" / "wine-launcher" / "bottles")
    config_dir: Path = field(default_factory=lambda: Path.home() / ".config" / "wine-launcher")
    runners_dir: Path = field(default_factory=lambda: Path.home() / ".local" / "share" / "wine-launcher" / "runners")
    downloads_dir: Path = field(default_factory=lambda: Path.home() / "Downloads" / "wine-launcher")

    # Default settings
    default_arch: str = "win64"
    default_runner: str = "system-wine"
    auto_check_updates: bool = True
    show_terminal: bool = False

    # UI preferences
    theme: str = "system"
    language: str = "es"
    window_geometry: Optional[dict] = None

    # Advanced
    vulkan_icd: str = ""
    dxvk_version: str = ""
    vkd3d_version: str = ""

    def __post_init__(self):
        self.bottles_dir = Path(self.bottles_dir).expanduser().resolve()
        self.config_dir = Path(self.config_dir).expanduser().resolve()
        self.runners_dir = Path(self.runners_dir).expanduser().resolve()
        self.downloads_dir = Path(self.downloads_dir).expanduser().resolve()

    def ensure_dirs(self) -> None:
        """Create all required directories"""
        for d in [self.bottles_dir, self.config_dir, self.runners_dir, self.downloads_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> dict:
        return {
            "bottles_dir": str(self.bottles_dir),
            "config_dir": str(self.config_dir),
            "runners_dir": str(self.runners_dir),
            "downloads_dir": str(self.downloads_dir),
            "default_arch": self.default_arch,
            "default_runner": self.default_runner,
            "auto_check_updates": self.auto_check_updates,
            "show_terminal": self.show_terminal,
            "theme": self.theme,
            "language": self.language,
            "window_geometry": self.window_geometry,
            "vulkan_icd": self.vulkan_icd,
            "dxvk_version": self.dxvk_version,
            "vkd3d_version": self.vkd3d_version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AppConfig":
        return cls(**data)

    def save(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        config_file = self.config_dir / "config.json"
        config_file.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, config_dir: Optional[Path] = None) -> "AppConfig":
        if config_dir is None:
            config_dir = Path.home() / ".config" / "wine-launcher"
        config_file = config_dir / "config.json"
        if config_file.exists():
            data = json.loads(config_file.read_text())
            return cls.from_dict(data)
        return cls(config_dir=config_dir)


@dataclass
class RunnerInfo:
    """Information about an available Wine/Proton runner"""
    name: str
    version: str
    runner_type: RunnerType
    path: Path
    description: str = ""
    installed: bool = True
    size_mb: float = 0.0

    def __post_init__(self):
        self.path = Path(self.path).expanduser().resolve()
        if isinstance(self.runner_type, str):
            self.runner_type = RunnerType(self.runner_type)

    @property
    def executable(self) -> Path:
        """Get the wine executable path"""
        if self.runner_type in (RunnerType.PROTON, RunnerType.PROTON_GE):
            return self.path / "proton"
        return self.path / "bin" / "wine"

    @property
    def wine64_path(self) -> Path:
        return self.path / "bin" / "wine64"

    @property
    def wineserver_path(self) -> Path:
        return self.path / "bin" / "wineserver"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "runner_type": self.runner_type.value,
            "path": str(self.path),
            "description": self.description,
            "installed": self.installed,
            "size_mb": self.size_mb,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RunnerInfo":
        data = data.copy()
        data["path"] = Path(data["path"])
        return cls(**data)