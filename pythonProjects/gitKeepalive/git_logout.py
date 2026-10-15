import requests

LOGOUT_URL = "http://10.17.0.1:1000/logout"

def logout():
    try:
        # Requesting /logout directly signals the gateway to drop the session state
        response = requests.get(LOGOUT_URL, timeout=5)
        print("Logout signal sent.")
    except requests.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    logout()