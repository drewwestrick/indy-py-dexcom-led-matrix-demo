import network
import time
import urequests
import json
import bluetooth
import struct
from micropython import const

# BLE Setup
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
_TEMP_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef1")
_HUMID_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef2")
_FLAG = bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY

class BLEWeather:
    def __init__(self):
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(lambda e, d: self.connections.add(d[0]) if e == _IRQ_CENTRAL_CONNECT else self.connections.discard(d[0]))
        self.connections = set()
        
        # Register service with temp and humidity characteristics
        ((self.temp_h, self.humid_h),) = self.ble.gatts_register_services((
            (_SERVICE_UUID, ((_TEMP_UUID, _FLAG), (_HUMID_UUID, _FLAG))),
        ))
        
        # Fixed advertising data with proper name AD structure
        # Format: Length(1) + Type(1) + Data
        # Flags: \x02\x01\x06 (length=2, type=flags, value=0x06)
        # Name: \x0e\x09CarmelWeather (length=14, type=complete_name, value=name)
        self.ble.gap_advertise(100000, adv_data=b'\x02\x01\x06\x0e\x09IndyWeather')
        
    def update(self, temp_f, humidity):
        # Write as UTF-8 strings with units (e.g., "72.5°F" and "65%")
        temp_str = f"{temp_f:.1f}°F".encode('utf-8')
        humid_str = f"{humidity}%".encode('utf-8')
        
        self.ble.gatts_write(self.temp_h, temp_str)
        self.ble.gatts_write(self.humid_h, humid_str)
        
        for conn in self.connections:
            self.ble.gatts_notify(conn, self.temp_h)
            self.ble.gatts_notify(conn, self.humid_h)

# Connect WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('Drew', 'testtest')
while not wlan.isconnected():
    time.sleep(1)
print(f"WiFi: {wlan.ifconfig()[0]}")

# Start BLE
ble = BLEWeather()
print("BLE advertising as 'IndyWeather'")

# Fetch and advertise weather every 5 minutes
while True:
    try:
        r = urequests.get("https://wttr.in/Indianapolis,Indiana?format=j1")
        data = json.loads(r.text)['current_condition'][0]
        r.close()
        
        temp = float(data['temp_F'])
        humidity = int(data['humidity'])
        
        print(f"Weather: {temp}°F, {humidity}%")
        ble.update(temp, humidity)
        
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(30)  # 30 seconds