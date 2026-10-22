import socket
import subprocess

PORTAL_IP = "10.17.0.1"
PORTAL_PORT = 1000

print("[1] Testing raw TCP socket connection...")
try:
    sock = socket.create_connection((PORTAL_IP, PORTAL_PORT), timeout=5)
    print(f"[+] TCP Connection to {PORTAL_IP}:{PORTAL_PORT} SUCCESSFUL.")
    sock.close()
except Exception as e:
    print(f"[-] TCP Connection FAILED: {e}")

print("\n[2] Testing HTTP GET via curl with chrome User-Agent...")
curl_cmd = [
    "curl.exe", "-v", "-s",
    "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "--max-time", "5",
    f"http://{PORTAL_IP}:{PORTAL_PORT}/"
]
res = subprocess.run(curl_cmd, capture_output=True, text=True)
print("--- CURL HEADERS / STDERR ---")
print(res.stderr[:500] if res.stderr else "No stderr output.")
print("--- CURL BODY SNIPPET ---")
print(res.stdout[:300] if res.stdout else "No body returned.")