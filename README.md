# Wine Launcher

A Linux application for running Windows applications using Wine/Proton, built with Python and PySide6 (Qt 6) using MVC architecture.

[![Release](https://img.shields.io/github/v/release/Vic01107/wine-launcher)](https://github.com/Vic01107/wine-launcher/releases)
[![License](https://img.shields.io/github/license/Vic01107/wine-launcher)](https://github.com/Vic01107/wine-launcher/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![Build](https://github.com/Vic01107/wine-launcher/actions/workflows/build.yml/badge.svg)](https://github.com/Vic01107/wine-launcher/actions)

## Features

- **MVC Architecture** - Clean separation of Model, View, and Controller layers
- **Multiple Runner Support** - System Wine, Steam Proton, Proton-GE, Wine-GE (Lutris), Custom runners
- **Bottle Management** - Isolated Wine prefixes per application ("bottles")
- **Winetricks Integration** - Easy installation of Windows dependencies (vcrun, dotnet, DXVK, etc.)
- **Graphics Layers** - DXVK, VKD3D, dgVoodoo2 support
- **Backup/Restore** - Tarball-based bottle backup and restore
- **Environment Variables** - Per-bottle environment configuration
- **Modern UI** - PySide6/Qt 6 with split-view layout

## Architecture

```
wine-launcher/
├── main.py                 # Entry point
├── models/                 # Data models
│   ├── __init__.py
│   ├── wine_prefix.py      # Wine prefix management
│   ├── bottle.py           # Bottle (prefix + apps + config)
│   └── app_config.py       # Global configuration
├── services/               # Business logic
│   ├── __init__.py
│   ├── runner_manager.py   # Runner detection
│   ├── bottle_service.py   # Bottle CRUD operations
│   └── winetricks_service.py # Winetricks integration
├── controllers/            # Application logic
│   ├── __init__.py
│   ├── main_controller.py  # Main coordinator
│   ├── bottle_controller.py
│   ├── runner_controller.py
│   └── settings_controller.py
└── views/                  # PySide6 UI
    ├── __init__.py
    ├── main_window.py      # Main window with splitter
    ├── bottle_list.py      # Bottle list panel
    ├── bottle_detail.py    # Bottle detail tabs
    ├── create_bottle_dialog.py
    ├── run_dialog.py
    └── settings_dialog.py
```

## Requirements

- Linux (tested on Ubuntu 22.04+, Fedora 38+, Arch)
- Python 3.10+
- Wine 8.0+ or Proton
- winetricks (optional, for dependencies)

### Python Dependencies

```bash
pip install -r requirements.txt
```

- PySide6 >= 6.6.0
- psutil >= 5.9.0
- python-dotenv >= 1.0.0

## Installation

### Quick Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/Vic01107/wine-launcher/main/install.sh | bash
```

### From Source

```bash
git clone https://github.com/Vic01107/wine-launcher.git
cd wine-launcher
pip install -r requirements.txt
python main.py
```

## Usage

### Creating a Bottle

1. Click **New Bottle** (Ctrl+N) or File -> New Bottle
2. Enter a name and optional description
3. Choose architecture (win64/win32)
4. Select runner type (auto-detects available runners)
5. Click OK - the bottle prefix will be created

### Running Applications

1. Select a bottle from the list
2. Click **Run App** (Ctrl+R) to run an installed app
3. Or click **Run Executable** (Ctrl+E) for a custom .exe

### Installing Windows Dependencies (Winetricks)

1. Select a bottle
2. Click **Winetricks** (Ctrl+W) or Bottle -> Winetricks
3. Choose a category (libraries, settings, apps)
4. Select verb(s) and click Install

### Managing Bottles

- **Backup**: File -> Backup Bottle (Ctrl+B)
- **Restore**: File -> Restore Bottle
- **Delete**: Right-click bottle -> Delete, or Bottle -> Delete Bottle

### Settings

File -> Settings (Ctrl+,) to configure:
- Directory paths (config, bottles, runners, backups)
- Default runner and architecture
- UI theme, font size, language
- Advanced options (auto-refresh, confirmations, etc.)

## Runner Types

| Type | Description | Priority |
|------|-------------|----------|
| `proton` | Steam Proton (compatibilitytools.d) | 1 |
| `proton-ge` | Proton-GE custom builds | 2 |
| `wine-ge` | Wine-GE (Lutris, manual) | 3 |
| `system-wine` | System package Wine | 4 |
| `custom` | User-added runners | 5 |

## Winetricks Verbs

Common verbs by category:

**Libraries:**
- `vcrun2019`, `vcrun2015`, `vcrun2013`, `vcrun2012`, `vcrun2010`
- `dotnet48`, `dotnet472`, `dotnet462`, `dotnet45`, `dotnet40`, `dotnet35`
- `dxvk`, `vkd3d`
- `d3dcompiler_47`, `d3dx9`, `d3dx11`
- `corefonts`, `tahoma`

**Settings:**
- `win10`, `win7`, `xp` (Windows version)
- `virtualdesktop`, `novirtualdesktop`
- `sound=pulse`, `sound=alsa`
- `renderer=vulkan`, `renderer=opengl`

**Apps:**
- `steam`, `lutris`, `heroic`, `battle.net`, `epicgames`, `gog`

## Configuration

Config file: `~/.config/wine-launcher/config.json`

```json
{
  "config_dir": "~/.config/wine-launcher",
  "bottles_dir": "~/.local/share/wine-launcher/bottles",
  "runners_dir": "~/.local/share/wine-launcher/runners",
  "backups_dir": "~/.local/share/wine-launcher/backups",
  "default_runner": "proton-ge",
  "default_arch": "win64",
  "ui_theme": "System",
  "show_statusbar": true,
  "show_tooltips": true,
  "remember_geometry": true,
  "font_size": 10,
  "auto_refresh_interval": 30,
  "max_log_lines": 1000,
  "confirm_delete": true,
  "close_to_tray": false,
  "start_minimized": false,
  "wine_debug": false
}
```

## Building from Source

```bash
# Install build dependencies
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed main.py

# Output in dist/
```

## Troubleshooting

### Wine not found
Install Wine from your distribution:
- Ubuntu/Debian: `sudo apt install wine64 wine32`
- Fedora: `sudo dnf install wine`
- Arch: `sudo pacman -S wine`

### winetricks not found
```bash
sudo apt install winetricks  # Ubuntu/Debian
sudo dnf install winetricks  # Fedora
```

### Proton not detected
Ensure Steam is installed and Proton is downloaded in Steam settings, or install Proton-GE manually:
```bash
# Download from GitHub releases
# Extract to ~/.steam/steam/compatibilitytools.d/
```

### Permission errors
Ensure your user is in the appropriate groups and directories are writable.

## License

MIT License - see LICENSE file

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following MVC pattern
4. Ensure all Python files compile (`python -m py_compile`)
5. Submit PR

## Roadmap

- [ ] Desktop entry creation for apps
- [ ] Bottle templates (gaming, office, development)
- [ ] DXVK/VKD3D version management
- [ ] Vulkan ICD loader selection
- [ ] Game-specific profiles
- [ ] Steam integration (auto-detect Steam games)
- [ ] Bottle sharing/export
- [ ] Logging viewer
- [ ] System tray support