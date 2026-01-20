import network
import time
import urequests

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('Drew', 'testtest')

while not wlan.isconnected():
    time.sleep(1)

print(f"WiFi connected, IP: {wlan.ifconfig()[0]}")

# Fetch weather for Carmel, Indiana using wttr.in API
# Format options: %t=temperature, %C=condition, %h=humidity, %w=wind
url = "https://wttr.in/Carmel,Indianapolis?format=%t"

print("Fetching weather...")
response = urequests.get(url)
temperature = response.text.strip()
response.close()

print(f"Current temperature in Indianapolis, IN: {temperature}")

# If you want more detailed info:
print("\nFetching detailed weather...")
url_detailed = "https://wttr.in/Indianapolis,Indiana?format=j1"
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