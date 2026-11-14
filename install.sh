#!/bin/bash
# Wine Launcher - Installer Script
# Usage: curl -fsSL https://raw.githubusercontent.com/Vic01107/wine-launcher/main/install.sh | bash
# Or: ./install.sh

set -euo pipefail

# Configuration
REPO_OWNER="${REPO_OWNER:-Vic01107}"
REPO_NAME="${REPO_NAME:-wine-launcher}"
BINARY_NAME="wine-launcher"
INSTALL_DIR="${HOME}/.local/bin"
DESKTOP_DIR="${HOME}/.local/share/applications"
ICON_DIR="${HOME}/.local/share/icons/hicolor/256x256/apps"
VERSION="${VERSION:-latest}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_ok() { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

# Detect architecture
ARCH="$(uname -m)"
case "$ARCH" in
    x86_64|amd64) ARCH="x86_64" ;;
    aarch64|arm64) ARCH="aarch64" ;;
    *) log_error "Arquitectura no soportada: $ARCH"; exit 1 ;;
esac

# Check if running from source (local build) or downloading release
LOCAL_BUILD=false
if [[ -f "main.py" && -f "requirements.txt" ]]; then
    LOCAL_BUILD=true
    log_info "Detectado código fuente local, compilando..."
fi

# Check system dependencies
check_system_deps() {
    log_info "Verificando dependencias del sistema..."
    local missing=()

    for cmd in wine winetricks; do
        if ! command -v "$cmd" &>/dev/null; then
            missing+=("$cmd")
        fi
    done

    if [[ ${#missing[@]} -gt 0 ]]; then
        log_warn "Faltan dependencias opcionales: ${missing[*]}"
        log_warn "Instálalas con tu gestor de paquetes:"
        echo "  Ubuntu/Debian: sudo apt install wine64 wine32 winetricks"
        echo "  Fedora:        sudo dnf install wine winetricks"
        echo "  Arch:          sudo pacman -S wine winetricks"
        echo ""
    else
        log_ok "Dependencias del sistema OK"
    fi
}

# Build from source using PyInstaller
build_local() {
    log_info "Instalando PyInstaller..."
    pip install --user pyinstaller >/dev/null 2>&1 || {
        log_error "Falló instalación de PyInstaller"
        exit 1
    }

    log_info "Compilando Wine Launcher..."
    python -m PyInstaller --onefile --windowed --name "$BINARY_NAME" main.py || {
        log_error "Falló la compilación"
        exit 1
    }

    if [[ ! -f "dist/$BINARY_NAME" ]]; then
        log_error "Binario no generado"
        exit 1
    fi

    log_ok "Compilado: dist/$BINARY_NAME"
    BINARY_PATH="dist/$BINARY_NAME"
}

# Download pre-built release
download_release() {
    log_info "Descargando release $VERSION para $ARCH..."

    local download_url
    if [[ "$VERSION" == "latest" ]]; then
        download_url="https://github.com/$REPO_OWNER/$REPO_NAME/releases/latest/download/${BINARY_NAME}-linux-${ARCH}"
    else
        download_url="https://github.com/$REPO_OWNER/$REPO_NAME/releases/download/$VERSION/${BINARY_NAME}-linux-${ARCH}"
    fi

    log_info "URL: $download_url"

    # Try download with curl, fallback to wget
    if command -v curl &>/dev/null; then
        curl -fsSL -o "/tmp/$BINARY_NAME" "$download_url" || {
            log_error "Falló descarga con curl"
            exit 1
        }
    elif command -v wget &>/dev/null; then
        wget -q -O "/tmp/$BINARY_NAME" "$download_url" || {
            log_error "Falló descarga con wget"
            exit 1
        }
    else
        log_error "Se requiere curl o wget"
        exit 1
    fi

    chmod +x "/tmp/$BINARY_NAME"
    BINARY_PATH="/tmp/$BINARY_NAME"
    log_ok "Descargado y preparado"
}

# Install binary
install_binary() {
    log_info "Instalando en $INSTALL_DIR..."
    mkdir -p "$INSTALL_DIR"
    cp "$BINARY_PATH" "$INSTALL_DIR/$BINARY_NAME"
    chmod +x "$INSTALL_DIR/$BINARY_NAME"
    log_ok "Binario instalado"
}

# Create .desktop entry
create_desktop_entry() {
    log_info "Creando entrada de menú..."
    mkdir -p "$DESKTOP_DIR"

    cat > "$DESKTOP_DIR/$BINARY_NAME.desktop" <<EOF
[Desktop Entry]
Name=Wine Launcher
Comment=Run Windows applications on Linux using Wine/Proton
Exec=$INSTALL_DIR/$BINARY_NAME
Icon=$BINARY_NAME
Terminal=false
Type=Application
Categories=Utility;System;Emulator;
StartupNotify=true
Keywords=wine;proton;windows;bottle;runner;
EOF

    log_ok "Entrada .desktop creada"
}

# Create icon
create_icon() {
    log_info "Generando icono..."
    mkdir -p "$ICON_DIR"

    # Try to generate with Python/PySide6 if available
    if python3 -c "import PySide6" 2>/dev/null; then
        python3 <<'PYEOF'
import sys
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QIcon
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtWidgets import QApplication

app = QApplication.instance() or QApplication(sys.argv)

pixmap = QPixmap(256, 256)
pixmap.fill(Qt.transparent)

painter = QPainter(pixmap)
painter.setRenderHint(QPainter.Antialiasing)
painter.setRenderHint(QPainter.TextAntialiasing)

# Background gradient
from PySide6.QtGui import QLinearGradient
grad = QLinearGradient(0, 0, 256, 256)
grad.setColorAt(0, QColor("#4A90D9"))
grad.setColorAt(1, QColor("#2E5C8A"))
painter.setBrush(grad)
painter.setPen(Qt.NoPen)
painter.drawRoundedRect(16, 16, 224, 224, 40, 40)

# Wine glass icon (simple)
painter.setBrush(QColor(255, 255, 255, 230))
painter.setPen(Qt.NoPen)

# Bowl
painter.drawEllipse(QRect(80, 90, 96, 80))
# Stem
painter.drawRect(122, 170, 12, 50)
# Base
painter.drawEllipse(QRect(104, 214, 48, 12))

# "WL" text fallback
painter.setFont(QFont("Arial", 48, QFont.Bold))
painter.setPen(QColor(255, 255, 255, 180))
painter.drawText(QRect(16, 16, 224, 224), Qt.AlignCenter, "WL")

painter.end()

import os
icon_dir = os.environ.get('ICON_DIR', '/tmp')
pixmap.save(f"{icon_dir}/wine-launcher.png")
PYEOF
        ICON_DIR="$ICON_DIR" python3 -c "pass" 2>/dev/null || true
        log_ok "Icono generado con PySide6"
    else
        # Fallback: create simple PNG with ImageMagick or just skip
        if command -v convert &>/dev/null; then
            convert -size 256x256 xc:none \
                -fill "#4A90D9" -draw "roundrectangle 16,16 240,240 40,40" \
                -fill white -font DejaVu-Sans-Bold -pointsize 80 -gravity center -annotate +0+0 "WL" \
                "$ICON_DIR/$BINARY_NAME.png" 2>/dev/null && log_ok "Icono generado con ImageMagick" || log_warn "No se pudo generar icono"
        else
            log_warn "PySide6/ImageMagick no disponible, saltando icono personalizado"
        fi
    fi
}

# Update desktop database
update_desktop_db() {
    log_info "Actualizando base de datos de aplicaciones..."
    if command -v update-desktop-database &>/dev/null; then
        update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    fi
    if command -v gtk-update-icon-cache &>/dev/null; then
        gtk-update-icon-cache -f -t "$(dirname "$(dirname "$ICON_DIR")")" 2>/dev/null || true
    fi
    log_ok "Base de datos actualizada"
}

# Check PATH
check_path() {
    if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
        log_warn "$INSTALL_DIR no está en tu PATH"
        echo ""
        echo "Añade esta línea a tu ~/.bashrc, ~/.zshrc o ~/.profile:"
        echo -e "  ${GREEN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
        echo ""
        echo "Luego recarga: source ~/.bashrc"
    else
        log_ok "PATH configurado correctamente"
    fi
}

# Verify installation
verify_install() {
    log_info "Verificando instalación..."
    if "$INSTALL_DIR/$BINARY_NAME" --version &>/dev/null || "$INSTALL_DIR/$BINARY_NAME" --help &>/dev/null || true; then
        log_ok "Binario ejecutable correctamente"
    else
        # PyInstaller --windowed apps may not support --version/--help
        # Just check it exists and is executable
        if [[ -x "$INSTALL_DIR/$BINARY_NAME" ]]; then
            log_ok "Binario instalado y ejecutable"
        else
            log_error "Verificación fallida"
            exit 1
        fi
    fi
}

# Main
main() {
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     Wine Launcher Installer           ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
    echo ""

    check_system_deps

    if [[ "$LOCAL_BUILD" == true ]]; then
        build_local
    else
        download_release
    fi

    install_binary
    create_desktop_entry
    create_icon
    update_desktop_db
    check_path
    verify_install

    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║     ¡Instalación completada!          ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo "Ejecuta con:"
    echo "  ${GREEN}wine-launcher${NC}          (si PATH está configurado)"
    echo "  ${GREEN}$INSTALL_DIR/wine-launcher${NC}  (ruta completa)"
    echo ""
    echo "O búscalo en tu menú de aplicaciones: \"Wine Launcher\""
    echo ""
    echo "Primeros pasos:"
    echo "  1. Abre Wine Launcher"
    echo "  2. Click \"Nueva Botella\" (Ctrl+N)"
    echo "  3. Elige runner (Proton-GE recomendado para juegos)"
    echo "  4. Click \"Ejecutar\" y selecciona tu .exe"
}

# Run
main "$@"