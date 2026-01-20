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
DEXCOM_UPDATE_INTERVAL = 300  # Fetch glucose every 5 minutes (seconds)
DISPLAY_UPDATE_INTERVAL = 1    # Update display every second


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


def main():
    """Main program"""
    print("=" * 50)
    print("Galactic Unicorn - Dexcom Glucose Monitor")
    print("=" * 50)
    
    # Initialize hardware
    gu = GalacticUnicorn()
    graphics = PicoGraphics(DISPLAY_GALACTIC_UNICORN)
    gu.set_brightness(0.5)
    
    # Initialize display
    display = Display(gu, graphics)
    
    # Connect WiFi and sync time
    connect_wifi()
    sync_time()
    
    # Initialize Dexcom client
    dexcom = DexcomClient(
        secrets.DEXCOM_USER,
        secrets.DEXCOM_PASS,
        secrets.DEXCOM_US
    )
    
    # Initial authentication and fetch
    if dexcom.authenticate() and dexcom.login():
        dexcom.fetch_glucose()
    
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
