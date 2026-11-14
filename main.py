#!/usr/bin/env python3
"""Wine Launcher - Main entry point"""
import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QCoreApplication

from controllers import MainController
from views import MainWindow
from models import AppConfig


__version__ = "0.1.0"


def parse_args():
    parser = argparse.ArgumentParser(description="Wine Launcher - Run Windows apps on Linux")
    parser.add_argument("--version", action="version", version=f"Wine Launcher {__version__}")
    parser.add_argument("--help", action="help", help="Show this help message and exit")
    return parser.parse_args()


def main():
    parse_args()  # Handle --version/--help before Qt init

    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Wine Launcher")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("WineLauncher")

    # Load configuration
    config = AppConfig.load()
    config.ensure_dirs()

    # Create main controller
    controller = MainController(config)
    if not controller.initialize():
        print("Error: Failed to initialize application", file=sys.stderr)
        return 1

    # Create and show main window
    window = MainWindow(controller)
    window.show()

    # Run application
    try:
        return app.exec()
    finally:
        controller.shutdown()


if __name__ == "__main__":
    sys.exit(main())