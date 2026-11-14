#!/bin/bash
# Wine Launcher - Uninstaller Script
# Usage: curl -fsSL https://raw.githubusercontent.com/Vic01107/wine-launcher/main/uninstall.sh | bash
# Or: ./uninstall.sh

set -euo pipefail

BINARY_NAME="wine-launcher"
INSTALL_DIR="${HOME}/.local/bin"
DESKTOP_DIR="${HOME}/.local/share/applications"
ICON_DIR="${HOME}/.local/share/icons/hicolor/256x256/apps"
CONFIG_DIR="${HOME}/.config/wine-launcher"
DATA_DIR="${HOME}/.local/share/wine-launcher"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_ok() { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

confirm() {
    local prompt="${1:-¿Estás seguro?}"
    read -r -p "$prompt [y/N] " response
    [[ "$response" =~ ^[Yy]$ ]]
}

main() {
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║    Wine Launcher Uninstaller          ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
    echo ""

    # Check what's installed
    local found=()
    [[ -f "$INSTALL_DIR/$BINARY_NAME" ]] && found+=("binario: $INSTALL_DIR/$BINARY_NAME")
    [[ -f "$DESKTOP_DIR/$BINARY_NAME.desktop" ]] && found+=("entrada .desktop: $DESKTOP_DIR/$BINARY_NAME.desktop")
    [[ -f "$ICON_DIR/$BINARY_NAME.png" ]] && found+=("icono: $ICON_DIR/$BINARY_NAME.png")
    [[ -d "$CONFIG_DIR" ]] && found+=("config: $CONFIG_DIR")
    [[ -d "$DATA_DIR" ]] && found+=("datos (botellas/backups): $DATA_DIR")

    if [[ ${#found[@]} -eq 0 ]]; then
        log_info "Nada que desinstalar. Wine Launcher no encontrado."
        exit 0
    fi

    echo "Se encontró lo siguiente:"
    for item in "${found[@]}"; do
        echo "  • $item"
    done
    echo ""

    # Remove binary + desktop + icon (always)
    if confirm "¿Eliminar binario, entrada de menú e icono?"; then
        rm -f "$INSTALL_DIR/$BINARY_NAME"
        rm -f "$DESKTOP_DIR/$BINARY_NAME.desktop"
        rm -f "$ICON_DIR/$BINARY_NAME.png"
        log_ok "Binario, .desktop e icono eliminados"

        # Update desktop database
        command -v update-desktop-database &>/dev/null && update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
        command -v gtk-update-icon-cache &>/dev/null && gtk-update-icon-cache -f -t "$(dirname "$(dirname "$ICON_DIR")")" 2>/dev/null || true
    fi

    # Remove config (optional)
    if [[ -d "$CONFIG_DIR" ]] && confirm "¿Eliminar configuración ($CONFIG_DIR)?"; then
        rm -rf "$CONFIG_DIR"
        log_ok "Configuración eliminada"
    fi

    # Remove data/bottles (optional - destructive!)
    if [[ -d "$DATA_DIR" ]] && confirm "¿ELIMINAR TODAS LAS BOTELLAS Y BACKUPS ($DATA_DIR)? ¡IRREVERSIBLE!"; then
        if confirm "¿ESTÁS COMPLETAMENTE SEGURO? Se borrarán todos tus prefijos Wine y backups."; then
            rm -rf "$DATA_DIR"
            log_ok "Datos eliminados"
        else
            log_info "Datos conservados en $DATA_DIR"
        fi
    fi

    echo ""
    log_ok "Desinstalación completada"
    echo ""
    echo "Para reinstalar:"
    echo "  curl -fsSL https://raw.githubusercontent.com/Vic01107/wine-launcher/main/install.sh | bash"
}

main "$@"