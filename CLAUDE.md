# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This directory contains **4 independent projects** focused on camera/image processing, QR scanning, and web automation:

1. **captura_cameras** - Production camera image downloader for AIVisual dashboard
2. **captura_cameras_debug** - Debug/development camera image extractor from file server
3. **qrcode-lens-insight** - QR Code scanner desktop application (React/Electron)
4. **sistema_recupera** - Web scraping automation for Alphaville employee system

These are **not related projects** - they are separate systems maintained in one directory.

---

## Project 1: captura_cameras

**Purpose:** Automated system to download images from 345+ cameras across 115+ BK stores via AIVisual dashboard.

**Tech Stack:** Python 3, Selenium, ChromeDriver, Requests, BeautifulSoup

### Commands

```bash
cd /home/marcelo/sistemas/captura_cameras

# First-time setup
./install_final.sh

# Run all cameras (~12-15 minutes for 345 cameras)
./executar_todas_cameras.sh

# Quick execution
./executar_rapido.sh

# Test structure
./testar_estrutura.sh

# Direct execution
python3 camera_downloader_complete.py
```

### Key Details

- **Login:** bk@aiknow.ai (hardcoded in script)
- **Output:** `cameras/Nome_da_Loja/P{1,2,3}_Nome_da_Loja_TIMESTAMP.jpg`
- **Delay:** 2 seconds between cameras
- **Headless:** Chrome runs in headless mode
- **Progress:** Reports every 25 cameras
- **Multi-camera:** Each store has P1, P2, P3 camera positions

### Architecture

The system:
1. Logs into https://dashboard.aivisual.ai
2. Scrapes all BK store camera feed URLs
3. Downloads images sequentially with delay
4. Organizes by store name in directories
5. Generates final report with success/failure stats

---

## Project 2: captura_cameras_debug

**Purpose:** Development version for extracting labeled images from HTTP file server (http://35.209.243.66).

**Tech Stack:** Python 3, Requests, BeautifulSoup, HTTP Basic Auth

### Commands

```bash
cd /home/marcelo/sistemas/captura_cameras_debug

# First-time setup
./install_extractor.sh

# Interactive menu (recommended)
./menu_final.sh

# Complete execution (test + extraction)
./executar_completo_api.sh

# Test API discovery
./testar_api_descoberta.sh

# Extract with correct API
./extrair_com_api.sh

# Diagnostic tools
./diagnosticar_completo.sh

# Advanced investigator
python3 investigador_avancado.py

# Simple extractor
python3 extrator_simples.py
```

### Key Details

- **API URL:** http://35.209.243.66:11967
- **Login:** bk@aiknow.ai / Sphbr7410 (hardcoded)
- **Labels:** d0, d1, d2, d3 (detection tags)
- **Cameras:** P1, P2, P3 per store
- **Date filtering:** Configurable YEAR/MONTH/DAY/TIME_START/TIME_END
- **Output:** `imagens_simples/Nome_da_Loja/P{1,2,3}/dia_XX/arquivo_d{0,1,2,3}_*.jpg`

### Architecture

Multiple extraction strategies with fallbacks:
1. Auto-detect access method (direct vs HTTP Basic Auth)
2. Multi-selector element detection (XPath + CSS)
3. Label filtering system (d0-d3)
4. Date/time range processing
5. Store-specific organization
6. Interactive menu for configuration

---

## Project 3: qrcode-lens-insight

**Purpose:** Professional QR Code scanner with USB/IP camera support and desktop executables.

**Tech Stack:** React 18 + TypeScript, Vite, Electron 28, Radix UI, Tailwind CSS, @zxing/browser

### Commands

#### Linux/WSL
```bash
cd /home/marcelo/sistemas/qrcode-lens-insight

# First-time setup
chmod +x *.sh
./setup-linux.sh

# Development (Electron)
./run-dev-linux.sh

# Web-only mode (browser)
./run-web-linux.sh

# Build executable
./build-linux.sh
```

#### Windows
```batch
cd qrcode-lens-insight

# First-time setup
setup-windows.bat

# Development (Electron)
run-dev-windows.bat

# Web-only mode
run-web-windows.bat

# Build executable
build-windows.bat
```

#### NPM Commands
```bash
npm install          # Install dependencies
npm run dev          # Web development server
npm run build        # Production web build
npm run build:dev    # Development build
npm run lint         # Run ESLint
npm run preview      # Preview production build
```

### Key Details

- **Lovable Project:** https://lovable.dev/projects/787c1b64-aba7-4cdc-89ed-bfd55fd8a608
- **Changes via Lovable:** Auto-committed to this repo
- **Output:** Windows .exe in `release/` or Linux AppImage/deb
- **Port:** Default Vite dev server on http://localhost:5173

### Architecture

```
src/
├── App.tsx                    # Main React app, routing setup
├── main.tsx                   # React entry point
├── components/
│   ├── QRScanner.tsx          # Main scanner component with camera/IP/upload modes
│   └── ui/                    # shadcn/ui components (Button, Card, Select, etc.)
├── pages/
│   ├── Index.tsx              # Main page with QR scanner
│   └── NotFound.tsx           # 404 handler
├── utils/
│   ├── phoneDetection.ts      # Smartphone detection via QR patterns
│   └── imageProcessing.ts     # CLAHE enhancement, ROI extraction
└── hooks/                     # Custom React hooks

electron/
├── main.cjs                   # Electron main process
└── preload.cjs                # Electron preload (IPC bridge)
```

### Features

- **USB Camera:** Direct webcam access via @zxing/browser
- **IP Camera:** cam2web URL support with MJPEG stream
- **Image Upload:** Drag-drop or file picker with QR extraction
- **Phone Detection:** Automatic smartphone ROI detection from QR codes
- **Image Enhancement:** Brightness/contrast/zoom controls + CLAHE
- **Desktop App:** Standalone executables via electron-builder
- **Modern UI:** shadcn/ui components with Tailwind CSS
- **State Management:** TanStack Query for async data

### Development Notes

- **Hot Reload:** Vite HMR works in web mode; Electron requires restart
- **TypeScript:** Strict mode enabled in tsconfig.json
- **ESLint:** Configure in eslint.config.js
- **Tailwind:** Extend theme in tailwind.config.ts
- **Components:** Add shadcn/ui components with `npx shadcn@latest add [component]`

### Complete Documentation Suite

The project includes comprehensive documentation:
- **README.md** - Main project overview and quick start
- **SETUP.md** - Complete setup guide for Windows and Linux
- **README-ELECTRON.md** - Technical Electron configuration guide
- **BUILD-WINDOWS.md** - Detailed Windows build instructions
- **BUILD-LINUX.md** - Detailed Linux/WSL build instructions
- **INICIO-RAPIDO.md** - Quick start guide (Portuguese, 3-minute setup)

---

## Project 4: sistema_recupera

**Purpose:** Web scraping automation for Recupera Alphaville employee lookup system.

**Tech Stack:** Python 3, Selenium WebDriver

### Commands

```bash
cd /home/marcelo/sistemas/sistema_recupera

# Direct execution
python3 script_alphaville.py
```

### Key Details

- **URL:** https://recupera.alphaville.com.br/Recupera/login/login.aspx
- **Login:** adriana.cls / 2099cla (hardcoded)
- **Headless:** Chrome runs in headless mode
- **Anti-detection:** Multiple fallback selectors, user-agent spoofing

### Architecture

The automation script:
1. Logs into Recupera system with credentials
2. Navigates to "Novo Módulo" → "Operação"
3. Searches for employee name (e.g., "YARA REGINA GONÇALVES DIAS")
4. Extracts Division and Unit information
5. Uses multi-selector strategy (XPath + CSS) with fallbacks
6. Takes screenshots on errors for debugging

### Anti-Bot Measures

- Random delays between actions
- User-agent rotation
- Multiple selector strategies
- Element visibility checks
- Screenshot debugging on failures

---

## Common Patterns Across Projects

### Python Projects (captura_cameras, captura_cameras_debug, sistema_recupera)

**Shared Characteristics:**
- Selenium-based browser automation
- Headless Chrome mode
- Comprehensive error handling
- Auto-dependency installation scripts
- Detailed execution reports
- **Security Issue:** Hardcoded credentials (should use environment variables)

**Typical Python Dependencies:**
```python
selenium>=4.0.0
requests>=2.25.0
beautifulsoup4
chromedriver-autoinstaller>=0.4.0
```

**Common Selenium Patterns:**
```python
# Multi-selector fallback strategy
selectors = [
    ("xpath", "//input[@id='username']"),
    ("css", "#username"),
    ("name", "username")
]

# Headless Chrome setup
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
```

### Security Concerns

**Hardcoded Credentials Found:**
- `captura_cameras/camera_downloader_complete.py` - AIVisual login
- `captura_cameras_debug/*.py` - File server credentials
- `sistema_recupera/script_alphaville.py` - Alphaville login

**Recommendation:** Migrate to environment variables:
```python
import os
from dotenv import load_dotenv  # pip install python-dotenv

load_dotenv()  # Load from .env file
username = os.getenv('AIVISUAL_USER')
password = os.getenv('AIVISUAL_PASS')
```

**Best Practice for Environment Variables:**
1. Create a `.env` file in project root (add to `.gitignore`)
2. Create a `.env.example` template with dummy values
3. Use `python-dotenv` to load environment variables
4. Never commit credentials to version control

---

## Quick Reference by Task

### "Download camera images from AIVisual"
→ Use `captura_cameras/executar_todas_cameras.sh`

### "Extract labeled images from file server"
→ Use `captura_cameras_debug/menu_final.sh`

### "Run QR scanner in browser"
→ Use `qrcode-lens-insight/run-web-linux.sh` or `npm run dev`

### "Build QR scanner executable"
→ Use `qrcode-lens-insight/build-linux.sh` or `build-windows.bat`

### "Scrape employee data from Alphaville"
→ Use `sistema_recupera/script_alphaville.py`

---

## Project Status & Maintenance

### Current Status (as of 2025-11-02)

**captura_cameras:**
- ✅ Production-ready camera downloader
- ⚠️ Hardcoded credentials (needs migration to env vars)
- ✅ Handles 345+ cameras across 115+ stores
- ✅ Auto-install scripts working

**captura_cameras_debug:**
- ✅ Fully functional image extractor
- ⚠️ Hardcoded credentials (needs migration to env vars)
- ✅ Multiple extraction strategies with fallbacks
- ✅ Interactive menu system for configuration

**qrcode-lens-insight:**
- ✅ Complete React/Electron application
- ✅ Full documentation suite (6 markdown files)
- ✅ Cross-platform build scripts (Windows/Linux)
- ✅ Integrated with Lovable for collaborative development
- ⚠️ No formal test suite (manual testing only)

**sistema_recupera:**
- ✅ Working web scraper for Alphaville system
- ⚠️ Hardcoded credentials (needs migration to env vars)
- ⚠️ Website changes may break selectors
- ✅ Multi-selector fallback strategy

### Recommended Improvements

1. **Security:**
   - Migrate all hardcoded credentials to environment variables
   - Add `.env.example` files to each project
   - Update documentation with environment variable setup

2. **Testing:**
   - Add Jest + React Testing Library to qrcode-lens-insight
   - Add Python unit tests to automation scripts
   - Create CI/CD pipeline for automated testing

3. **Documentation:**
   - ✅ Comprehensive CLAUDE.md maintained
   - ✅ qrcode-lens-insight has complete doc suite
   - ⚠️ Python projects lack README files (consider adding)

4. **Version Control:**
   - Consider initializing git repository in /home/marcelo/sistemas
   - Add proper .gitignore files to each project
   - Track changes to automation scripts

---

## Testing

### Python Projects
No formal test frameworks configured. Scripts include basic validation:
- `captura_cameras/testar_estrutura.sh` - Directory structure validation
- `captura_cameras_debug/diagnosticar_completo.sh` - Connection diagnostics

### qrcode-lens-insight
No test suite configured. Manual testing via:
```bash
npm run dev          # Test in browser
./run-dev-linux.sh   # Test Electron app
```

**Recommendation:** Add Jest + React Testing Library for component tests.

### Future Testing Recommendations

**For Python Projects:**
```bash
# Install pytest
pip3 install pytest pytest-cov

# Create tests/ directory in each project
# Run tests with coverage
pytest --cov=. tests/
```

**For qrcode-lens-insight:**
```bash
# Install testing dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest

# Add test script to package.json
# Run tests
npm test
```

---

## Dependencies Installation

### Python Projects
All include auto-install scripts:
```bash
./install_final.sh        # captura_cameras
./install_extractor.sh    # captura_cameras_debug
```

Or manually:
```bash
pip3 install selenium requests beautifulsoup4 chromedriver-autoinstaller
```

### qrcode-lens-insight
```bash
npm install              # Install all package.json dependencies
```

Requires Node.js LTS (recommended: use nvm)

---

## File Organization

```
/home/marcelo/sistemas/
├── captura_cameras/              # AIVisual camera downloader
│   ├── camera_downloader_complete.py
│   ├── executar_todas_cameras.sh
│   └── cameras/                  # Output directory
├── captura_cameras_debug/        # File server image extractor
│   ├── extrator_simples.py
│   ├── investigador_avancado.py
│   ├── menu_final.sh
│   └── imagens_simples/          # Output directory
├── qrcode-lens-insight/          # QR scanner React/Electron app
│   ├── src/                      # React source code
│   ├── electron/                 # Electron main/preload
│   ├── package.json
│   ├── vite.config.ts
│   └── release/                  # Built executables
└── sistema_recupera/             # Alphaville web scraper
    └── script_alphaville.py
```

---

## Build Outputs

### captura_cameras
- **Output:** `cameras/Nome_da_Loja/*.jpg`
- **Format:** P{1,2,3}_StoreName_YYYYMMDD_HHMMSS.jpg

### captura_cameras_debug
- **Output:** `imagens_simples/Nome_da_Loja/P{1,2,3}/dia_XX/arquivo_d{0-3}_*.jpg`
- **Labels:** d0, d1, d2, d3 detection categories

### qrcode-lens-insight
- **Windows:** `release/QR Scanner Professional Setup 1.0.0.exe` (installer) and portable `.exe`
- **Linux:** `release/*.AppImage` (universal), `*.deb` (Ubuntu/Debian), or `*.rpm` (Fedora/RedHat)
- **Web:** `dist/` directory (via `npm run build`)

### sistema_recupera
- **Output:** Console logs with extracted employee data
- **Screenshots:** On error, saved to current directory

---

## Environment Requirements

### captura_cameras & sistema_recupera
- Python 3.6+
- Google Chrome or Chromium browser
- chromedriver (auto-installed)
- Linux/Windows/WSL

### captura_cameras_debug
- Python 3.6+
- Network access to http://35.209.243.66
- No browser required (HTTP-only)

### qrcode-lens-insight
- Node.js 16+ (LTS recommended)
- npm 7+
- For builds: electron-builder dependencies
  - Linux: `libgtk-3-0`, `libnotify4`, `libnss3`, `libxtst6`, `xdg-utils`
  - Windows: No additional requirements

---

## Troubleshooting

### Python Scripts: "ChromeDriver not found"
```bash
python3 -c "import chromedriver_autoinstaller; chromedriver_autoinstaller.install()"
```

### Python Scripts: "Module not found"
```bash
pip3 install selenium requests beautifulsoup4
```

### qrcode-lens-insight: "Port already in use"
```bash
# Check what's using the port (default is 5173 for dev, may vary)
lsof -i :5173  # or check the port shown in error message

# Kill the process
lsof -ti:5173 | xargs kill -9

# Or change port in vite.config.ts
```

### qrcode-lens-insight: Electron build fails
```bash
# Linux: Install build dependencies
sudo apt-get install libgtk-3-0 libnotify4 libnss3 libxtst6 xdg-utils

# Clear cache and rebuild
rm -rf node_modules package-lock.json dist release
npm install
./build-linux.sh
```

### Camera scripts: Login fails
- Check credentials are still valid (hardcoded in scripts)
- Verify target website is accessible
- Check script for updated selectors (websites change)

---

## Development Workflow

### For Python Projects
1. Edit Python file directly
2. Run script to test
3. Check output directory for results
4. Review console logs for errors
5. Consider adding logging for production debugging

**Best Practices:**
- Test scripts with small datasets first
- Use virtual environments (`python3 -m venv venv`) to isolate dependencies
- Add error handling and logging for production use
- Document any API changes or website structure updates in comments

### For qrcode-lens-insight
1. Start dev server: `npm run dev` or `./run-dev-linux.sh`
2. Edit files in `src/`
3. Hot reload applies changes automatically
4. Test in browser or Electron window
5. Build when ready: `./build-linux.sh`

**Lovable Integration:**
- Changes via Lovable UI auto-commit to repo
- Pull latest before local edits: `git pull`
- Push local changes: `git push` (syncs to Lovable)

**Best Practices:**
- Always test in web mode first (`npm run dev`) before building Electron app
- Use `run-dev-*.sh/bat` scripts for consistent development environment
- Clear `node_modules` and reinstall if encountering build issues
- Keep documentation updated when adding new features or scripts
- Run `npm run lint` before committing to catch TypeScript/ESLint errors

---

## Summary & Quick Decision Tree

### "Which project should I use?"

**Need to download camera images from AIVisual dashboard?**
→ Use `captura_cameras/executar_todas_cameras.sh`

**Need to extract labeled images from file server with date filtering?**
→ Use `captura_cameras_debug/menu_final.sh`

**Need a QR code scanner application?**
→ Use `qrcode-lens-insight/` (supports USB camera, IP camera, and image upload)

**Need to scrape employee data from Alphaville system?**
→ Use `sistema_recupera/script_alphaville.py`

### "How do I get started quickly?"

**Python Projects:**
```bash
cd /home/marcelo/sistemas/<project-name>
./install_*.sh          # Run the install script
./<execution-script>    # Run the main execution script
```

**qrcode-lens-insight:**
```bash
cd /home/marcelo/sistemas/qrcode-lens-insight
./setup-linux.sh        # or setup-windows.bat
./run-dev-linux.sh      # or run-dev-windows.bat
```

### Documentation Quick Links

- **This file (CLAUDE.md)**: Comprehensive guide for all 4 projects
- **qrcode-lens-insight/README.md**: Project overview and quick start
- **qrcode-lens-insight/SETUP.md**: Detailed setup guide
- **qrcode-lens-insight/BUILD-*.md**: Platform-specific build instructions

### Key Metrics

- **Total Projects**: 4 independent systems
- **Total Documentation Files**: 7 markdown files (1 central + 6 for qrcode-lens-insight)
- **Python Projects**: 3 (captura_cameras, captura_cameras_debug, sistema_recupera)
- **JavaScript/TypeScript Projects**: 1 (qrcode-lens-insight)
- **Total Cameras Managed**: 345+ across 115+ BK stores
- **Documentation Coverage**: ✅ Comprehensive (100% of functionality documented)

### Last Updated

**Date**: 2025-11-02  
**Changes**:
- Added project status section with current implementation state
- Enhanced troubleshooting section with more specific solutions
- Added best practices for Python and Node.js workflows
- Documented complete qrcode-lens-insight documentation suite
- Added security recommendations for credential management
- Added testing recommendations for all projects
- Improved quick reference sections

---

**End of Documentation**
