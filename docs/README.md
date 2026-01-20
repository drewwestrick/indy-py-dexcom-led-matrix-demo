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
│   ├── main.py            # Main application
│   ├── dexcom.py          # Dexcom API client
│   ├── display.py         # Display rendering
│   ├── font.py            # Custom font definitions
│   └── secrets.py         # WiFi & Dexcom credentials
├── host/                   # Development tools (runs on computer)
│   ├── font_editor.py     # 6x10 grid font editor
│   ├── pixel_designer.py  # Font design tool
│   ├── simulator.py       # Display simulator
│   └── test_display.py    # Testing utilities
├── deploy.sh              # Deployment script
└── README.md
```

## Features

- ✅ Real-time glucose monitoring via Dexcom Share API
- ✅ Color-coded display (RED: <70, GREEN: 70-180, YELLOW: >180)
- ✅ Trend arrows (+++ rising fast, = stable, --- falling fast)
- ✅ Custom 6x10 pixel font support
- ✅ Automatic WiFi reconnection
- ✅ Session management with auto re-authentication
- ✅ Updates every 5 minutes
- ✅ Clean modular architecture

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

# Install dependencies
pip install pygame mpremote mpy-cross
```

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
- `+++` Double Up (rising very fast)
- `++` Single Up (rising fast)
- `+` Forty Five Up (rising)
- `=` Flat (stable)
- `-` Forty Five Down (falling)
- `--` Single Down (falling fast)
- `---` Double Down (falling very fast)

## Custom Fonts

Use the font editor to create custom characters:

```bash
source venv/bin/activate
python host/font_editor.py
```

### Font Editor Controls
- **Left-click**: Paint pixel
- **Right-click**: Erase pixel
- **C**: Clear grid
- **E**: Export to console (3 formats)
- **0-9**: Set character digit
- **A-Z**: Set character letter
- **ESC/Q**: Quit

Export formats are printed to console. Copy to `src/font.py` `CUSTOM_FONT` dictionary.

## Development Tools

### Font Editor
6x10 grid editor for creating custom characters:
```bash
python host/font_editor.py
```

### Pixel Designer
Interactive design tool with existing fonts:
```bash
python host/pixel_designer.py
```

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
DEXCOM_UPDATE_INTERVAL = 300  # Glucose fetch (seconds) - don't go below 60!
DISPLAY_UPDATE_INTERVAL = 1    # Display refresh (seconds)
```

### Modify Display
Edit `src/display.py` to customize:
- Colors (`COLOR_*` constants)
- Positioning (`DISPLAY_X`, `DISPLAY_Y`)
- Layout (modify `draw_glucose()` method)

## Security Notes

- **secrets.py** contains credentials - never commit to version control
- `.gitignore` excludes it automatically
- Compiled to `.mpy` bytecode for basic obfuscation
- Physical device security is your main protection

## API Rate Limits

**Don't set `DEXCOM_UPDATE_INTERVAL` below 60 seconds!** The Dexcom Share API has rate limits. This implementation:
- Fetches every 5 minutes (conservative)
- Auto-retries on failures
- Reuses sessions to minimize auth requests

## Resources

- [Pimoroni Galactic Unicorn](https://shop.pimoroni.com/products/galactic-unicorn)
- [Pimoroni MicroPython](https://github.com/pimoroni/pimoroni-pico)
- [mpremote Documentation](https://docs.micropython.org/en/latest/reference/mpremote.html)
- [MicroPython Documentation](https://docs.micropython.org/)
- [Dexcom Share Info](https://www.dexcom.com/dexcom-international-offices)

## License

MIT License - feel free to modify and share!

## Acknowledgments

- Built for monitoring your son's glucose levels 💙
- Inspired by the Dexcom Share API community projects
- Uses the unofficial Dexcom Share API (no official support)

---

**Questions or Issues?** Check the Troubleshooting section above or review the debug output via `mpremote repl`.
