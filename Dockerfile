# Wine Launcher - Dockerfile
# Multi-stage build: builder -> runtime
# Usage: docker build -t wine-launcher . && docker run --rm -it -v $HOME/.wine-launcher:/data wine-launcher

# =============================================================================
# STAGE 1: Builder - Compile PyInstaller binary
# =============================================================================
FROM python:3.11-slim AS builder

# Install system dependencies for PyInstaller + Wine runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    wine64 wine32 winetricks \
    libgl1-mesa-glx libegl1-mesa \
    libxcb-xinerama0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
    libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-xfixes0 \
    libxcb-xkb1 libxkbcommon-x11-0 libxkbcommon0 \
    libfontconfig1 libfreetype6 libglib2.0-0 libharfbuzz0b \
    libice6 libsm6 libx11-6 libx11-xcb1 libxcb1 libxext6 \
    libxfixes3 libxi6 libxrender1 libxtst6 zlib1g \
    patchelf gcc musl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up Wine
RUN wineboot --init || true

WORKDIR /app

# Copy project
COPY requirements.txt .
COPY main.py .
COPY models/ ./models/
COPY services/ ./services/
COPY controllers/ ./controllers/
COPY views/ ./views/

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt pyinstaller

# Build standalone binary
RUN python -m PyInstaller --onefile --windowed --name wine-launcher main.py

# Verify binary
RUN file dist/wine-launcher && ldd dist/wine-launcher | grep -v "not found" || true


# =============================================================================
# STAGE 2: Runtime - Minimal image with binary + Wine
# =============================================================================
FROM debian:bookworm-slim AS runtime

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    wine64 wine32 winetricks \
    libgl1-mesa-glx libegl1-mesa \
    libxcb-xinerama0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
    libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-xfixes0 \
    libxcb-xkb1 libxkbcommon-x11-0 libxkbcommon0 \
    libfontconfig1 libfreetype6 libglib2.0-0 libharfbuzz0b \
    libice6 libsm6 libx11-6 libx11-xcb1 libxcb1 libxext6 \
    libxfixes3 libxi6 libxrender1 libxtst6 zlib1g \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
ARG UID=1000
ARG GID=1000
RUN groupadd -g ${GID} winelauncher && \
    useradd -m -u ${UID} -g ${GID} -s /bin/bash winelauncher

# Copy binary from builder
COPY --from=builder /app/dist/wine-launcher /usr/local/bin/wine-launcher
RUN chmod +x /usr/local/bin/wine-launcher

# Create directories
RUN mkdir -p /home/winelauncher/.config/wine-launcher \
             /home/winelauncher/.local/share/wine-launcher/bottles \
             /home/winelauncher/.local/share/wine-launcher/backups \
             /home/winelauncher/.local/share/wine-launcher/runners \
             /home/winelauncher/.cache/wine \
    && chown -R winelauncher:winelauncher /home/winelauncher

# Switch to non-root
USER winelauncher
WORKDIR /home/winelauncher

# Environment
ENV WINEPREFIX=/home/winelauncher/.local/share/wine-launcher/bottles/default
ENV WINEDLLOVERRIDES="mscoree,mshtml="
ENV QT_QPA_PLATFORM=xcb

# Initialize Wine prefix on first run
RUN wineboot --init 2>/dev/null || true

# Entrypoint
ENTRYPOINT ["wine-launcher"]

# Default command (can be overridden)
CMD []

# Labels
LABEL org.opencontainers.image.title="Wine Launcher"
LABEL org.opencontainers.image.description="Run Windows apps on Linux with Wine/Proton"
LABEL org.opencontainers.image.version="0.1.0"
LABEL org.opencontainers.image.source="https://github.com/Vic01107/wine-launcher"
LABEL org.opencontainers.image.licenses="MIT"