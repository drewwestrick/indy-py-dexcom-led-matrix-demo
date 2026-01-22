"""
Galactic Unicorn - Dexcom Glucose Monitor
Main application entry point
"""

import time
import network
import ntptime
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
DISPLAY_UPDATE_INTERVAL = 1     # Seconds between display updates
DIGIT_SPACING = 1               # Pixel gap between digits for readability
TEST_MODE = True                # Run diagnostic test on startup (set False for production)

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
    authenticates with Dexcom Share API, and enters main loop to
    periodically fetch and display glucose data.
    """
    print("=" * 50)
    print("Galactic Unicorn - Dexcom Glucose Monitor")
    print("=" * 50)
    
    # Initialize hardware
    gu = GalacticUnicorn()
    graphics = PicoGraphics(DISPLAY_GALACTIC_UNICORN)
    gu.set_brightness(0.5)
    
    # Initialize display
    display = Display(gu, graphics, digit_spacing=DIGIT_SPACING)
    
    # Initialize WiFi and Dexcom client
    wlan = None
    dexcom = DexcomClient(
        secrets.DEXCOM_USER,
        secrets.DEXCOM_PASS,
        secrets.DEXCOM_US
    )
    
    # State tracking for concurrent operations
    wifi_connected = False
    wifi_start_time = None
    dexcom_authenticated = False
    dexcom_logged_in = False
    dexcom_fetched = False
    
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
        while not wifi_connected and max_wait_remaining > 0 and wait_count < max_wait_remaining:
            status = wlan.status()
            if status < 0 or status >= 3:
                break
            print(f"Waiting for WiFi... (status: {status})")
            time.sleep(1)
            wait_count += 1
        
        if wlan.status() == 3:
            wifi_connected = True
            print(f"Connected! IP: {wlan.ifconfig()[0]}")
        else:
            print(f"WiFi connection failed after test (status: {wlan.status()})")
            raise RuntimeError("WiFi connection failed")
    else:
        # Normal flow: connect WiFi first
        wlan = connect_wifi()
        wifi_connected = True
    
    # Sync time
    sync_time()
    
    # Now authenticate and fetch Dexcom data
    print("Authenticating with Dexcom while preparing display...")
    if dexcom.authenticate():
        dexcom_authenticated = True
        if dexcom.login():
            dexcom_logged_in = True
            if dexcom.fetch_glucose():
                dexcom_fetched = True
    
    if not dexcom_fetched:
        print("Warning: Initial Dexcom fetch failed, will retry in main loop")
    
    print("Starting main loop...")
    last_fetch = time.time()
    
    # Main loop
    while True:
        try:
            current_time = time.time()
            
            # Fetch new glucose data periodically
            if current_time - last_fetch >= DEXCOM_UPDATE_INTERVAL:
                dexcom.fetch_glucose()
                last_fetch = current_time
            
            # Update display
            display.draw_glucose(
                dexcom.get_glucose_value(),
                dexcom.get_glucose_trend()
            )
            
            time.sleep(DISPLAY_UPDATE_INTERVAL)
            
        except KeyboardInterrupt:
            print("Interrupted by user")
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
