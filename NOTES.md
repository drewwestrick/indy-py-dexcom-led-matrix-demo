### WiFi Demo ###
``` python
import network

# Create WLAN object
wlan = network.WLAN(network.STA_IF)

# Activate the interface
wlan.active(True)

# Connect to WiFi (replace with your credentials)
wlan.connect('YOUR_SSID', 'YOUR_PASSWORD')

# Wait for connection (run this a few times until connected)
wlan.isconnected()

# Check connection status
wlan.status()
# Returns: 3 = connected, 0 = idle, 1 = connecting, -1/-2/-3 = errors

# Get IP address and network info
wlan.ifconfig()
# Returns: (IP, netmask, gateway, DNS)

# Check signal strength
wlan.status('rssi')

# Disconnect
wlan.disconnect()

# Deactivate interface
wlan.active(False)
```

### Install urequests & copy weather.py to device ###
``` shell
mpremote mip install urequests
mpremote cp weather.py :weather.py
mpremote run weather.py
```

``` python
import network
import time
from umqtt.simple import MQTTClient

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('Glassboard', 'design4HARDtech')

while not wlan.isconnected():
    time.sleep(1)

print(f"WiFi connected, IP: {wlan.ifconfig()[0]}")

# Fetch weather for Carmel, Indiana using wttr.in API
# Format options: %t=temperature, %C=condition, %h=humidity, %w=wind
url = "https://wttr.in/Carmel,Indiana?format=%t"

print("Fetching weather...")
response = urequests.get(url)
temperature = response.text.strip()
response.close()

print(f"Current temperature in Carmel, IN: {temperature}")

# If you want more detailed info:
print("\nFetching detailed weather...")
url_detailed = "https://wttr.in/Carmel,Indiana?format=j1"
response = urequests.get(url_detailed)

# Parse JSON response
import json
weather_data = json.loads(response.text)
response.close()

current = weather_data['current_condition'][0]
print(f"Temperature: {current['temp_F']}°F")
print(f"Feels like: {current['FeelsLikeF']}°F")
print(f"Condition: {current['weatherDesc'][0]['value']}")
print(f"Humidity: {current['humidity']}%")
print(f"Wind: {current['windspeedMiles']} mph")
```