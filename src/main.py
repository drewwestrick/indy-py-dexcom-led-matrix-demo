"""
Galactic Unicorn - Dexcom Glucose Monitor
Main application entry point
"""

import time
import network
import ntptime
import uasyncio as asyncio
from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN

# Import modules
try:
    import secrets
except ImportError:
    print("ERROR: secrets.mpy not found!")
    raise

from dexcom import DexcomClient
from display import Display

# Configuration
DEXCOM_UPDATE_INTERVAL = 30    # Seconds between glucose fetches (min: 30)
DISPLAY_UPDATE_INTERVAL = 1     # Deprecated: No longer used in async version (kept for reference)
DIGIT_SPACING = 1               # Pixel gap between digits for readability
TEST_MODE = True                # Run diagnostic test on startup (set False for production)

# Brightness configuration
BRIGHTNESS_MIN = 0.2           # Minimum brightness (20%)
BRIGHTNESS_MAX = 1.0           # Maximum brightness (100%)
BRIGHTNESS_STEP = 0.1          # Brightness adjustment step (10%)
BRIGHTNESS_DEFAULT = 0.5       # Default brightness (50%)

# Galactic Unicorn button constants (from galactic.py)
# LUX buttons on Galactic Unicorn for brightness control
SWITCH_BRIGHTNESS_UP = 21     # LUX + button (brightness up)
SWITCH_BRIGHTNESS_DOWN = 26   # LUX - button (brightness down)

def connect_wifi():
    """Connect to WiFi"""
    print(f"Connecting to WiFi: '{secrets.WIFI_SSID}'...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASS)
    
    # Wait for connection (max 30 seconds)
    max_wait = 30
    while max_wait > 0:
        status = wlan.status()
        if status < 0 or status >= 3:
            break
        max_wait -= 1
        time.sleep(1)
    
    if wlan.status() != 3:
        raise RuntimeError(f"WiFi connection failed (status: {wlan.status()})")
    
    print(f"Connected! IP: {wlan.ifconfig()[0]}")
    return wlan


def sync_time():
    """Sync system time using NTP"""
    print("Syncing time with NTP...")
    try:
        ntptime.settime()
        print("Time synced successfully")
    except Exception as e:
        print(f"NTP sync failed: {e}")


def run_digit_test(display):
    """
    Run test mode cycling through glucose values 50-400 with all arrow types
    
    Displays all 7 arrow symbols (double_down through double_up) across the
    glucose range to verify font rendering and arrow positioning.
    Duration: 10 seconds total, ~0.028s per value
    
    Args:
        display: Display instance to render test values
    """
    print("\n" + "=" * 50)
    print("RUNNING DIGIT TEST MODE")
    print("Testing glucose values 50-400 over 10 seconds")
    print("=" * 50)
    
    start_value = 50
    end_value = 400
    duration = 10  # seconds
    
    # Calculate number of steps (one per value)
    num_values = end_value - start_value + 1  # 351 values
    delay = duration / num_values  # ~0.071 seconds per value
    
    # Arrow trend cycle: 50 values per arrow type
    arrow_trends = [
        "DoubleDown",      # 50-99
        "SingleDown",      # 100-149
        "FortyFiveDown",   # 150-199
        "Flat",            # 200-249
        "FortyFiveUp",     # 250-299
        "SingleUp",        # 300-349
        "DoubleUp"         # 350-400
    ]
    
    for value in range(start_value, end_value + 1):
        # Calculate which arrow to show based on value
        trend_index = min((value - start_value) // 50, len(arrow_trends) - 1)
        trend = arrow_trends[trend_index]
        
        # Display current test value with appropriate trend
        display.draw_glucose(value, trend)
        print(f"Test: {value} mg/dL ({trend})", end='\r')
        time.sleep(delay)
    
    print("\n" + "=" * 50)
    print("DIGIT TEST COMPLETE")
    print("=" * 50 + "\n")


def main():
    """
    Main application entry point
    
    Initializes hardware, runs optional test mode, connects to WiFi,
    authenticates with Dexcom Share API, and starts async event loop.
    """
    print("=" * 50)
    print("Galactic Unicorn - Dexcom Glucose Monitor")
    print("=" * 50)
    
    # Initialize hardware
    gu = GalacticUnicorn()
    graphics = PicoGraphics(DISPLAY_GALACTIC_UNICORN)
    
    # Initialize brightness
    current_brightness = BRIGHTNESS_DEFAULT
    gu.set_brightness(current_brightness)
    
    # Initialize display
    display = Display(gu, graphics, digit_spacing=DIGIT_SPACING)
    display.set_brightness(current_brightness)
    
    # Initialize WiFi and Dexcom client
    dexcom = DexcomClient(
        secrets.DEXCOM_USER,
        secrets.DEXCOM_PASS,
        secrets.DEXCOM_US
    )
    
    # Run digit test if enabled, while connecting to WiFi in parallel
    if TEST_MODE:
        print("Starting WiFi connection in parallel with self-test...")
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASS)
        wifi_start_time = time.time()
        
        # Run test while WiFi connects in background
        run_digit_test(display)
        
        # Check WiFi status after test
        max_wait_remaining = 30 - (time.time() - wifi_start_time)
        wait_count = 0
        while max_wait_remaining > 0 and wait_count < max_wait_remaining:
            status = wlan.status()
            if status < 0 or status >= 3:
                break
            print(f"Waiting for WiFi... (status: {status})")
            time.sleep(1)
            wait_count += 1
        
        if wlan.status() == 3:
            print(f"Connected! IP: {wlan.ifconfig()[0]}")
        else:
            print(f"WiFi connection failed after test (status: {wlan.status()})")
            raise RuntimeError("WiFi connection failed")
    else:
        # Normal flow: connect WiFi first
        connect_wifi()
    
    # Sync time
    sync_time()
    
    # Authenticate and fetch initial Dexcom data
    print("Authenticating with Dexcom...")
    if dexcom.authenticate() and dexcom.login():
        dexcom.fetch_glucose()  # Initial fetch (optional)
    else:
        print("Warning: Dexcom authentication failed, will retry in main loop")
    
    # Start async event loop
    print("Starting async event loop...")
    try:
        asyncio.run(async_main(gu, display, dexcom, current_brightness))
    except KeyboardInterrupt:
        print("Interrupted by user")


async def async_main(gu, display, dexcom, initial_brightness):
    """
    Async main loop - coordinates all tasks
    
    Args:
        gu: GalacticUnicorn instance
        display: Display instance
        dexcom: DexcomClient instance
        initial_brightness: Initial brightness value
    """
    # Shared state - initialize with current or None values
    state = {
        'brightness': initial_brightness,
        'needs_update': True,  # Flag to trigger display updates
        'glucose_value': dexcom.get_glucose_value() or None,
        'glucose_trend': dexcom.get_glucose_trend() or None,
    }
    
    # Create tasks
    tasks = [
        asyncio.create_task(button_checker(gu, display, state)),
        asyncio.create_task(glucose_fetcher(dexcom, state)),
        asyncio.create_task(display_updater(display, state)),
    ]
    
    # Run all tasks concurrently with error handling
    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        print(f"Critical error in async task: {e}")
        # Tasks will be cancelled when function exits
        raise


async def button_checker(gu, display, state):
    """
    Async task to check buttons frequently
    
    Args:
        gu: GalacticUnicorn instance
        display: Display instance
        state: Shared state dictionary
    """
    lux_up_was_pressed = False
    lux_down_was_pressed = False
    
    while True:
        # Check for brightness button presses (edge detection)
        lux_up_pressed = gu.is_pressed(SWITCH_BRIGHTNESS_UP)
        lux_down_pressed = gu.is_pressed(SWITCH_BRIGHTNESS_DOWN)
        
        # LUX Up - increase brightness on press (not hold)
        if lux_up_pressed and not lux_up_was_pressed:
            state['brightness'] = min(state['brightness'] + BRIGHTNESS_STEP, BRIGHTNESS_MAX)
            gu.set_brightness(state['brightness'])
            display.set_brightness(state['brightness'])
            state['needs_update'] = True
            print(f"Brightness: {state['brightness']:.1f}")
        lux_up_was_pressed = lux_up_pressed
        
        # LUX Down - decrease brightness on press (not hold)
        if lux_down_pressed and not lux_down_was_pressed:
            state['brightness'] = max(state['brightness'] - BRIGHTNESS_STEP, BRIGHTNESS_MIN)
            gu.set_brightness(state['brightness'])
            display.set_brightness(state['brightness'])
            state['needs_update'] = True
            print(f"Brightness: {state['brightness']:.1f}")
        lux_down_was_pressed = lux_down_pressed
        
        # Check buttons every 50ms for responsiveness
        await asyncio.sleep(0.05)


async def glucose_fetcher(dexcom, state):
    """
    Async task to fetch glucose data periodically
    
    Args:
        dexcom: DexcomClient instance
        state: Shared state dictionary
    """
    while True:
        try:
            if dexcom.fetch_glucose():
                new_value = dexcom.get_glucose_value()
                new_trend = dexcom.get_glucose_trend()
                
                # Only trigger update if values actually changed
                if new_value != state['glucose_value'] or new_trend != state['glucose_trend']:
                    state['glucose_value'] = new_value
                    state['glucose_trend'] = new_trend
                    state['needs_update'] = True
        except Exception as e:
            print(f"Error fetching glucose: {e}")
        
        # Fetch every 30 seconds
        await asyncio.sleep(DEXCOM_UPDATE_INTERVAL)


async def display_updater(display, state):
    """
    Async task to update display only when needed
    
    Updates when:
    - needs_update flag is set (glucose/brightness change)
    - Timer bar needs animation update (every 1 second)
    
    Args:
        display: Display instance
        state: Shared state dictionary
    """
    last_timer_update = time.time()
    
    while True:
        current_time = time.time()
        
        # Update timer bar every 1 second for animation
        timer_needs_update = (current_time - last_timer_update) >= 1
        
        # Redraw if something changed or timer needs update
        if state['needs_update'] or timer_needs_update:
            display.draw_glucose(
                state['glucose_value'],
                state['glucose_trend']
            )
            state['needs_update'] = False
            
            if timer_needs_update:
                last_timer_update = current_time
        
        # Check every 100ms for updates
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    main()
