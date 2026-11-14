"""Tests for Controllers layer"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from models import AppConfig, PrefixArch
from controllers import MainController, BottleController, RunnerController, SettingsController


class TestMainController:
    @pytest.fixture
    def config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = AppConfig.get_default()
            config.config_dir = Path(tmpdir) / "config"
            config.bottles_dir = Path(tmpdir) / "bottles"
            config.runners_dir = Path(tmpdir) / "runners"
            config.backups_dir = Path(tmpdir) / "backups"
            config.ensure_dirs()
            yield config

    @pytest.fixture
    def controller(self, config):
        with patch('controllers.main_controller.RunnerManager') as mock_rm:
            mock_instance = Mock()
            mock_instance.discover_runners.return_value = []
            mock_rm.return_value = mock_instance

            controller = MainController(config)
            controller.runner_manager = mock_instance
            yield controller

    def test_initialize(self, controller):
        result = controller.initialize()
        assert result is True
        controller.runner_manager.discover_runners.assert_called_once()

    def test_shutdown(self, controller):
        controller.shutdown()
        controller.config.save.assert_called()

    def test_get_bottles(self, controller):
        mock_bottle = Mock()
        controller.bottle_service.list_bottles.return_value = [mock_bottle]

        bottles = controller.get_bottles()
        assert bottles == [mock_bottle]

    def test_get_runners(self, controller):
        mock_runner = Mock()
        controller.runner_manager.discover_runners.return_value = [mock_runner]

        runners = controller.get_runners()
        assert runners == [mock_runner]

    def test_lazy_load_controllers(self, controller):
        # Access each controller property to trigger lazy loading
        bc = controller.bottle_controller
        rc = controller.runner_controller
        sc = controller.settings_controller

        assert bc is not None
        assert rc is not None
        assert sc is not None

        # Second access returns same instance
        assert controller.bottle_controller is bc


class TestBottleController:
    @pytest.fixture
    def config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = AppConfig.get_default()
            config.config_dir = Path(tmpdir) / "config"
            config.bottles_dir = Path(tmpdir) / "bottles"
            config.runners_dir = Path(tmpdir) / "runners"
            config.backups_dir = Path(tmpdir) / "backups"
            config.ensure_dirs()
            yield config

    @pytest.fixture
    def main_controller(self, config):
        with patch('controllers.main_controller.RunnerManager') as mock_rm, \
             patch('controllers.main_controller.BottleService') as mock_bs:

            mock_rm_instance = Mock()
            mock_rm_instance.discover_runners.return_value = []
            mock_rm.return_value = mock_rm_instance

            mock_bs_instance = Mock()
            mock_bs.return_value = mock_bs_instance

            controller = MainController(config)
            controller.runner_manager = mock_rm_instance
            controller.bottle_service = mock_bs_instance
            yield controller

    def test_create_bottle(self, main_controller):
        from models import Bottle
        mock_bottle = Mock(spec=Bottle)
        mock_bottle.name = "TestBottle"
        main_controller.bottle_service.create_bottle.return_value = mock_bottle

        bottle = main_controller.bottle_controller.create_bottle(
            "TestBottle", "Desc", "proton-ge", "win64", "Proton-GE 9.21"
        )

        assert bottle.name == "TestBottle"
        main_controller.bottle_service.create_bottle.assert_called_once()

    def test_list_bottles(self, main_controller):
        mock_bottles = [Mock(), Mock()]
        main_controller.bottle_service.list_bottles.return_value = mock_bottles

        bottles = main_controller.bottle_controller.list_bottles()
        assert bottles == mock_bottles

    def test_get_bottle_details(self, main_controller):
        from models import Bottle, BottleStatus, WinePrefix, PrefixArch
        mock_bottle = Mock(spec=Bottle)
        mock_bottle.name = "TestBottle"
        mock_bottle.description = "Desc"
        mock_bottle.status = BottleStatus.STOPPED
        mock_bottle.prefix = Mock(spec=WinePrefix)
        mock_bottle.prefix.path = Path("/test/path")
        mock_bottle.prefix.size_mb = 100.5
        mock_bottle.prefix.arch = PrefixArch.WIN64
        mock_bottle.runner_type = "proton-ge"
        mock_bottle.runner_version = "9.21"
        mock_bottle.created_at = "2025-01-01"
        mock_bottle.updated_at = "2025-01-02"
        mock_bottle.installed_apps = []
        mock_bottle.dxvk_enabled = True
        mock_bottle.vkd3d_enabled = False
        mock_bottle.winetricks = ["vcrun2019"]
        mock_bottle.env_vars = {"DXVK_HUD": "1"}

        main_controller.bottle_service.get_bottle.return_value = mock_bottle

        details = main_controller.bottle_controller.get_bottle_details("TestBottle")

        assert details["name"] == "TestBottle"
        assert details["status"] == "stopped"
        assert details["dxvk_enabled"] is True
        assert details["env_vars"] == {"DXVK_HUD": "1"}

    def test_run_app(self, main_controller):
        main_controller.bottle_service.run_app.return_value = Mock()

        main_controller.bottle_controller.run_app("TestBottle", "MyApp")

        main_controller.bottle_service.run_app.assert_called_once()


class TestRunnerController:
    @pytest.fixture
    def main_controller(self):
        with patch('controllers.main_controller.RunnerManager') as mock_rm:
            mock_rm_instance = Mock()
            mock_rm.return_value = mock_rm_instance

            from controllers import MainController
            from models import AppConfig
            config = AppConfig.get_default()
            controller = MainController(config)
            controller.runner_manager = mock_rm_instance
            yield controller

    def test_list_runners(self, main_controller):
        from models import RunnerInfo, RunnerType
        mock_runners = [
            RunnerInfo("Proton 9.0", "9.0", RunnerType.PROTON, Path("/opt/proton"), "", 100),
            RunnerInfo("System Wine", "9.0", RunnerType.SYSTEM_WINE, Path("/usr"), "", 200),
        ]
        main_controller.runner_manager.discover_runners.return_value = mock_runners

        runners = main_controller.runner_controller.list_runners()
        assert len(runners) == 2

    def test_get_default_runner(self, main_controller):
        from models import RunnerInfo, RunnerType
        mock_runner = RunnerInfo("Proton 9.0", "9.0", RunnerType.PROTON, Path("/opt/proton"), "", 100)
        main_controller.runner_manager.get_default_runner.return_value = mock_runner

        runner = main_controller.runner_controller.get_default_runner()
        assert runner.name == "Proton 9.0"

    def test_refresh_runners(self, main_controller):
        main_controller.runner_controller.refresh_runners()
        main_controller.runner_manager.discover_runners.assert_called_with(force_refresh=True)


class TestSettingsController:
    @pytest.fixture
    def config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = AppConfig.get_default()
            config.config_dir = Path(tmpdir) / "config"
            config.bottles_dir = Path(tmpdir) / "bottles"
            config.runners_dir = Path(tmpdir) / "runners"
            config.backups_dir = Path(tmpdir) / "backups"
            config.ensure_dirs()
            yield config

    @pytest.fixture
    def main_controller(self, config):
        with patch('controllers.main_controller.RunnerManager') as mock_rm, \
             patch('controllers.main_controller.BottleService') as mock_bs:

            mock_rm_instance = Mock()
            mock_rm_instance.discover_runners.return_value = []
            mock_rm.return_value = mock_rm_instance

            controller = MainController(config)
            controller.runner_manager = mock_rm_instance
            controller.bottle_service = Mock()
            yield controller

    def test_update_paths(self, main_controller):
        result = main_controller.settings_controller.update_paths(
            bottles_dir="/new/bottles",
            runners_dir="/new/runners"
        )

        assert result is True
        assert str(main_controller.config.bottles_dir) == "/new/bottles"
        assert str(main_controller.config.runners_dir) == "/new/runners"

    def test_set_default_runner(self, main_controller):
        result = main_controller.settings_controller.set_default_runner("proton-ge")

        assert result is True
        assert main_controller.config.default_runner == "proton-ge"

    def test_set_invalid_arch(self, main_controller):
        result = main_controller.settings_controller.set_default_arch("invalid")
        assert result is False

        result = main_controller.settings_controller.set_default_arch("win32")
        assert result is True
        assert main_controller.config.default_arch == "win32"

    def test_toggle_setting(self, main_controller):
        result = main_controller.settings_controller.toggle_setting("show_statusbar", False)
        assert result is True
        assert main_controller.config.show_statusbar is False

        result = main_controller.settings_controller.toggle_setting("invalid_setting", True)
        assert result is False

    def test_reset_to_defaults(self, main_controller):
        main_controller.config.default_runner = "custom"
        main_controller.config.font_size = 20

        new_config = main_controller.settings_controller.reset_to_defaults()

        assert new_config.default_runner is None
        assert new_config.font_size == 10

    def test_validate_paths(self, main_controller):
        results = main_controller.settings_controller.validate_paths()

        assert "config_dir" in results
        assert "bottles_dir" in results
        assert "runners_dir" in results
        assert "backups_dir" in results

        for name, info in results.items():
            assert "path" in info
            assert "exists" in info
            assert "writable" in info


if __name__ == "__main__":
    pytest.main([__file__, "-v"])