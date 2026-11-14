"""Winetricks Service - Manage winetricks verbs and dependencies"""
import subprocess
from pathlib import Path
from typing import Optional
from ..models import WinePrefix
from dataclasses import dataclass


class WinetricksService:
    """Service for managing winetricks verbs in Wine prefixes"""

    VERBS = {
        "libraries": [
            "vcrun2019", "vcrun2015", "vcrun2013", "vcrun2012", "vcrun2010",
            "vcrun2008", "vcrun2005", "vcrun6sp6",
            "dotnet48", "dotnet472", "dotnet471", "dotnet47", "dotnet462",
            "dotnet461", "dotnet46", "dotnet45", "dotnet40", "dotnet35",
            "dotnet30", "dotnet20", "dotnet11",
            "dxvk", "vkd3d",
            "d3dcompiler_47", "d3dx9", "d3dx10", "d3dx11",
            "xact", "xaudio", "xinput",
            "gdiplus", "riched20", "riched30",
            "msxml3", "msxml4", "msxml6",
            "corefonts", "tahoma", "cjkfonts",
        ],
        "settings": [
            "win10", "win81", "win8", "win7", "vista", "xp",
            "sandbox", "isolate_home",
            "virtualdesktop", "novirtualdesktop",
            "sound=pulse", "sound=alsa", "sound=oss",
            "glsl=enabled", "glsl=disabled",
            "renderer=gdi", "renderer=opengl", "renderer=vulkan",
        ],
        "apps": [
            "steam", "lutris", "heroic", "battle.net", "origin",
            "epicgames", "gog", "ubisoftconnect",
        ],
    }

    def __init__(self):
        self._winetricks_path = self._find_winetricks()

    def _find_winetricks(self) -> Optional[Path]:
        """Find winetricks executable"""
        import shutil
        paths = [
            shutil.which("winetricks"),
            Path("/usr/bin/winetricks"),
            Path("/usr/local/bin/winetricks"),
            Path.home() / ".local" / "bin" / "winetricks",
        ]
        for p in paths:
            if p and Path(p).exists():
                return Path(p)
        return None

    @property
    def available(self) -> bool:
        return self._winetricks_path is not None

    def get_verbs(self, category: str = None) -> list[str]:
        """Get available verbs, optionally filtered by category"""
        if category and category in self.VERBS:
            return self.VERBS[category]
        all_verbs = []
        for verbs in self.VERBS.values():
            all_verbs.extend(verbs)
        return sorted(set(all_verbs))

    def get_categories(self) -> list[str]:
        return list(self.VERBS.keys())

    def run_verb(self, prefix: WinePrefix, verb: str, args: list[str] = None):
        """Run a winetricks verb in a prefix"""
        if not self.available:
            return WinetricksResult(False, "", "winetricks not found")

        cmd = [str(self._winetricks_path), "--unattended", verb]
        if args:
            cmd.extend(args)

        env = prefix.get_env()

        try:
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300,
            )
            return WinetricksResult(
                result.returncode == 0,
                result.stdout,
                result.stderr
            )
        except subprocess.TimeoutExpired:
            return WinetricksResult(False, "", "Timeout: winetricks took too long")
        except Exception as e:
            return WinetricksResult(False, "", str(e))

    def run_verbs(self, prefix: WinePrefix, verbs: list[str]) -> list:
        """Run multiple verbs sequentially"""
        results = []
        for verb in verbs:
            result = self.run_verb(prefix, verb)
            results.append(result)
            if not result.success:
                break
        return results

    def list_installed(self, prefix: WinePrefix) -> list[str]:
        """List installed verbs in a prefix"""
        if not self.available:
            return []

        cmd = [str(self._winetricks_path), "list-installed"]
        env = prefix.get_env()

        try:
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return [line.strip() for line in result.stdout.splitlines() if line.strip()]
        except Exception:
            pass
        return []

    def uninstall_verb(self, prefix: WinePrefix, verb: str):
        """Uninstall a verb"""
        if not self.available:
            return WinetricksResult(False, "", "winetricks not found")

        cmd = [str(self._winetricks_path), "--unattended", "uninstall", verb]
        env = prefix.get_env()

        try:
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
            )
            return WinetricksResult(
                result.returncode == 0,
                result.stdout,
                result.stderr
            )
        except Exception as e:
            return WinetricksResult(False, "", str(e))

    def get_verb_info(self, verb: str) -> dict:
        """Get information about a verb"""
        if not self.available:
            return {}

        cmd = [str(self._winetricks_path), "info", verb]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                info = {"name": verb, "description": "", "sha256": "", "size": ""}
                for line in result.stdout.splitlines():
                    if ":" in line:
                        key, value = line.split(":", 1)
                        info[key.strip().lower()] = value.strip()
                return info
        except Exception:
            pass
        return {}


@dataclass
class WinetricksResult:
    """Result of a winetricks operation"""
    success: bool
    stdout: str
    stderr: str

    @property
    def output(self) -> str:
        return self.stdout + self.stderr

    def __bool__(self) -> bool:
        return self.success