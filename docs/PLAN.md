# Project Plan: Galactic Unicorn Real-Time Clock & Dexcom Monitor

## 1. Project Goal
Create a standalone "Smart Clock" using the Pimoroni Galactic Unicorn (Pico 2 W). The device will connect to WiFi, sync time via NTP, and display the current time alongside live blood glucose data fetched from the Dexcom Share API.

## 2. Hardware Specification
* **Device:** Pimoroni Galactic Unicorn (Powered by Raspberry Pi Pico 2 W / RP2350).
* **Display Resolution:** 53 pixels wide x 11 pixels high.
* **Connectivity:** WiFi (Pico 2 W onboard).
* **Firmware:** Pimoroni MicroPython (RP2350 build).

## 3. Required Libraries & Drivers
The code must use the specific Pimoroni drivers included in their firmware:
* `galactic`: To interface with the LED matrix hardware.
* `picographics`: For drawing text and shapes (using `DISPLAY_GALACTIC_UNICORN`).
* `network`: Standard MicroPython WiFi.
* `urequests`: For HTTP POST requests.
* `ntptime`: For time synchronization.

## 4. The Dexcom Share API (Unofficial)
We are using the "Share" API. It requires a specific 3-step authentication flow.

**Global Constants:**
* **Application ID (UUID):** `d89443d2-327c-4a6f-89e5-496bbb0317db`
* **Base URL (US):** `https://share2.dexcom.com`
* **Base URL (Non-US):** `https://shareous1.dexcom.com`

**Authentication Flow:**
1.  **Get Account ID:**
    * `POST /ShareWebServices/Services/General/AuthenticatePublisherAccount`
    * **Body:** `{"applicationId": "...", "accountName": "USER", "password": "PASS"}`
    * **Returns:** A GUID string (Account ID).
2.  **Get Session ID:**
    * `POST /ShareWebServices/Services/General/LoginPublisherAccountById`
    * **Body:** `{"applicationId": "...", "password": "PASS", "accountId": "ACCOUNT_ID_FROM_STEP_1"}`
    * **Returns:** A GUID string (Session ID).
3.  **Get Glucose Data:**
    * `POST /ShareWebServices/Services/Publisher/ReadPublisherLatestGlucoseValues?sessionId=SESSION_ID&minutes=1440&maxCount=1`
    * **Returns:** JSON array with the reading. Key fields: `Value` (mg/dL) and `Trend` (Arrow direction).

## 5. Functional Requirements

### A. Connectivity
* Connect to WiFi using credentials stored in `secrets.py`.
* Sync system time using `ntptime.settime()` on boot.

### B. Display Layout (53x11 Grid)
The screen should be visually split into two zones:
* **Left Side (Time):**
    * Format: `HH:MM` (24h or 12h).
    * Color: White.
    * Font: Small enough to fit (e.g., `bitmap6` or `bitmap8`).
* **Right Side (Glucose):**
    * Value: The numeric glucose level (e.g., "120").
    * Color Logic:
        * **Red:** < 70 mg/dL (Low)
        * **Yellow:** > 180 mg/dL (High)
        * **Green:** 70-180 mg/dL (In Range)
    * Trend Indicator: A simple arrow or symbol indicating the trend.

### C. Main Loop Logic
1.  **Boot:** Connect WiFi, Sync Time.
2.  **Loop (Fast):** Update the Clock display every second.
3.  **Loop (Slow):** Fetch new Dexcom data every 5 minutes (300 seconds). Do NOT spam the API.
4.  **Error Handling:** If Dexcom fetch fails (token expired), re-run the Login/Auth flow automatically.

## 6. File Structure
* `main.py`: The application logic.
* `secrets.py`: Should contain:
    * `WIFI_SSID`
    * `WIFI_PASS`
    * `DEXCOM_USER`
    * `DEXCOM_PASS`
    * `DEXCOM_US` (Boolean)

## 7. Visual Mockup (ASCII)
```text
(0,0) ----------------------------------------------------- (53,0)
|  1  2  :  3  4           1  2  0      ^   |
|  (White Time)          (Color Glucose)    |
(0,11) ---------------------------------------------------- (53,11)