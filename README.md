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
- ✅ Color-coded display (RED: <70, BLUE: 70-180, YELLOW: >180 mg/dL)
- ✅ Custom blocky pixel art font (6x10 digits)
- ✅ Trend arrows with custom 10px-wide symbols (flat, up, down, etc.)
- ✅ Hardware brightness control using LUX +/- buttons (9 levels: 20%-100%)
- ✅ Async/event-driven architecture for responsive buttons and efficient updates
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
mpy-cross secrets.py
mpremote cp secrets.mpy :secrets.mpy
mpremote cp dexcom.py :dexcom.py
mpremote cp display.py :display.py
mpremote cp font.py :font.py
mpremote cp main.py :main.py
cd ..
```

### Step 3: Run

```bash
# Run once (via mpremote)
mpremote run src/main.py

# Or for auto-run on boot, copy main.py as boot.py
mpremote cp src/main.py :boot.py
```

## Architecture

### Async Event-Driven Design

The system uses MicroPython's `uasyncio` for concurrent task management:

**Three Independent Tasks:**
1. **button_checker** - Polls LUX buttons every 50ms for instant brightness response
2. **glucose_fetcher** - Fetches glucose data every 30 seconds
3. **display_updater** - Redraws display only when:
   - Glucose value changes
   - Brightness changes
   - Timer bar animation update (every 1 second)

**Benefits:**
- Responsive buttons (no blocking)
- Efficient CPU usage (event-driven updates)
- Lower power consumption
- True concurrent operations

## Display Configuration

### Glucose Ranges
- **LOW**: < 70 mg/dL (RED)
- **NORMAL**: 70-180 mg/dL (BLUE)
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

### Brightness Control

Adjust display brightness using the Galactic Unicorn's built-in LUX buttons:

- **LUX + button**: Increase brightness (10% per press)
- **LUX - button**: Decrease brightness (10% per press)
- **Range**: 20% to 100% (9 levels: 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
- **Default**: 50%

Brightness changes are applied immediately to both the LED matrix hardware and the rendered display colors. The current brightness level is printed to the console when adjusted. Each button press changes brightness by one level (0.1 increment).

#### Technical Details

The brightness control works at two levels:
1. **Hardware level**: `gu.set_brightness(value)` - Controls LED driver PWM
2. **Software level**: `display.set_brightness(value)` - Scales color values before rendering

This dual approach ensures consistent brightness across all display elements (glucose digits, arrows, timer bar) with proper color balance at all brightness levels.

**Button IDs:**
- `SWITCH_BRIGHTNESS_UP = 21` (LUX + button)
- `SWITCH_BRIGHTNESS_DOWN = 26` (LUX - button)

Edge detection is used to register single button presses - the brightness only changes on the initial press, not while holding the button. Brightness persists until device reset (returns to default on reboot).

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
DIGIT_SPACING = 1             # Pixel gap between digits
TEST_MODE = True              # Set False to skip test cycle on startup
```

**Note:** Don't set `DEXCOM_UPDATE_INTERVAL` below 30 seconds to avoid API rate limits!

### Adjust Brightness Settings
Edit `src/main.py`:
```python
BRIGHTNESS_MIN = 0.2           # Minimum brightness (20%)
BRIGHTNESS_MAX = 1.0           # Maximum brightness (100%)
BRIGHTNESS_STEP = 0.1          # Brightness adjustment step (10%)
BRIGHTNESS_DEFAULT = 0.5       # Default brightness on startup (50%)
```

### Modify Display
Edit `src/display.py` to customize:
- Colors:
  - `COLOR_RED = (255, 0, 0)` - Low glucose (<70)
  - `COLOR_BLUE = (92, 115, 255)` - Normal glucose (70-180)
  - `COLOR_YELLOW = (255, 89, 18)` - High glucose (>180)
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
