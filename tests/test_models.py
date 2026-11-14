"""Tests for Models layer"""
import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime

from models import (
    WinePrefix, Bottle, AppConfig, RunnerInfo, RunnerType,
    BottleStatus, PrefixArch
)


class TestPrefixArch:
    def test_values(self):
        assert PrefixArch.WIN64.value == "win64"
        assert PrefixArch.WIN32.value == "win32"


class TestBottleStatus:
    def test_values(self):
        assert BottleStatus.STOPPED.value == "stopped"
        assert BottleStatus.RUNNING.value == "running"
        assert BottleStatus.CREATING.value == "creating"
        assert BottleStatus.ERROR.value == "error"
        assert BottleStatus.UPDATING.value == "updating"


class TestRunnerType:
    def test_values(self):
        assert RunnerType.SYSTEM_WINE.value == "system-wine"
        assert RunnerType.PROTON.value == "proton"
        assert RunnerType.PROTON_GE.value == "proton-ge"
        assert RunnerType.WINE_GE.value == "wine-ge"
        assert RunnerType.CUSTOM.value == "custom"


class TestWinePrefix:
    def test_create_new(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            prefix_path = Path(tmpdir) / "test_prefix"
            prefix = WinePrefix.create_new(prefix_path, PrefixArch.WIN64)

            assert prefix.path == prefix_path
            assert prefix.arch == PrefixArch.WIN64
            assert prefix.runner_path is None
            assert prefix.path.exists()
            assert (prefix.path / "drive_c").exists()
            assert (prefix.path / "user.reg").exists()
            assert (prefix.path / "system.reg").exists()

    def test_get_env(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            prefix_path = Path(tmpdir) / "test_prefix"
            prefix = WinePrefix.create_new(prefix_path, PrefixArch.WIN64)
            env = prefix.get_env()

            assert "WINEPREFIX" in env
            assert env["WINEPREFIX"] == str(prefix_path)
            assert "WINEARCH" in env
            assert env["WINEARCH"] == "win64"

    def test_size_mb(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            prefix_path = Path(tmpdir) / "test_prefix"
            prefix = WinePrefix.create_new(prefix_path, PrefixArch.WIN64)

            # Create a test file
            (prefix_path / "test.txt").write_text("x" * 1024 * 1024)  # 1MB

            size = prefix.size_mb
            assert size >= 1.0


class TestBottle:
    def test_create_new(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            prefix_path = Path(tmpdir) / "test_bottle"
            bottle = Bottle.create_new(
                name="TestBottle",
                prefix_path=prefix_path,
                description="Test description",
                runner_type="proton-ge",
                arch=PrefixArch.WIN64
            )

            assert bottle.name == "TestBottle"
            assert bottle.description == "Test description"
            assert bottle.runner_type == "proton-ge"
            assert bottle.prefix.arch == PrefixArch.WIN64
            assert bottle.status == BottleStatus.STOPPED
            assert bottle.installed_apps == []
            assert bottle.winetricks == []
            assert bottle.env_vars == {}
            assert bottle.dxvk_enabled is False
            assert bottle.vkd3d_enabled is False

    def test_add_remove_app(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            prefix_path = Path(tmpdir) / "test_bottle"
            bottle = Bottle.create_new("Test", prefix_path)

            # Add app
            app = bottle.add_app("MyApp", "drive_c/app.exe", "-arg", "drive_c/app")
            assert app["name"] == "MyApp"
            assert app["exe_path"] == "drive_c/app.exe"
            assert app["args"] == "-arg"
            assert app["working_dir"] == "drive_c/app"
            assert len(bottle.installed_apps) == 1

            # Get app
            retrieved = bottle.get_app("MyApp")
            assert retrieved == app

            # Remove app
            result = bottle.remove_app("MyApp")
            assert result is True
            assert len(bottle.installed_apps) == 0

            # Remove non-existent
            result = bottle.remove_app("NonExistent")
            assert result is False

    def test_to_from_dict(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            prefix_path = Path(tmpdir) / "test_bottle"
            bottle = Bottle.create_new("Test", prefix_path, runner_type="system-wine")
            bottle.add_app("App1", "app1.exe")
            bottle.winetricks = ["vcrun2019", "dxvk"]
            bottle.env_vars = {"DXVK_HUD": "1"}

            data = bottle.to_dict()
            assert data["name"] == "Test"
            assert data["runner_type"] == "system-wine"
            assert len(data["installed_apps"]) == 1

            restored = Bottle.from_dict(data)
            assert restored.name == bottle.name
            assert restored.runner_type == bottle.runner_type
            assert len(restored.installed_apps) == 1
            assert restored.winetricks == ["vcrun2019", "dxvk"]
            assert restored.env_vars == {"DXVK_HUD": "1"}

    def test_save_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "config"
            config_dir.mkdir()
            prefix_path = Path(tmpdir) / "bottles" / "TestBottle"

            bottle = Bottle.create_new("TestBottle", prefix_path, description="Desc")
            bottle.add_app("App1", "app1.exe")
            bottle.save(config_dir)

            # Load
            loaded = Bottle.load(config_dir / "TestBottle.json")
            assert loaded.name == "TestBottle"
            assert loaded.description == "Desc"
            assert len(loaded.installed_apps) == 1


class TestAppConfig:
    def test_get_default(self):
        config = AppConfig.get_default()
        assert config.default_arch == "win64"
        assert config.ui_theme == "System"
        assert config.font_size == 10

    def test_load_save(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / "config"
            config_dir.mkdir()

            config = AppConfig.get_default()
            config.config_dir = config_dir
            config.bottles_dir = Path(tmpdir) / "bottles"
            config.default_runner = "proton-ge"
            config.save()

            loaded = AppConfig.load()
            assert loaded.default_runner == "proton-ge"
            assert loaded.bottles_dir == Path(tmpdir) / "bottles"

    def test_ensure_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = AppConfig.get_default()
            config.config_dir = Path(tmpdir) / "config"
            config.bottles_dir = Path(tmpdir) / "bottles"
            config.runners_dir = Path(tmpdir) / "runners"
            config.backups_dir = Path(tmpdir) / "backups"
            config.ensure_dirs()

            assert config.config_dir.exists()
            assert config.bottles_dir.exists()
            assert config.runners_dir.exists()
            assert config.backups_dir.exists()


class TestRunnerInfo:
    def test_creation(self):
        runner = RunnerInfo(
            name="Test Runner",
            version="9.0",
            runner_type=RunnerType.PROTON_GE,
            path=Path("/opt/proton"),
            description="Proton-GE 9.0",
            size_mb=1024.5
        )

        assert runner.name == "Test Runner"
        assert runner.version == "9.0"
        assert runner.runner_type == RunnerType.PROTON_GE


if __name__ == "__main__":
    pytest.main([__file__, "-v"])