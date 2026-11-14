"""Runner Controller - Manages Wine/Proton runner operations"""
from typing import Optional, List
from ..models import RunnerInfo, RunnerType, AppConfig
from ..services import RunnerManager


class RunnerController:
    """Controller for runner-related operations"""

    def __init__(self, main_controller):
        self.main = main_controller
        self.service = main_controller.runner_manager

    def list_runners(self) -> List[RunnerInfo]:
        """Get all available runners"""
        return self.service.discover_runners()

    def get_runner(self, name: str) -> Optional[RunnerInfo]:
        """Get a specific runner by name"""
        return self.service.get_runner(name)

    def get_default_runner(self) -> Optional[RunnerInfo]:
        """Get the default runner based on priority"""
        return self.service.get_default_runner()

    def validate_runner(self, runner: RunnerInfo) -> bool:
        """Validate that a runner works correctly"""
        import subprocess
        wine_bin = runner.path / "bin" / "wine"
        if runner.runner_type == RunnerType.PROTON or runner.runner_type == RunnerType.PROTON_GE:
            wine_bin = runner.path / "proton"
        elif runner.runner_type == RunnerType.SYSTEM_WINE:
            wine_bin = Path(runner.path) / "bin" / "wine"

        if not wine_bin.exists():
            return False

        try:
            result = subprocess.run(
                [str(wine_bin), "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0 and "wine" in result.stdout.lower()
        except Exception:
            return False

    def refresh_runners(self) -> List[RunnerInfo]:
        """Force refresh runner list"""
        return self.service.discover_runners(force_refresh=True)

    def install_proton_ge(self, version: str = "latest") -> Optional[RunnerInfo]:
        """Install Proton-GE (placeholder)"""
        return self.service.install_proton_ge(version)

    def install_wine_ge(self, version: str = "latest") -> Optional[RunnerInfo]:
        """Install Wine-GE (placeholder)"""
        return self.service.install_wine_ge(version)

    def add_custom_runner(self, path: str, name: str = None) -> Optional[RunnerInfo]:
        """Add a custom runner from a path"""
        from pathlib import Path
        runner_dir = Path(path)
        if not runner_dir.exists():
            return None

        # Probe the runner
        runner = self.service._probe_custom_runner(runner_dir)
        if runner and name:
            runner.name = name
        return runner