import time
import requests
import re

PORTAL_URL = "http://10.17.0.1:1000"
USERNAME = "h8949637183"  # Ensure actual username is here
PASSWORD = "344677876"  # Ensure actual password is here

session = requests.Session()

# Spoof a standard Chrome/Windows browser profile
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
})

def debug_login():
    try:
        print(f"[1] Fetching login page from {PORTAL_URL}...")
        init_res = session.get(PORTAL_URL, timeout=5)
        print(f"    Initial HTTP Status: {init_res.status_code}")

        # Search for magic token
        magic_match = re.search(r'name="magic"\s+value="([a-f0-9]+)"', init_res.text)
        
        if not magic_match:
            print("[-] FAILED: Could not find 'magic' token in HTML.")
            print("    Raw HTML snippet received:")
            print(init_res.text[:300])
            return

        magic_token = magic_match.group(1)
        print(f"[+] Found magic token: {magic_token}")

        payload = {
            '4Tredir': 'http://detectportal.brave-http-only.com/',
            'magic': magic_token,
            'username': USERNAME,
            'password': PASSWORD
        }
        
        print("[2] Submitting POST authentication request...")
        auth_res = session.post(f"{PORTAL_URL}/", data=payload, timeout=10)
        print(f"    POST HTTP Status: {auth_res.status_code}")

        # Check internet connectivity
        print("[3] Testing internet connection...")
        check = session.get("http://clients3.google.com/generate_204", timeout=5)
        if check.status_code == 204:
            print("[+] SUCCESS: Authenticated and connected to internet!")
        else:
            print(f"[-] FAILED: Portal responded, but internet test returned status {check.status_code}.")

    except requests.RequestException as e:
        print(f"[-] ERROR: Network issue - {e}")

if __name__ == "__main__":
    debug_login()