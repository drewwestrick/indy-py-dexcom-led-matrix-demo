import network
import time

# Create WLAN object
wlan = network.WLAN(network.STA_IF)

# Activate the interface
wlan.active(True)

# Connect to WiFi (replace with your credentials)
wlan.connect('Drew', 'testtest')

# Wait for connection (run this a few times until connected)
while not wlan.isconnected():
    print(f"Status: {wlan.status()}")
    time.sleep(1)
    # Returns: 3 = connected, 0 = idle, 1 = connecting, -1/-2/-3 = errors

# Get IP address and network info
wlan.ifconfig()
# Returns: (IP, netmask, gateway, DNS)

# Check signal strength
print(f"RSSI: {wlan.status('rssi')}")

# Disconnect
wlan.disconnect()

# Deactivate interface
wlan.active(False)