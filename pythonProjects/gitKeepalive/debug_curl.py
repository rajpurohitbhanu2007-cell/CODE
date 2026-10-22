import subprocess
import re
import time

PORTAL_URL = "http://10.17.0.1:1003"
USERNAME = "h8949637183" # Replace with actual portal username
PASSWORD = "344677876"  # Replace with actual portal password

def run_curl(url, data=None):
    """Executes native Windows curl command and returns output string."""
    cmd = ["curl.exe", "-s", "-L", "--max-time", "10"]
    if data:
        cmd.extend(["-X", "POST"])
        for k, v in data.items():
            cmd.extend(["-d", f"{k}={v}"])
    cmd.append(url)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def test_login():
    print("[1] Fetching login page via native curl.exe...")
    html = run_curl(PORTAL_URL)
    
    magic_match = re.search(r'name="magic"\s+value="([a-f0-9]+)"', html)
    if not magic_match:
        print("[-] FAILED: Could not extract magic token.")
        print("Raw output snippet:", html[:200])
        return

    magic_token = magic_match.group(1)
    print(f"[+] Extracted magic token: {magic_token}")

    print("[2] Submitting POST authentication payload...")
    payload = {
        '4Tredir': 'http://detectportal.brave-http-only.com/',
        'magic': magic_token,
        'username': USERNAME,
        'password': PASSWORD
    }
    auth_output = run_curl(f"{PORTAL_URL}/", data=payload)
    print("[+] POST request completed.")

    print("[3] Testing internet connectivity...")
    test_out = run_curl("http://clients3.google.com/generate_204")
    if test_out == "":  # 204 No Content returns empty string in curl
        print("[+] SUCCESS: Authenticated and online!")
    else:
        print("[-] FAILED: Internet check did not return 204.")

if __name__ == "__main__":
    test_login()