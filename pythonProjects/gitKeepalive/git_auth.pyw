import time
import requests
import re
import atexit

PORTAL_URL = "http://10.17.0.1:1000"
USERNAME = "h8949637183"
PASSWORD = "344677876"
CHECK_INTERVAL = 180  # Ping every 3 minutes

# Store the dynamic token globally so the logout function can access it
current_token = None
session = requests.Session()

def logout():
    """Triggered automatically when the script stops."""
    global current_token
    if current_token:
        try:
            logout_url = f"{PORTAL_URL}/logout?{current_token}"
            session.get(logout_url, timeout=5)
            print("Graceful logout successful.")
        except requests.RequestException:
            pass

# Register the logout function to run on script exit
atexit.register(logout)

def is_connected():
    """Check if internet access is active."""
    try:
        response = session.get("http://clients3.google.com/generate_204", timeout=5)
        return response.status_code == 204
    except requests.RequestException:
        return False

def login_and_get_token():
    """Authenticate and parse the HTML response for the session token."""
    global current_token
    payload = {
        'mode': '191',
        'username': USERNAME,
        'password': PASSWORD,
        'a': str(int(time.time() * 1000))
    }
    try:
        response = session.post(f"{PORTAL_URL}/login.xml", data=payload, timeout=10)
        
        # Search the returned HTML for the keepalive token using Regex
        match = re.search(r'keepalive\?([a-f0-9]{16})', response.text)
        if match:
            current_token = match.group(1)
            print(f"Authenticated. Token: {current_token}")
        else:
            print("Login failed or token not found.")
            current_token = None
            
    except requests.RequestException:
        current_token = None

def send_keepalive():
    """Send the GET request to keep the session active."""
    global current_token
    if current_token:
        try:
            session.get(f"{PORTAL_URL}/keepalive?{current_token}", timeout=5)
        except requests.RequestException:
            pass

def main():
    while True:
        if not is_connected():
            login_and_get_token()
        else:
            # If connected, ping the keepalive URL with the active token
            send_keepalive()
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()