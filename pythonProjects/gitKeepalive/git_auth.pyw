import subprocess
import re
import time
import atexit

PORTAL_URL = "http://10.17.0.1:1000"
USERNAME = "h8949637183"  # Replace with actual portal username
PASSWORD = "344677876" # with actual portal password
CHECK_INTERVAL = 180  # Ping every 3 minutes

current_token = None

def run_curl(endpoint, data=None):
    """Executes Windows native curl.exe with strict connection timeouts."""
    cmd = [
        "curl.exe", "-s", "-L", 
        "--connect-timeout", "3", 
        "--max-time", "5",
        "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "-H", "Connection: close"
    ]
    if data:
        cmd.extend(["-X", "POST"])
        for k, v in data.items():
            cmd.extend(["-d", f"{k}={v}"])
            
    cmd.append(f"{PORTAL_URL}{endpoint}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=6)
        return result.stdout
    except subprocess.TimeoutExpired:
        print("[!] curl.exe timed out.")
        return ""

def is_connected():
    """Verify internet connectivity by testing Google's endpoint."""
    cmd = ["curl.exe", "-s", "--connect-timeout", "3", "--max-time", "5", "http://clients3.google.com/generate_204"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=6)
        return res.stdout == ""
    except Exception:
        return False

def login():
    """Submit authentication directly to the gateway."""
    global current_token
    print("[*] Internet unreachable. Attempting login...")
    payload = {
        '4Tredir': 'http://detectportal.brave-http-only.com/',
        'username': USERNAME,
        'password': PASSWORD
    }
    
    html = run_curl("/login", data=payload)
    
    match = re.search(r'(?:keepalive|logout)\?([a-f0-9]{16})', html)
    if match:
        current_token = match.group(1)
        print(f"[+] Token acquired: {current_token}")
    else:
        print("[-] Login payload sent, awaiting connection activation...")

def send_keepalive():
    """Ping keepalive URL using active dynamic token."""
    global current_token
    if current_token:
        print(f"[*] Sending keepalive ping (Token: {current_token})...")
        run_curl(f"/keepalive?{current_token}")

def logout():
    """Send teardown signal upon exiting."""
    global current_token
    if current_token:
        print("[*] Cleaning up session...")
        run_curl(f"/logout?{current_token}")

atexit.register(logout)

def main():
    print("[+] Keepalive service started.")
    while True:
        if not is_connected():
            login()
        else:
            print("[+] Connection active.")
            send_keepalive()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()