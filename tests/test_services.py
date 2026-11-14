"""Tests for Services layer"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from models import AppConfig, WinePrefix, Bottle, PrefixArch, BottleStatus
from services import BottleService, RunnerManager, WinetricksService


class TestBottleService:
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
    def service(self, config):
        return BottleService(config)

    def test_create_bottle(self, service):
        bottle = service.create_bottle("TestBottle", "Description", "proton-ge", PrefixArch.WIN64)

        assert bottle.name == "TestBottle"
        assert bottle.description == "Description"
        assert bottle.runner_type == "proton-ge"
        assert bottle.prefix.arch == PrefixArch.WIN64
        assert bottle.prefix.path.exists()

    def test_create_duplicate_bottle_fails(self, service):
        service.create_bottle("TestBottle", "", "system-wine", PrefixArch.WIN64)

        with pytest.raises(ValueError, match="already exists"):
            service.create_bottle("TestBottle", "", "system-wine", PrefixArch.WIN64)

    def test_get_bottle(self, service):
        created = service.create_bottle("TestBottle", "", "system-wine", PrefixArch.WIN64)
        loaded = service.get_bottle("TestBottle")

        assert loaded is not None
        assert loaded.name == created.name

    def test_get_nonexistent_bottle(self, service):
        loaded = service.get_bottle("NonExistent")
        assert loaded is None

    def test_list_bottles(self, service):
        service.create_bottle("BottleA", "", "system-wine", PrefixArch.WIN64)
        service.create_bottle("BottleB", "", "proton", PrefixArch.WIN64)

        bottles = service.list_bottles()
        assert len(bottles) == 2
        assert bottles[0].name == "BottleA"
        assert bottles[1].name == "BottleB"

    def test_delete_bottle(self, service):
        service.create_bottle("ToDelete", "", "system-wine", PrefixArch.WIN64)
        result = service.delete_bottle("ToDelete", remove_prefix=True)

        assert result is True
        assert service.get_bottle("ToDelete") is None

    def test_delete_nonexistent_bottle(self, service):
        result = service.delete_bottle("NonExistent")
        assert result is False

    def test_install_uninstall_app(self, service):
        bottle = service.create_bottle("TestBottle", "", "system-wine", PrefixArch.WIN64)

        app = service.install_app(bottle, Path("drive_c/app.exe"), "MyApp", "-arg", "drive_c/app")
        assert app["name"] == "MyApp"
        assert len(bottle.installed_apps) == 1

        result = service.uninstall_app(bottle, "MyApp")
        assert result is True
        assert len(bottle.installed_apps) == 0

    def test_apply_winetricks(self, service):
        bottle = service.create_bottle("TestBottle", "", "system-wine", PrefixArch.WIN64)

        result = service.apply_winetricks(bottle, ["vcrun2019", "dxvk"])
        assert result is True
        assert "vcrun2019" in bottle.winetricks
        assert "dxvk" in bottle.winetricks

    def test_enable_dxvk_vkd3d(self, service):
        bottle = service.create_bottle("TestBottle", "", "system-wine", PrefixArch.WIN64)

        service.enable_dxvk(bottle, True)
        assert bottle.dxvk_enabled is True

        service.enable_vkd3d(bottle, True)
        assert bottle.vkd3d_enabled is True

    def test_env_vars(self, service):
        bottle = service.create_bottle("TestBottle", "", "system-wine", PrefixArch.WIN64)

        service.set_env_var(bottle, "DXVK_HUD", "1")
        assert bottle.env_vars["DXVK_HUD"] == "1"

        service.remove_env_var(bottle, "DXVK_HUD")
        assert "DXVK_HUD" not in bottle.env_vars

    def test_backup_restore(self, service):
        bottle = service.create_bottle("TestBottle", "Desc", "system-wine", PrefixArch.WIN64)
        bottle.add_app("App1", "app1.exe")
        bottle.winetricks = ["vcrun2019"]

        # Backup
        backup_path = service.backup_bottle(bottle, Path(bottle.config.backups_dir))
        assert backup_path.exists()
        assert backup_path.suffix == ".gz"

        # Delete original
        service.delete_bottle("TestBottle", remove_prefix=True)
        assert service.get_bottle("TestBottle") is None

        # Restore
        restored = service.restore_bottle(backup_path, "RestoredBottle")
        assert restored.name == "RestoredBottle"
        assert restored.description == "Desc"
        assert len(restored.installed_apps) == 1
        assert restored.winetricks == ["vcrun2019"]


class TestWinetricksService:
    def test_get_categories(self):
        service = WinetricksService()
        categories = service.get_categories()

        assert "libraries" in categories
        assert "settings" in categories
        assert "apps" in categories

    def test_get_verbs(self):
        service = WinetricksService()
        verbs = service.get_verbs("libraries")

        assert "vcrun2019" in verbs
        assert "dxvk" in verbs
        assert "dotnet48" in verbs

    def test_get_all_verbs(self):
        service = WinetricksService()
        all_verbs = service.get_verbs()

        assert len(all_verbs) > 50
        assert "vcrun2019" in all_verbs
        assert "win10" in all_verbs

    @patch('subprocess.run')
    def test_run_verb_not_available(self, mock_run):
        service = WinetricksService()
        service._winetricks_path = None

        with tempfile.TemporaryDirectory() as tmpdir:
            prefix = WinePrefix.create_new(Path(tmpdir) / "prefix", PrefixArch.WIN64)
            result = service.run_verb(prefix, "vcrun2019")

            assert result.success is False
            assert "winetricks not found" in result.stderr


class TestRunnerManager:
    @pytest.fixture
    def config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = AppConfig.get_default()
            config.config_dir = Path(tmpdir) / "config"
            config.runners_dir = Path(tmpdir) / "runners"
            config.ensure_dirs()
            yield config

    def test_discover_runners_empty(self, config):
        manager = RunnerManager(config)
        runners = manager.discover_runners()

        # Should return empty list when no Wine/Proton installed
        assert isinstance(runners, list)

    def test_get_default_runner_priority(self, config):
        manager = RunnerManager(config)

        # Mock some runners
        from models import RunnerInfo, RunnerType

        proton = RunnerInfo("Proton 9.0", "9.0", RunnerType.PROTON, Path("/opt/proton"), "", 100)
        system = RunnerInfo("System Wine", "9.0", RunnerType.SYSTEM_WINE, Path("/usr"), "", 200)

        manager._runners_cache = [system, proton]

        default = manager.get_default_runner()
        assert default.runner_type == RunnerType.PROTON  # Proton has higher priority

    def test_sanitize_name(self, config):
        manager = RunnerManager(config)

        assert manager._sanitize_name("Normal Name") == "Normal Name"
        assert manager._sanitize_name('Name<>:"/\\|?*') == "Name__________"
        assert manager._sanitize_name("  spaced  ") == "spaced"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])