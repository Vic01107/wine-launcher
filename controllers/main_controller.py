"""Main Controller - Application entry point and coordination"""
from typing import Optional
from ..models import AppConfig
from ..services import RunnerManager, BottleService


class MainController:
    """Main application controller - coordinates all sub-controllers"""

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or AppConfig.load()
        self.config.ensure_dirs()

        self.runner_manager = RunnerManager(self.config)
        self.bottle_service = BottleService(self.config)

        self._bottle_controller = None
        self._runner_controller = None
        self._settings_controller = None

        self.current_bottle = None
        self.running_process = None

    @property
    def bottle_controller(self):
        if self._bottle_controller is None:
            from .bottle_controller import BottleController
            self._bottle_controller = BottleController(self)
        return self._bottle_controller

    @property
    def runner_controller(self):
        if self._runner_controller is None:
            from .runner_controller import RunnerController
            self._runner_controller = RunnerController(self)
        return self._runner_controller

    @property
    def settings_controller(self):
        if self._settings_controller is None:
            from .settings_controller import SettingsController
            self._settings_controller = SettingsController(self)
        return self._settings_controller

    def initialize(self) -> bool:
        """Initialize the application"""
        self.runner_manager.discover_runners()
        return True

    def shutdown(self) -> None:
        """Clean shutdown"""
        if self.running_process:
            self.running_process.terminate()
        self.config.save()

    def get_bottles(self) -> list:
        """Get all bottles"""
        return self.bottle_service.list_bottles()

    def get_runners(self) -> list:
        """Get all available runners"""
        return self.runner_manager.discover_runners()

    def create_bottle(self, name: str, description: str = "",
                      runner_type: str = "system-wine", arch: str = "win64",
                      runner_name: str = None):
        """Create a new bottle"""
        from ..models import PrefixArch
        arch_enum = PrefixArch.WIN64 if arch == "win64" else PrefixArch.WIN32
        return self.bottle_service.create_bottle(
            name, description, runner_type, arch_enum, runner_name
        )

    def delete_bottle(self, name: str, remove_prefix: bool = True) -> bool:
        """Delete a bottle"""
        return self.bottle_service.delete_bottle(name, remove_prefix)

    def run_bottle_app(self, bottle_name: str, app_name: str):
        """Run an app in a bottle"""
        bottle = self.bottle_service.get_bottle(bottle_name)
        if not bottle:
            raise ValueError(f"Bottle '{bottle_name}' not found")
        return self.bottle_service.run_app(bottle, app_name)

    def run_executable(self, bottle_name: str, executable: str, args: list = None):
        """Run arbitrary executable in a bottle"""
        bottle = self.bottle_service.get_bottle(bottle_name)
        if not bottle:
            raise ValueError(f"Bottle '{bottle_name}' not found")
        return self.bottle_service.run_executable(bottle, executable, args)