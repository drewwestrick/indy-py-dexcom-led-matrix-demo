# Galactic Unicorn - Dexcom Glucose Monitor

Displays real-time blood glucose data from Dexcom Share on a Pimoroni Galactic Unicorn (Raspberry Pi Pico 2 W) with a 53x11 LED matrix.

## Hardware Requirements

- **Pimoroni Galactic Unicorn** - RP2350-based board with 53x11 RGB LED matrix
- **Raspberry Pi Pico 2 W** - Built-in WiFi
- **MicroPython v1.25.0** (or later)
- **Dexcom CGM** with Share service enabled
- **WiFi network** (2.4GHz)

## Project Structure

```
indy-py-demo/
├── src/                    # Device files (runs on Pico)
│   ├── main.py            # Main application entry point
│   ├── dexcom.py          # Dexcom Share API client
│   ├── display.py         # Display rendering and graphics
│   ├── font.py            # Custom font and arrow symbols
│   └── secrets.py         # WiFi & Dexcom credentials (not in git)
├── host/                   # Development tools (runs on computer)
│   └── font_editor.py     # Interactive font/symbol editor
├── docs/                   # Documentation
│   ├── README.md          # This file
│   ├── PLAN.md            # Original project requirements
│   └── REFACTORING.md     # Development history
├── deploy.sh              # Automated deployment script
└── .gitignore             # Git exclusions
```

## Features

- ✅ Real-time glucose monitoring via Dexcom Share API
- ✅ Color-coded display (RED: <70, GREEN: 70-180, YELLOW: >180 mg/dL)
- ✅ Custom blocky pixel art font (6x10 digits)
- ✅ Trend arrows with custom 10px-wide symbols (flat, up, down, etc.)
- ✅ Test mode for cycling through all values and arrows
- ✅ Automatic WiFi reconnection
- ✅ Session management with auto re-authentication
- ✅ Updates every 30 seconds (configurable)
- ✅ Clean modular architecture
- ✅ Interactive font/symbol editor with dropdown loading
- ✅ Automated deployment script

## Prerequisites

### 1. Pimoroni Firmware
Install the latest Pimoroni MicroPython firmware for Pico 2 W:
- Download from: [Pimoroni Releases](https://github.com/pimoroni/pimoroni-pico/releases)
- Look for: `pimoroni-picow_galactic_unicorn-*-micropython.uf2`
- Install by holding BOOTSEL button while connecting USB, then drag the .uf2 file

### 2. Dexcom Share Setup
- Download the [Dexcom mobile app](https://www.dexcom.com/apps)
- Enable Dexcom Share service
- Add at least one follower (required to enable Share API)
- Note your Dexcom credentials (email/phone and password)

### 3. Development Tools
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies from requirements.txt
pip install -r requirements.txt
```

**Dependencies installed:**
- `mpremote` - MicroPython remote control for deploying to device
- `mpy-cross` - Cross-compiler for creating .mpy bytecode files
- `pygame` - Graphics library for font editor GUI

## Setup Instructions

### Step 1: Configure Credentials

Create `src/secrets.py` with your WiFi and Dexcom credentials:

```python
# WiFi credentials
WIFI_SSID = "your_wifi_name"
WIFI_PASS = "your_wifi_password"

# Dexcom Share credentials
DEXCOM_USER = "your_dexcom_username"  # Email or +1234567890
DEXCOM_PASS = "your_dexcom_password"
DEXCOM_US = True  # True for US servers, False for international
```

**⚠️ IMPORTANT:** Never commit `secrets.py` to version control!

### Step 2: Deploy to Device

```bash
# Use the deployment script
./deploy.sh

# Or manually:
cd src
mpy-cross dexcom.py display.py font.py secrets.py
mpremote cp *.mpy :
mpremote cp main.py :main.py
```

### Step 3: Run

You should see both `main.py` and `secrets.mpy` on the device.

### Step 6your Galactic Unicorn** via USB, then:

```bash
# Activate venv if not already active
source venv/bin/activate

# Copy the compiled secrets to the Pico
mpremote cp secrets.mpy :secrets.mpy

# Copy main.py to the Pico
mpremote cp main.py :main.py

```bash
# Run once (via mpremote)
mpremote run src/main.py

# Or copy to device to auto-run on boot
mpremote cp src/main.py :main.py
```

## Display Configuration

### Glucose Ranges
- **LOW**: < 70 mg/dL (RED)
- **NORMAL**: 70-180 mg/dL (GREEN)
- **HIGH**: > 180 mg/dL (YELLOW)

### Trend Arrows

Custom 10px-wide pixel art symbols displayed next to glucose value:

- `double_up`: ⇈ Rising very fast (>2 mg/dL/min)
- `single_up`: ↑ Rising fast (1-2 mg/dL/min)
- `forty_five_up`: ↗ Rising (0.5-1 mg/dL/min)
- `flat`: → Stable (±0.5 mg/dL/min)
- `forty_five_down`: ↘ Falling (0.5-1 mg/dL/min)
- `single_down`: ↓ Falling fast (1-2 mg/dL/min)
- `double_down`: ⇊ Falling very fast (<-2 mg/dL/min)

*Note: Arrows are custom block-based pixel art rendered from font.py*

## Custom Fonts & Symbols

Use the font editor to create or modify characters and symbols:

```bash
source venv/bin/activate
python host/font_editor.py
```

### Font Editor Controls
- **Left-click**: Paint pixel
- **Right-click**: Erase pixel
- **Drag**: Paint/erase multiple pixels
- **C**: Clear grid
- **E**: Export to console (3 formats)
- **L**: Toggle dropdown to load existing fonts
- **UP/DOWN**: Navigate dropdown
- **ENTER**: Load selected character/symbol
- **W/S**: Increase/decrease grid width
- **H/J**: Increase/decrease grid height
- **R**: Reset grid to 6x10
- **0-9**: Set current character (digit)
- **A-Z**: Set current character (letter)
- **ESC/Q**: Quit

### Grid Size Limits
- **Width**: 1-25 pixels (for wide arrows like double_up)
- **Height**: 1-10 pixels (display height constraint)

### Workflow
1. Press **L** to open the dropdown
2. Select an existing character/symbol to edit
3. Modify the design using click/drag
4. Press **E** to export the optimized block format
5. Copy the output to `src/font.py`'s `CUSTOM_FONT` dictionary
6. Run `./deploy.sh` to update the device

Export formats are printed to console. The **optimized blocks format** is recommended for efficiency.

## Troubleshooting

### WiFi Connection Failed
- Verify SSID and password in `src/secrets.py`
- Check that your network is 2.4GHz (Pico W doesn't support 5GHz)
- Ensure you're within WiFi range

### Dexcom Authentication Errors
1. **Verify credentials** at [uam1.dexcom.com](https://uam1.dexcom.com) (US) or [uam2.dexcom.com](https://uam2.dexcom.com) (International)
2. **Ensure Share is enabled** in the Dexcom mobile app
3. **Add at least one follower** - the Share API requires this
4. **Check region setting** - Set `DEXCOM_US = False` if outside US
5. **Phone number format** - Use `"+11234567890"` format with `+` and country code

### No Glucose Data
- Check that your Dexcom transmitter is active and connected
- Verify readings appear in the Dexcom mobile app
- Ensure Share is actively transmitting (not paused)

### Display Issues
- Adjust brightness: `gu.set_brightness(0.5)` in src/main.py (0.0-1.0)
- Check font.py has required characters (0-9)

## Monitoring & Debugging

### View Live Output
```bash
# Connect to REPL to see print statements
mpremote repl

# Exit with Ctrl+]
```

## Customization

### Adjust Glucose Thresholds
Edit `src/display.py`:
```python
GLUCOSE_LOW = 70    # Red below this (mg/dL)
GLUCOSE_HIGH = 180  # Yellow above this (mg/dL)
```

### Change Update Intervals
Edit `src/main.py`:
```python
DEXCOM_UPDATE_INTERVAL = 30  # Glucose fetch (seconds)
DISPLAY_UPDATE_INTERVAL = 1   # Display refresh (seconds)
DIGIT_SPACING = 1             # Pixel gap between digits
TEST_MODE = False             # Set True to run test cycle on startup
```

**Note:** Don't set `DEXCOM_UPDATE_INTERVAL` below 30 seconds to avoid API rate limits!

### Modify Display
Edit `src/display.py` to customize:
- Colors (`COLOR_*` constants)
- Positioning (`DISPLAY_X`, `DISPLAY_Y` - currently offset 6px for centering)
- Glucose thresholds (`GLUCOSE_LOW`, `GLUCOSE_HIGH`)
- Layout (modify `draw_glucose()` method)

## Security Notes

- **secrets.py** contains credentials - never commit to version control
- `.gitignore` excludes it automatically
- Compiled to `.mpy` bytecode for basic obfuscation
- Physical device security is your main protection

## API Rate Limits

**Don't set `DEXCOM_UPDATE_INTERVAL` below 30 seconds!** The Dexcom Share API has rate limits. This implementation:
- Fetches every 30 seconds by default (aggressive but safe)
- Auto-retries on failures
- Reuses sessions to minimize auth requests
- Test mode disabled in production (`TEST_MODE = False`)

## Resources

- [Pimoroni Galactic Unicorn](https://shop.pimoroni.com/products/galactic-unicorn)
- [Pimoroni MicroPython](https://github.com/pimoroni/pimoroni-pico)
- [mpremote Documentation](https://docs.micropython.org/en/latest/reference/mpremote.html)
- [MicroPython Documentation](https://docs.micropython.org/)
- [Dexcom Share Info](https://www.dexcom.com/dexcom-international-offices)

## License

MIT License - feel free to modify and share!

## Acknowledgments

- Built for monitoring my son's glucose levels 💙
- Inspired by the Dexcom Share API community projects
- Uses the unofficial Dexcom Share API (no official support)

---

**Questions or Issues?** Check the Troubleshooting section above or review the debug output via `mpremote repl`.
