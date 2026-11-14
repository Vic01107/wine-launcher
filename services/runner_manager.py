"""Runner Manager - Detects and manages Wine/Proton runners"""
import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional
from ..models import RunnerInfo, RunnerType, AppConfig


class RunnerManager:
    """Manages Wine/Proton runner detection and installation"""

    SYSTEM_PATHS = [
        "/usr/bin/wine",
        "/usr/bin/wine64",
        "/usr/local/bin/wine",
        "/opt/wine*/bin/wine",
    ]

    PROTON_PATHS = [
        Path.home() / ".steam" / "steam" / "compatibilitytools.d" / "*",
        Path.home() / ".local" / "share" / "Steam" / "compatibilitytools.d" / "*",
        Path("/usr/share/steam/compatibilitytools.d") / "*",
        Path("/opt/steam/compatibilitytools.d") / "*",
    ]

    WINE_GE_PATHS = [
        Path.home() / ".local" / "share" / "lutris" / "runners" / "wine" / "*",
        Path.home() / ".wine-ge" / "*",
    ]

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or AppConfig.load()
        self._runners_cache: list[RunnerInfo] = []

    def discover_runners(self, force_refresh: bool = False) -> list[RunnerInfo]:
        """Discover all available Wine/Proton runners"""
        if self._runners_cache and not force_refresh:
            return self._runners_cache

        runners = []

        system_wine = self._find_system_wine()
        if system_wine:
            runners.append(system_wine)

        proton_runners = self._find_proton_runners()
        runners.extend(proton_runners)

        wine_ge_runners = self._find_wine_ge_runners()
        runners.extend(wine_ge_runners)

        custom_runners = self._find_custom_runners()
        runners.extend(custom_runners)

        self._runners_cache = runners
        return runners

    def _find_system_wine(self) -> Optional[RunnerInfo]:
        """Find system-installed Wine"""
        for path in self.SYSTEM_PATHS:
            expanded = Path(path).expanduser()
            if "*" in str(expanded):
                import glob
                matches = glob.glob(str(expanded))
                for match in matches:
                    runner = self._probe_wine(Path(match))
                    if runner:
                        return runner
            else:
                runner = self._probe_wine(expanded)
                if runner:
                    return runner
        return None

    def _probe_wine(self, wine_path: Path) -> Optional[RunnerInfo]:
        """Probe a wine executable for version info"""
        if not wine_path.exists() or not os.access(wine_path, os.X_OK):
            return None

        try:
            result = subprocess.run(
                [str(wine_path), "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and "wine" in result.stdout.lower():
                version = result.stdout.strip().split()[-1]
                prefix = wine_path.parent.parent
                return RunnerInfo(
                    name="System Wine",
                    version=version,
                    runner_type=RunnerType.SYSTEM_WINE,
                    path=prefix,
                    description=f"System Wine {version}",
                    size_mb=self._get_dir_size_mb(prefix),
                )
        except Exception:
            pass
        return None

    def _find_proton_runners(self) -> list[RunnerInfo]:
        """Find Proton runners (Steam compatibility tools)"""
        runners = []
        for base_path in self.PROTON_PATHS:
            if "*" in str(base_path):
                import glob
                matches = glob.glob(str(base_path))
                for match in matches:
                    runner = self._probe_proton(Path(match))
                    if runner:
                        runners.append(runner)
            else:
                runner = self._probe_proton(base_path)
                if runner:
                    runners.append(runner)
        return runners

    def _probe_proton(self, proton_dir: Path) -> Optional[RunnerInfo]:
        """Probe a Proton installation"""
        proton_script = proton_dir / "proton"
        if not proton_script.exists():
            return None

        try:
            result = subprocess.run(
                [str(proton_script), "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_line = result.stdout.strip()
                version = version_line.split()[0].replace("proton-", "")
                return RunnerInfo(
                    name=f"Proton {version}",
                    version=version,
                    runner_type=RunnerType.PROTON,
                    path=proton_dir,
                    description=f"Steam Proton {version}",
                    size_mb=self._get_dir_size_mb(proton_dir),
                )
        except Exception:
            pass
        return None

    def _find_wine_ge_runners(self) -> list[RunnerInfo]:
        """Find Wine-GE runners (Lutris, manual installs)"""
        runners = []
        for base_path in self.WINE_GE_PATHS:
            if "*" in str(base_path):
                import glob
                matches = glob.glob(str(base_path))
                for match in matches:
                    runner = self._probe_wine_ge(Path(match))
                    if runner:
                        runners.append(runner)
        return runners

    def _probe_wine_ge(self, wine_dir: Path) -> Optional[RunnerInfo]:
        """Probe a Wine-GE installation"""
        wine_bin = wine_dir / "bin" / "wine"
        if not wine_bin.exists():
            return None

        try:
            result = subprocess.run(
                [str(wine_bin), "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and "wine" in result.stdout.lower():
                version = result.stdout.strip().split()[-1]
                if "GE" in version or "ge" in version or "Staging" in version:
                    return RunnerInfo(
                        name=f"Wine-GE {version}",
                        version=version,
                        runner_type=RunnerType.WINE_GE,
                        path=wine_dir,
                        description=f"Wine-GE {version}",
                        size_mb=self._get_dir_size_mb(wine_dir),
                    )
        except Exception:
            pass
        return None

    def _find_custom_runners(self) -> list[RunnerInfo]:
        """Find custom runners in our runners directory"""
        runners = []
        if self.config.runners_dir.exists():
            for runner_dir in self.config.runners_dir.iterdir():
                if runner_dir.is_dir():
                    runner = self._probe_custom_runner(runner_dir)
                    if runner:
                        runners.append(runner)
        return runners

    def _probe_custom_runner(self, runner_dir: Path) -> Optional[RunnerInfo]:
        """Probe a custom runner directory"""
        wine_bin = runner_dir / "bin" / "wine"
        if wine_bin.exists():
            try:
                result = subprocess.run(
                    [str(wine_bin), "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    version = result.stdout.strip().split()[-1]
                    return RunnerInfo(
                        name=runner_dir.name,
                        version=version,
                        runner_type=RunnerType.CUSTOM,
                        path=runner_dir,
                        description=f"Custom: {runner_dir.name}",
                        size_mb=self._get_dir_size_mb(runner_dir),
                    )
            except Exception:
                pass
        return None

    def get_runner(self, name: str) -> Optional[RunnerInfo]:
        """Get a specific runner by name"""
        for runner in self.discover_runners():
            if runner.name == name:
                return runner
        return None

    def get_default_runner(self) -> Optional[RunnerInfo]:
        """Get the default runner based on config"""
        runners = self.discover_runners()
        if not runners:
            return None

        priority = {
            RunnerType.PROTON: 0,
            RunnerType.PROTON_GE: 1,
            RunnerType.WINE_GE: 2,
            RunnerType.SYSTEM_WINE: 3,
            RunnerType.CUSTOM: 4,
        }
        runners.sort(key=lambda r: priority.get(r.runner_type, 99))
        return runners[0]

    def _get_dir_size_mb(self, path: Path) -> float:
        """Get directory size in MB"""
        try:
            total = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
            return round(total / (1024 * 1024), 2)
        except Exception:
            return 0.0

    def install_proton_ge(self, version: str = "latest") -> Optional[RunnerInfo]:
        """Download and install Proton-GE (placeholder)"""
        return None

    def install_wine_ge(self, version: str = "latest") -> Optional[RunnerInfo]:
        """Download and install Wine-GE (placeholder)"""
        return None