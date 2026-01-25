"""
Dexcom Share API Client
Handles authentication and glucose data fetching
"""

import time
import json
import urequests

# Constants
DEXCOM_APP_ID = "d89443d2-327c-4a6f-89e5-496bbb0317db"

class DexcomClient:
    """Client for Dexcom Share API"""
    
    def __init__(self, username, password, is_us=True):
        """
        Initialize Dexcom client
        
        Args:
            username: Dexcom Share username
            password: Dexcom Share password
            is_us: True for US servers, False for international
        """
        self.username = username
        self.password = password
        self.base_url = "https://share2.dexcom.com" if is_us else "https://shareous1.dexcom.com"
        self.account_id = None
        self.session_id = None
        self.glucose_value = None
        self.glucose_trend = None
    
    def authenticate(self):
        """
        Step 1: Authenticate to get Account ID
        Returns: Account ID or None
        """
        url = f"{self.base_url}/ShareWebServices/Services/General/AuthenticatePublisherAccount"
        headers = {"Content-Type": "application/json"}
        payload = {
            "applicationId": DEXCOM_APP_ID,
            "accountName": self.username,
            "password": self.password
        }
        
        print("Authenticating with Dexcom...")
        try:
            response = urequests.post(url, json=payload, headers=headers)
            status = response.status_code
            content = response.text
            response.close()
            
            if status == 200:
                # Parse the account ID from response
                import json
                self.account_id = self.account_id.strip('"') if isinstance(self.account_id, str) else self.account_id
                print(f"Authentication successful. Account ID: {self.account_id[:8]}...")
                return self.account_id
            else:
                print(f"Authentication failed: {status} - {content}")
                return None
        except OSError as e:
            # Network errors (e.g., -104 ECONNRESET)
            print(f"Network error during authentication: {e}")
            print("This often means the connection was reset. Try again in a moment.")
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    def login(self):
        """
        Step 2: Login with Account ID to get Session ID
        Returns: Session ID or None
        """
        if not self.account_id:
            print("No account ID - cannot login")
            return None
        
        url = f"{self.base_url}/ShareWebServices/Services/General/LoginPublisherAccountById"
        headers = {"Content-Type": "application/json"}
        payload = {
            "applicationId": DEXCOM_APP_ID,
            "accountId": self.account_id,
            "password": self.password
        }
        
        print("Logging in to Dexcom...")
        try:
            response = urequests.post(url, json=payload, headers=headers)
            status = response.status_code
            content = response.text
            response.close()
            
            if status == 200:
                # Parse the session ID from response
                import json
                self.session_id = self.session_id.strip('"') if isinstance(self.session_id, str) else self.session_id
                print(f"Login successful. Session ID: {self.session_id[:8]}...")
                return self.session_id
            else:
                print(f"Login failed: {status} - {content}")
                return None
        except OSError as e:
            # Network errors (e.g., -104 ECONNRESET)
            print(f"Network error during login: {e}")
            print("This often means the connection was reset. Try again in a moment.")
            return None
        except Exception as e:
            print(f"Login error: {e}")
            return None
    
    def fetch_glucose(self):
        """
        Step 3: Fetch late, _retry_count=0):
        """
        Step 3: Fetch latest glucose reading
        Returns: True if successful, False otherwise
        """
        if not self.session_id:
            print("No session ID - attempting re-authentication...")
            if not self.authenticate():
                return False
            if not self.login():
                return False
        
        url = f"{self.base_url}/ShareWebServices/Services/Publisher/ReadPublisherLatestGlucoseValues?sessionId={self.session_id}&minutes=10&maxCount=1"
        
        print("Fetching glucose data...")
        try:
            response = urequests.post(url)
            status = response.status_code
            content = response.text
            response.close()
            
            if status == 200:
                data = json.loads(content) if content else []
                
                if data and len(data) > 0:
                    reading = data[0]
                    self.glucose_value = reading.get("Value")
                    self.glucose_trend = reading.get("Trend")
                    print(f"Glucose: {self.glucose_value} mg/dL, Trend: {self.glucose_trend}")
                    return True
                else:
                    print("No recent glucose data available")
                    return False
            else:
                print(f"Fetch failed: {status}")
                
                # Session might have expired - try re-authenticating once
                if status in [401, 403, 500] and _retry_count == 0:
                    print("Session expired - re-authenticating...")
                    self.session_id = None
                    if self.authenticate() and self.login():
                        return self.fetch_glucose(_retry_count=1)  # Retry once with protection
            # Network errors (e.g., -104 ECONNRESET)
            print(f"Network error during fetch: {e}")
            print("Connection reset - will retry on next cycle")
            return False
        except Exception as e:
            print(f"Fetch error: {e}")
            return False
    
    def get_glucose_value(self):
        """Get current glucose value"""
        return self.glucose_value
    
    def get_glucose_trend(self):
        """Get current glucose trend"""
        return self.glucose_trend
