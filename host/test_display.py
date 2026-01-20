"""
Test the display layout using the simulator
Run this to preview how the clock will look on the Galactic Unicorn
"""

import sys
import requests
from simulator import DisplaySimulator, MockPicoGraphics, DISPLAY_GALACTIC_UNICORN
from datetime import datetime

try:
    import secrets
except ImportError:
    print("ERROR: secrets.py not found!")
    print("Copy secrets.py.example to secrets.py and configure your credentials.")
    sys.exit(1)

# Dexcom API Configuration
DEXCOM_APP_ID = "d89443d2-327c-4a6f-89e5-496bbb0317db"
DEXCOM_BASE_URL = "https://share2.dexcom.com" if secrets.DEXCOM_US else "https://shareous1.dexcom.com"

# Real glucose data (fetched from Dexcom)
glucose_value = None
glucose_trend = None

# Glucose display thresholds
GLUCOSE_LOW = 70
GLUCOSE_HIGH = 180

# Trend arrow mapping
TREND_ARROWS = {
    "DoubleUp": "↑↑",
    "SingleUp": "↑",
    "FortyFiveUp": "↗",
    "Flat": "→",
    "FortyFiveDown": "↘",
    "SingleDown": "↓",
    "DoubleDown": "↓↓",
    "NotComputable": "?",
    "RateOutOfRange": "!"
}


def fetch_dexcom_data():
    """Fetch real glucose data from Dexcom API"""
    global glucose_value, glucose_trend
    
    try:
        # Step 1: Authenticate
        print("Authenticating with Dexcom...")
        url = f"{DEXCOM_BASE_URL}/ShareWebServices/Services/General/AuthenticatePublisherAccount"
        payload = {
            "applicationId": DEXCOM_APP_ID,
            "accountName": secrets.DEXCOM_USER,
            "password": secrets.DEXCOM_PASS
        }
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        
        if response.status_code != 200:
            print(f"Authentication failed: {response.status_code}")
            return False
            
        account_id = response.json().strip('"')
        print(f"Authenticated. Account ID: {account_id[:8]}...")
        
        # Step 2: Login
        print("Logging in...")
        url = f"{DEXCOM_BASE_URL}/ShareWebServices/Services/General/LoginPublisherAccountById"
        payload = {
            "applicationId": DEXCOM_APP_ID,
            "accountId": account_id,
            "password": secrets.DEXCOM_PASS
        }
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")
            return False
            
        session_id = response.json().strip('"')
        print(f"Logged in. Session ID: {session_id[:8]}...")
        
        # Step 3: Fetch glucose data
        print("Fetching glucose data...")
        url = f"{DEXCOM_BASE_URL}/ShareWebServices/Services/Publisher/ReadPublisherLatestGlucoseValues"
        params = {
            "sessionId": session_id,
            "minutes": 10,
            "maxCount": 1
        }
        response = requests.post(url, params=params)
        
        if response.status_code != 200:
            print(f"Fetch failed: {response.status_code}")
            return False
            
        data = response.json()
        if data and len(data) > 0:
            latest = data[0]
            glucose_value = latest.get("Value")
            glucose_trend = latest.get("Trend")
            print(f"Glucose: {glucose_value} mg/dL, Trend: {glucose_trend}")
            return True
        else:
            print("No glucose data available")
            return False
            
    except Exception as e:
        print(f"Error fetching Dexcom data: {e}")
        return False


def draw_display(graphics):
    """Draw the clock and glucose display (matches main.py)"""
    # Clear display
    graphics.set_pen(0, 0, 0)
    graphics.clear()
    
    # Display glucose value with color coding
    if glucose_value:
        # Determine color based on glucose level
        if glucose_value < GLUCOSE_LOW:
            graphics.set_pen(255, 0, 0)  # Red - low
        elif glucose_value > GLUCOSE_HIGH:
            graphics.set_pen(255, 255, 0)  # Yellow - high
        else:
            graphics.set_pen(0, 255, 0)  # Green - in range
        
        # Glucose value starting from top
        glucose_str = str(glucose_value)
        graphics.text(glucose_str, 0, 0, scale=1)
    else:
        # No data
        graphics.set_pen(255, 255, 255)
        graphics.text("---", 10, 0, scale=1)
    
    graphics.update()


def main():
    """Run the display simulator"""
    global glucose_value, glucose_trend
    
    print("=" * 50)
    print("Galactic Unicorn Display Simulator")
    print("=" * 50)
    print(f"Display: 53x11 pixels")
    print("=" * 50)
    
    # Fetch real data
    if not fetch_dexcom_data():
        print("\nWARNING: Using mock data (failed to fetch from Dexcom)")
        glucose_value = 278
        glucose_trend = "Flat"
    
    print(f"\nDisplaying: {glucose_value} mg/dL, Trend: {glucose_trend}")
    print("Press ESC or Q to quit")
    print("=" * 50)
    
    simulator = DisplaySimulator()
    simulator.run(draw_display)


if __name__ == "__main__":
    main()
