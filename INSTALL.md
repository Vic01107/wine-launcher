# Guía de Instalación - Wine Launcher

> Ejecuta aplicaciones Windows (.exe) en Linux de forma nativa con interfaz gráfica.

---

## Requisitos Previos (Obligatorios)

Wine Launcher **requiere Wine/Proton instalado en tu sistema**. La app solo gestiona y lanza; el motor de compatibilidad es Wine.

### Ubuntu / Debian / Linux Mint / Pop!_OS

```bash
# 1. Habilitar arquitectura 32-bit (necesario para muchas apps/juegos)
sudo dpkg --add-architecture i386
sudo apt update

# 2. Instalar Wine + winetricks
sudo apt install wine64 wine32 winetricks

# 3. Verificar
wine --version
winetricks --version
```

### Fedora / RHEL / CentOS / AlmaLinux

```bash
sudo dnf install wine wine-core wine-common winetricks
# Para 32-bit:
sudo dnf install wine.i686
```

### Arch Linux / Manjaro / EndeavourOS

```bash
sudo pacman -S wine winetricks
# Para 32-bit (multilib debe estar habilitado en /etc/pacman.conf):
sudo pacman -S lib32-wine
```

### openSUSE

```bash
sudo zypper install wine winetricks
```

### Para Juegos (Recomendado: Proton-GE)

```bash
# Opción A: Descargar manualmente
mkdir -p ~/.steam/steam/compatibilitytools.d
cd ~/.steam/steam/compatibilitytools.d
wget https://github.com/GloriousEggroll/proton-ge-custom/releases/download/GE-Proton9-21/GE-Proton9-21.tar.gz
tar -xzf GE-Proton9-21.tar.gz

# Opción B: Usar ProtonUp-Qt (GUI)
flatpak install flathub com.vysp3r.ProtonUpQt
# Abre ProtonUp-Qt → "Add version" → Proton-GE → Install
```

---

## Métodos de Instalación de Wine Launcher

### Método 1: Instalador Automático (Recomendado)

```bash
# Una sola línea - detecta tu arquitectura, descarga release o compila local
curl -fsSL https://raw.githubusercontent.com/Vic01107/wine-launcher/main/install.sh | bash
```

**Qué hace:**
- ✅ Verifica `wine` y `winetricks`
- ✅ Descarga binario pre-compilado (x86_64/ARM64) o compila local
- ✅ Instala en `~/.local/bin/wine-launcher`
- ✅ Crea entrada en menú de aplicaciones
- ✅ Genera icono

---

### Método 2: Binario Pre-compilado (Manual)

```bash
# 1. Descargar (cambia x86_64 por aarch64 si eres ARM)
wget https://github.com/Vic01107/wine-launcher/releases/latest/download/wine-launcher-linux-x86_64

# 2. Dar permisos
chmod +x wine-launcher-linux-x86_64

# 3. Ejecutar
./wine-launcher-linux-x86_64

# 4. Opcional: mover a PATH
mv wine-launcher-linux-x86_64 ~/.local/bin/wine-launcher
```

---

### Método 3: AppImage (Portable, Universal)

```bash
wget https://github.com/Vic01107/wine-launcher/releases/latest/download/wine-launcher-linux-x86_64.AppImage
chmod +x wine-launcher-linux-x86_64.AppImage
./wine-launcher-linux-x86_64.AppImage
```

---

### Método 4: Compilar desde Código Fuente

```bash
# 1. Clonar repo
git clone https://github.com/Vic01107/wine-launcher.git
cd wine-launcher

# 2. Instalar dependencias Python
pip install --user -r requirements.txt
# PySide6>=6.6.0, psutil>=5.9.0, python-dotenv>=1.0.0

# 3. Ejecutar directamente (desarrollo)
python main.py

# 4. O compilar binario standalone
pip install --user pyinstaller
python -m PyInstaller --onefile --windowed --name wine-launcher main.py
# Resultado en: dist/wine-launcher
```

---

### Método 5: Flatpak (Próximamente)

```bash
# Cuando esté disponible en Flathub
flatpak install flathub com.tuusuario.WineLauncher
```

---

## Post-Instalación

### 1. Verificar PATH

```bash
# Comprobar que ~/.local/bin está en PATH
echo $PATH | grep -q "$HOME/.local/bin" && echo "✅ OK" || echo "❌ FALTA"

# Si falta, añade a tu ~/.bashrc o ~/.zshrc:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 2. Primera Ejecución

```bash
wine-launcher
# O búscalo en el menú: "Wine Launcher"
```

Verás la ventana principal vacía. ¡Es normal!

---

## Primeros Pasos (Crear tu Primera Botella)

### 1. Click **"Nueva Botella"** (Ctrl+N)

```
┌─────────────────────────────────────┐
│ Nombre:        MiJuego              │
│ Descripción:   Elden Ring           │
│ Arquitectura:  win64  ◄── (64-bit)  │
│ Runner:        Proton-GE 9.21       │
└─────────────────────────────────────┘
```

### 2. Click **"Ejecutar"** (Ctrl+R o Ctrl+E)

- **Run App (Ctrl+R)**: Apps ya instaladas en la botella
- **Run Executable (Ctrl+E)**: Instaladores `.exe`, portables, etc.

### 3. Instalar Dependencias (Winetricks)

```
Botella → Winetricks (Ctrl+W)
  → libraries → vcrun2019, dxvk, dotnet48
  → settings  → win10, virtualdesktop
```

---

## Estructura de Directorios

```
~/.config/wine-launcher/          # Configuración global (config.json)
~/.local/share/wine-launcher/
├── bottles/                      # Prefijos Wine (una carpeta por botella)
│   └── MiJuego/
│       ├── drive_c/              # C: virtual
│       ├── user.reg              # Registro HKCU
│       └── system.reg            # Registro HKLM
├── runners/                      # Runners personalizados (opcional)
└── backups/                      # Backups .tar.gz
```

---

## Desinstalación

```bash
# Binario + entry .desktop + icono
rm ~/.local/bin/wine-launcher
rm ~/.local/share/applications/wine-launcher.desktop
rm ~/.local/share/icons/hicolor/256x256/apps/wine-launcher.png

# Configuración y botellas (OPCIONAL - borra todo)
rm -rf ~/.config/wine-launcher
rm -rf ~/.local/share/wine-launcher
```

---

## Solución de Problemas

| Problema | Solución |
|----------|----------|
| `wine: command not found` | Instala Wine (ver requisitos previos) |
| `winetricks: command not found` | `sudo apt install winetricks` |
| Error "Wine prefix not found" | Recrea la botella (botón derecho → Eliminar → Nueva) |
| App no inicia | Prueba otro runner (Proton-GE → System Wine) |
| Error 32-bit | `sudo dpkg --add-architecture i386 && sudo apt update && sudo apt install wine32` |
| Sin audio | `sudo apt install libpulse0:i386` (Ubuntu) |
| Ventana negra / crash | Activa **Virtual Desktop** en pestaña Config → Winetricks → virtualdesktop |
| Permisos denegados | `chmod +x wine-launcher` o ejecuta desde terminal para ver logs |

---

## Ver Logs / Depurar

```bash
# Ejecutar desde terminal para ver output
wine-launcher

# Con debug de Wine
WINEDEBUG=+all wine-launcher 2>&1 | tee wine.log

# Solo errores
WINEDEBUG=err+all wine-launcher
```

---

## Actualización

```bash
# Método 1: Re-ejecutar instalador
curl -fsSL https://raw.githubusercontent.com/Vic01107/wine-launcher/main/install.sh | bash

# Método 2: Descargar nuevo binario
wget -O ~/.local/bin/wine-launcher https://github.com/Vic01107/wine-launcher/releases/latest/download/wine-launcher-linux-x86_64
chmod +x ~/.local/bin/wine-launcher
```

---

## Enlaces Útiles

- **ProtonDB** (compatibilidad juegos): https://www.protondb.com
- **WineHQ AppDB**: https://appdb.winehq.org
- **Winetricks verbs**: https://github.com/Winetricks/winetricks
- **Proton-GE releases**: https://github.com/GloriousEggroll/proton-ge-custom/releases
- **Issues / Bugs**: https://github.com/Vic01107/wine-launcher/issues

---

## Licencia

MIT License - Código abierto, úsalo libremente.

---

*¿Problemas? Abre un issue en GitHub con: distro, versión Wine, log de error, y qué .exe intentas correr.*

---

## Capturas de Pantalla (Referencia Visual)

> **Nota**: Estas son representaciones ASCII de la UI real. La app usa Qt6 nativo.

### Ventana Principal

```
┌─────────────────────────────────────────────────────────────────────┐
│ Wine Launcher                                    [≣] [□] [×]       │
├─────────────────────────────────────────────────────────────────────┤
│ Archivo  Botella  Ayuda                                             │
├──────────────┬──────────────────────────────────────────────────────┤
│              │  ┌General│Apps│Config│Winetricks│Entorno│          │
│  BOTELLAS    │  │                                   │              │
│  ┌────────┐  │  │  Nombre:      Cyberpunk2077       │              │
│  │● Cyber │  │  │  Estado:      Detenido            │              │
│  │ punk207│  │  │  Arquitectura: win64              │              │
│  │ 7 Pro- │  │  │  Runner:      Proton-GE 9.21      │              │
│  │ ton-GE │  │  │  Prefijo:     ~/.local/.../Cyberp │              │
│  │ win64  │  │  │  Tamaño:      18.4 GB             │              │
│  ├────────┤  │  │  [✓] DXVK  [✓] VKD3D  [ ] dgVoodoo│              │
│  │● Office│  │  └───────────────────────────────────┘              │
│  │  System│  │  [Apps instaladas]                    [+] [▶] [🗑] │
│  │ Wine   │  │  ┌─────────────────────────────────────────────┐   │
│  │ win32  │  │  │ Cyberpunk2077.exe        drive_c/Games/CP77 │   │
│  ├────────┤  │  │ GOG Galaxy.exe           drive_c/GOG/       │   │
│  │● Steam │  │  └─────────────────────────────────────────────┘   │
│  │ Proton │  │                                                      │
│  │ 9.0    │  │                                                      │
│  └────────┘  │                                                      │
│  [Nueva]     │                                                      │
│              │                                                      │
└──────────────┴──────────────────────────────────────────────────────┘
```

### Diálogo Nueva Botella

```
┌────────────────────────────────────────┐
│        Crear Nueva Botella             │
├────────────────────────────────────────┤
│ Nombre:        [MiJuego______________] │
│ Descripción:   [____________________]  │
│                [____________________]  │
│ Arquitectura:  [win64 ▼]              │
│ Runner Type:   [proton-ge ▼]          │
│ Runner:        [Proton-GE 9.21 ▼]     │
│                [Auto-detect (Default)] │
├────────────────────────────────────────┤
│                    [Cancelar] [OK]     │
└────────────────────────────────────────┘
```

### Pestaña Winetricks

```
┌────────────────────────────────────────┐
│ Categoría: [libraries ▼]               │
├────────────────────────────────────────┤
│ ☐ vcrun2019       ☐ dotnet48           │
│ ☐ vcrun2015       ☐ dxvk               │
│ ☐ vcrun2013       ☐ vkd3d              │
│ ☐ d3dcompiler_47  ☐ corefonts          │
│ ☐ d3dx9           ☐ tahoma             │
│ ☐ xact            ☐ gdiplus            │
├────────────────────────────────────────┤
│  [Instalar Seleccionados] [Refrescar]  │
├────────────────────────────────────────┤
│ Instalados:                            │
│ • vcrun2019                            │
│ • dxvk                                 │
│ • win10                                │
└────────────────────────────────────────┘
```

---

## Flatpak (Guía Avanzada)

> Wine Launcher como Flatpak requiere permisos especiales para Wine. **No recomendado para juegos** por limitaciones de sandbox.

### Instalación (cuando esté en Flathub)

```bash
# Desde Flathub (futuro)
flatpak install flathub com.tuusuario.WineLauncher

# O desde archivo .flatpak local
flatpak install wine-launcher.flatpak
```

### Permisos Necesarios

```bash
# Dar acceso a archivos del usuario (donde están los .exe)
flatpak override --user --filesystem=home com.tuusuario.WineLauncher

# Acceso a Wine/Proton del sistema (complejo en Flatpak)
flatpak override --user --filesystem=/usr/bin/wine:ro com.tuusuario.WineLauncher
flatpak override --user --filesystem=/usr/lib/wine:ro com.tuusuario.WineLauncher
flatpak override --user --filesystem=/opt:ro com.tuusuario.WineLauncher  # Proton-GE

# GPU / Vulkan (para DXVK/VKD3D)
flatpak override --user --device=dri com.tuusuario.WineLauncher
flatpak override --user --env=VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/*.json com.tuusuario.WineLauncher
```

### Limitaciones Conocidas Flatpak

| Limitación | Impacto | Workaround |
|------------|---------|------------|
| Sandbox aisla Wine | No ve Wine del sistema | Usar Wine bundlado en Flatpak (aumenta tamaño ~300MB) |
| Sin acceso a `/opt` | Proton-GE no detectado | Bind-mount manual o ProtonUp-Qt Flatpak |
| Vulkan ICD | DXVK puede fallar | `--env=VK_ICD_FILENAMES=...` |
| Tamaño | ~500MB+ vs 50MB nativo | Usar binario nativo o AppImage |

**Recomendación**: Usa **binario nativo (Método 1/2)** o **AppImage**. Flatpak solo si tu distro lo requiere (Silverblue, Kinoite, Endless OS).

---

## Preguntas Frecuentes (FAQ)

### General

**P: ¿Es esto una máquina virtual?**
R: No. Wine/Proton traduce llamadas Windows a Linux en tiempo real. Sin overhead de VM.

**P: ¿Funciona mejor que Lutris/Bottles?**
R: Es alternativa minimalista. Lutris/Bottles tienen más features (scripts, DB online). Wine Launcher es más simple, MVC, hackeable.

**P: ¿Puedo usar mis botellas de Bottles/Lutris?**
R: Sí. Son solo prefijos Wine estándar. Apunta `~/.local/share/wine-launcher/bottles/` a tu carpeta existente o importa backup `.tar.gz`.

**P: ¿Actualiza Wine/Proton automáticamente?**
R: No. Tú gestionas runners. Wine Launcher solo los detecta. Para actualizar Proton-GE: ProtonUp-Qt o re-descargar.

### Juegos

**P: ¿Funciona Elden Ring / Cyberpunk 2077 / [juego AAA]?**
R: Revisa ProtonDB. Con Proton-GE + DXVK + VKD3D + vcrun2019 + win10, la mayoría Platino/Oro funcionan.

**P: ¿Anti-cheat (EAC, BattlEye, Vanguard)?**
R: **No funcionan** en Linux (kernel-level). Solo server-side anti-cheat (VAC, FairFight) o user-mode funcionan.

**P: ¿Mando Xbox/PS5?**
R: Sí, via Steam Input o `steam-devices` / `udev` rules. Proton-GE incluye soporte.

**P: ¿Mods (Nexus, Vortex, MO2)?**
R: Vortex/MO2 corren via Wine. Instala `dotnet48` + `vcrun2019` en la botella.

### Técnico

**P: ¿Dónde están los logs de mi juego?**
R: Terminal donde lanzaste `wine-launcher` o `WINEDEBUG=+all wine-launcher 2>&1 | tee log.txt`

**P: ¿Cómo cambio de Proton-GE a Wine-GE?**
R: Botella → Pestaña General → Runner → Selecciona otro → Guardar → Reinicia app.

**P: ¿Puedo tener varias versiones de Wine?**
R: Sí. Cada botella tiene su runner. Puedes mezclar System Wine, Proton 9, Proton-GE, Wine-GE.

**P: ¿Backup incluye savegames?**
R: Sí, backup = prefix completo (drive_c + registry). Savegames en `drive_c/users/steamuser/` o `drive_c/Program Files/` según juego.

**P: ¿Error "wine: cannot find L"C:\\windows\\system32\\kernel32.dll"?**
R: Prefijo corrupto. Elimina botella y recrea. O `WINEPREFIX=~/.local/.../botella wineboot -u`

**P: ¿Pantalla negra al iniciar juego?**
R: 1) Winetricks → settings → `virtualdesktop` 2) Prueba `renderer=vulkan` / `renderer=opengl` 3) Desactiva overlay (Steam, Discord, MangoHud).

**P: ¿Audio crackling / sin sonido?**
R: `sudo apt install libpulse0:i386 pipewire-pulse` (Ubuntu). Winetricks → settings → `sound=pulse`.

**P: ¿Cómo uso dgVoodoo2 para juegos viejos (DX6-8)?**
R: Winetricks → apps → `dgvoodoo2` (si disponible) o manual: copia DLLs a `drive_c/windows/system32/` + config `dgVoodooControlPanel.exe`.

### Desarrollo

**P: ¿Cómo contribuyo?**
R: Fork → feature branch → PR. Requisitos: Python 3.10+, `python -m py_compile` pasa, MVC pattern.

**P: ¿Dónde está el código del runner detector?**
R: `services/runner_manager.py` - `discover_runners()`, `_probe_wine()`, `_probe_proton()`, etc.

**P: ¿Cómo agrego un winetrick verb nuevo?**
R: `services/winetricks_service.py` - diccionario `VERBS` por categoría.

---

## Tarjeta de Referencia Rápida

```
┌─────────────────────────────────────────────────────────────────┐
│                    WINE LAUNCHER - QUICK REF                    │
├─────────────────────────────────────────────────────────────────┤
│ ATATAJOS                                                        │
│  Ctrl+N    Nueva botella         Ctrl+R    Ejecutar app         │
│  Ctrl+E    Ejecutar .exe         Ctrl+W    Winetricks           │
│  Ctrl+B    Backup botella        Ctrl+,    Configuración        │
│  Delete    Eliminar botella      F5        Refrescar lista      │
├─────────────────────────────────────────────────────────────────┤
│ ESTRUCTURA                                                      │
│  ~/.config/wine-launcher/config.json      # Config global       │
│  ~/.local/share/wine-launcher/bottles/    # Prefijos (1 por app) │
│  ~/.local/share/wine-launcher/backups/    # .tar.gz backups     │
│  ~/.local/share/wine-launcher/runners/    # Runners custom      │
├─────────────────────────────────────────────────────────────────┤
│ WINETRICKS COMUNES (Juegos)                                     │
│  Libraries:  vcrun2019 dxvk vkd3d d3dcompiler_47 corefonts      │
│  Settings:   win10 virtualdesktop sound=pulse renderer=vulkan   │
│  Apps:       steam lutris heroic battle.net epicgames gog       │
├─────────────────────────────────────────────────────────────────┤
│ RUNNERS (Prioridad auto-detect)                                 │
│  1. Proton (Steam)           4. System Wine                     │
│  2. Proton-GE (GloriousEgg)  5. Custom                          │
│  3. Wine-GE (Lutris)                                              │
├─────────────────────────────────────────────────────────────────┤
│ DEBUG                                                            │
│  wine-launcher                    # Logs en terminal            │
│  WINEDEBUG=+all wine-launcher     # Verbose                     │
│  WINEDEBUG=err+all wine-launcher  # Solo errores                │
├─────────────────────────────────────────────────────────────────┤
│ COMANDOS ÚTILES                                                  │
│  wineboot -u                      # Actualizar prefix           │
│  winetricks list-installed        # Ver verbs instalados        │
│  winetricks uninstall vcrun2019   # Quitar verb                 │
│  proton run file.exe              # Proton directo              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Changelog

### v0.1.0 (Inicial)
- MVC architecture completo (Models, Services, Controllers, Views)
- Gestión botellas: crear, eliminar, backup/restore, renombrar
- Runner detection: System Wine, Proton, Proton-GE, Wine-GE, Custom
- Winetricks integration: verbs por categoría, install/uninstall, list-installed
- UI: Split view, 5 pestañas detalle, diálogos modales, menú contextual
- Configuración persistente JSON, paths customizables
- Instalador `install.sh` + GitHub Actions CI/CD (x86_64 + ARM64 + AppImage)
- PyInstaller standalone binary (~50MB)

---

## Licencia Completa

```
MIT License

Copyright (c) 2025 Wine Launcher Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

*Documentación v0.1.0 | Última actualización: 2025 | [GitHub Issues](https://github.com/Vic01107/wine-launcher/issues)*