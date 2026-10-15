import time
import requests

# Network Configuration
PORTAL_URL = "http://10.17.0.1:1000"
LOGIN_ENDPOINT = f"{PORTAL_URL}/login.xml"
USERNAME = "h8949637183"
PASSWORD = "344677876"
CHECK_INTERVAL = 180  # Interval in seconds (3 minutes)

def is_connected():
    """Verify internet connectivity by testing a fast external endpoint."""
    try:
        response = requests.get("http://clients3.google.com/generate_204", timeout=5)
        return response.status_code == 204
    except requests.RequestException:
        return False

def login():
    """Send authentication payload to the firewall portal."""
    payload = {
        'mode': '191',  # Standard Cyberoam/Sophos portal login mode
        'username': USERNAME,
        'password': PASSWORD,
        'a': str(int(time.time() * 1000))
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    try:
        requests.post(LOGIN_ENDPOINT, data=payload, headers=headers, timeout=10)
    except requests.RequestException:
        pass

def main():
    while True:
        if not is_connected():
            login()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()