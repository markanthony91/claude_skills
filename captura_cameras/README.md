# Camera Image Downloader - Production System

Automated system for downloading images from 345+ cameras across 115+ BK stores via AIVisual dashboard.

## Quick Start

```bash
# First-time setup (installs dependencies)
./install_final.sh

# Run all cameras (~12-15 minutes for 345 cameras)
./executar_todas_cameras.sh

# Quick execution
./executar_rapido.sh

# Test directory structure
./testar_estrutura.sh
```

## Features

- ✅ Downloads images from 345+ cameras
- ✅ Organizes images by store name
- ✅ Handles P1, P2, P3 camera positions per store
- ✅ Automated login to AIVisual dashboard
- ✅ Progress reporting every 25 cameras
- ✅ Detailed execution report with success/failure stats
- ✅ 2-second delay between downloads to prevent overload

## Technical Details

### Technology Stack
- **Python 3.6+**
- **Selenium WebDriver** - Browser automation
- **ChromeDriver** - Chrome browser control (auto-installed)
- **Requests** - HTTP library
- **BeautifulSoup** - HTML parsing

### System Flow

1. **Login**: Authenticates with https://dashboard.aivisual.ai
2. **Scraping**: Extracts all BK store camera feed URLs
3. **Download**: Downloads images sequentially with 2-second delay
4. **Organization**: Saves to `cameras/Nome_da_Loja/P{1,2,3}_Nome_da_Loja_TIMESTAMP.jpg`
5. **Report**: Generates final report with statistics

## Output Structure

```
cameras/
├── Loja_BK_Central/
│   ├── P1_Loja_BK_Central_20251102_153045.jpg
│   ├── P2_Loja_BK_Central_20251102_153047.jpg
│   └── P3_Loja_BK_Central_20251102_153049.jpg
├── Loja_BK_Shopping/
│   ├── P1_Loja_BK_Shopping_20251102_153052.jpg
│   ├── P2_Loja_BK_Shopping_20251102_153054.jpg
│   └── P3_Loja_BK_Shopping_20251102_153056.jpg
└── ...
```

## Configuration

### Credentials
**⚠️ Security Warning**: Credentials are currently hardcoded in `camera_downloader_complete.py`

**Recommended**: Migrate to environment variables:

1. Install python-dotenv:
```bash
pip3 install python-dotenv
```

2. Create `.env` file:
```
AIVISUAL_USER=bk@aiknow.ai
AIVISUAL_PASS=your_password_here
```

3. Update script to use environment variables

### Camera Delay
Default: 2 seconds between cameras
To modify: Edit `DELAY` variable in `camera_downloader_complete.py`

## Available Scripts

| Script | Description | Execution Time |
|--------|-------------|----------------|
| `install_final.sh` | Install all dependencies | ~2-3 minutes |
| `executar_todas_cameras.sh` | Download from all cameras | ~12-15 minutes |
| `executar_rapido.sh` | Quick execution mode | ~5-8 minutes |
| `testar_estrutura.sh` | Validate directory structure | <1 minute |
| `camera_downloader_complete.py` | Main Python script (direct execution) | ~12-15 minutes |

## Dependencies

Installed automatically via `install_final.sh`:
- selenium >= 4.0.0
- requests >= 2.25.0
- beautifulsoup4
- chromedriver-autoinstaller >= 0.4.0

### Manual Installation
```bash
pip3 install selenium requests beautifulsoup4 chromedriver-autoinstaller
```

## Requirements

- **Python**: 3.6 or higher
- **Chrome/Chromium**: Browser must be installed
- **Network**: Access to https://dashboard.aivisual.ai
- **OS**: Linux, Windows, or WSL

## Troubleshooting

### "ChromeDriver not found"
```bash
python3 -c "import chromedriver_autoinstaller; chromedriver_autoinstaller.install()"
```

### "Module not found"
```bash
pip3 install selenium requests beautifulsoup4
```

### Login fails
- Verify credentials in script are current
- Check if AIVisual dashboard is accessible
- Website structure may have changed (update selectors)

### Downloads are slow
- Normal: ~2 seconds per camera (intentional delay)
- Total time: 345 cameras × 2 seconds ≈ 11-12 minutes
- Plus overhead: scraping, login, report generation

### Missing images
- Check console output for errors
- Verify camera is online in AIVisual dashboard
- Some cameras may be offline or unavailable

## Performance

- **Cameras**: 345+ across 115+ stores
- **Download Rate**: ~30 cameras/minute (with 2s delay)
- **Total Execution**: ~12-15 minutes for full run
- **Success Rate**: Typically >95% (some cameras may be offline)

## Logging

Console output includes:
- Login status
- Progress updates every 25 cameras
- Individual download status
- Final statistics (success/failure counts)
- Execution time

## Best Practices

1. **Test First**: Run `testar_estrutura.sh` before full execution
2. **Schedule**: Run during off-peak hours to minimize impact
3. **Monitor**: Check logs for download failures
4. **Storage**: Ensure sufficient disk space (~1-2GB per full run)
5. **Credentials**: Migrate to environment variables for security

## Directory Structure

```
captura_cameras/
├── camera_downloader_complete.py  # Main script
├── executar_todas_cameras.sh      # Full execution
├── executar_rapido.sh            # Quick mode
├── install_final.sh              # Setup script
├── testar_estrutura.sh           # Structure test
├── test_estrutura.py             # Test utilities
├── cameras/                      # Output directory (created automatically)
└── README.md                     # This file
```

## Support

For issues or questions:
1. Check this README
2. Review main documentation: `/home/marcelo/sistemas/CLAUDE.md`
3. Examine console output for specific errors

## Related Projects

This is part of a multi-project repository. See `/home/marcelo/sistemas/CLAUDE.md` for:
- `captura_cameras_debug` - Debug version with label filtering
- `qrcode-lens-insight` - QR code scanner application
- `sistema_recupera` - Alphaville employee lookup automation

---

**Last Updated**: 2025-11-02
