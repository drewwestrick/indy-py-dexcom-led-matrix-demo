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
import network
import mip
import os
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('Drew', 'testtest')
wlan.isconnected()
mip.install('urequests')
print(os.listdir('lib/'))

mpremote mip install urequests
mpremote cp weather.py :weather.py
mpremote run weather.py
```