"""Wine Prefix model - Represents a Wine/Proton prefix (Windows environment)"""
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional
import json
import os


class PrefixArch(Enum):
    """Architecture of the Wine prefix"""
    WIN32 = "win32"
    WIN64 = "win64"


@dataclass
class WinePrefix:
    """
    Represents a Wine prefix - a self-contained Windows environment.
    Each prefix has its own C: drive, registry, and installed applications.
    """
    path: Path
    name: str
    arch: PrefixArch = PrefixArch.WIN64
    version: str = "1.0"
    created_at: str = field(default_factory=lambda: __import__('datetime').datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: __import__('datetime').datetime.now().isoformat())
    metadata: dict = field(default_factory=dict)

    # Wine/Proton specific
    wine_version: Optional[str] = None
    proton_version: Optional[str] = None
    runner_path: Optional[Path] = None

    # Environment variables
    env_vars: dict = field(default_factory=dict)

    def __post_init__(self):
        self.path = Path(self.path).expanduser().resolve()
        if self.runner_path:
            self.runner_path = Path(self.runner_path).expanduser().resolve()

    @property
    def drive_c(self) -> Path:
        """Path to the C: drive inside the prefix"""
        return self.path / "drive_c"

    @property
    def registry_path(self) -> Path:
        """Path to registry files"""
        return self.path

    @property
    def is_valid(self) -> bool:
        """Check if prefix exists and has basic structure"""
        return self.path.exists() and (self.path / "system.reg").exists()

    @property
    def size_mb(self) -> float:
        """Get prefix size in MB"""
        if not self.path.exists():
            return 0.0
        total = sum(f.stat().st_size for f in self.path.rglob("*") if f.is_file())
        return round(total / (1024 * 1024), 2)

    def to_dict(self) -> dict:
        """Serialize to dictionary"""
        return {
            "path": str(self.path),
            "name": self.name,
            "arch": self.arch.value,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "wine_version": self.wine_version,
            "proton_version": self.proton_version,
            "runner_path": str(self.runner_path) if self.runner_path else None,
            "env_vars": self.env_vars,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WinePrefix":
        """Deserialize from dictionary"""
        data = data.copy()
        data["path"] = Path(data["path"])
        data["arch"] = PrefixArch(data["arch"])
        if data.get("runner_path"):
            data["runner_path"] = Path(data["runner_path"])
        return cls(**data)

    def save(self, config_dir: Path) -> None:
        """Save prefix metadata to config directory"""
        config_dir.mkdir(parents=True, exist_ok=True)
        self.updated_at = __import__('datetime').datetime.now().isoformat()
        config_file = config_dir / f"{self.name}.json"
        config_file.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, config_file: Path) -> "WinePrefix":
        """Load prefix from config file"""
        data = json.loads(config_file.read_text())
        return cls.from_dict(data)

    @classmethod
    def create_new(cls, path: Path, name: str, arch: PrefixArch = PrefixArch.WIN64,
                   runner_path: Optional[Path] = None) -> "WinePrefix":
        """Create a new Wine prefix at the given path"""
        path = Path(path).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)

        prefix = cls(
            path=path,
            name=name,
            arch=arch,
            runner_path=runner_path,
        )

        # Initialize basic Wine prefix structure
        prefix._initialize_prefix()

        return prefix

    def _initialize_prefix(self) -> None:
        """Initialize basic Wine prefix directory structure"""
        dirs = [
            self.drive_c / "windows",
            self.drive_c / "windows" / "system32",
            self.drive_c / "windows" / "syswow64",
            self.drive_c / "Program Files",
            self.drive_c / "Program Files (x86)",
            self.drive_c / "users" / "Public",
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

        # Create basic registry files if they don't exist
        for reg_file in ["system.reg", "user.reg", "userdef.reg"]:
            reg_path = self.path / reg_file
            if not reg_path.exists():
                reg_path.write_text("")

    def get_env(self) -> dict:
        """Get environment variables for running Wine in this prefix"""
        env = os.environ.copy()
        env.update({
            "WINEPREFIX": str(self.path),
            "WINEARCH": self.arch.value,
        })
        env.update(self.env_vars)
        return env

    def get_wine_cmd(self) -> list[str]:
        """Get the wine command to use for this prefix"""
        if self.runner_path and self.runner_path.exists():
            return [str(self.runner_path)]
        return ["wine"]

    def run(self, executable: str | Path, args: list[str] = None, cwd: Path = None) -> "ProcessResult":
        """Run an executable inside this prefix"""
        import subprocess

        cmd = self.get_wine_cmd()
        if isinstance(executable, Path):
            executable = str(executable)
        cmd.append(executable)
        if args:
            cmd.extend(args)

        env = self.get_env()
        work_dir = cwd or self.drive_c

        result = subprocess.run(
            cmd,
            env=env,
            cwd=work_dir,
            capture_output=True,
            text=True,
        )
        return ProcessResult(result.returncode, result.stdout, result.stderr)


@dataclass
class ProcessResult:
    """Result of running a process in a Wine prefix"""
    returncode: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        return self.returncode == 0