import time
import requests

LOGOUT_URL = "http://10.17.0.1:1000/logout.xml"
USERNAME = "YOUR_USERNAME"
PASSWORD = "YOUR_PASSWORD"

def logout():
    payload = {
        'mode': '193',
        'username': USERNAME,
        'password': PASSWORD,
        'a': str(int(time.time() * 1000))
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    try:
        response = requests.post(LOGOUT_URL, data=payload, headers=headers, timeout=5)
        print(f"Server Response: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    logout()