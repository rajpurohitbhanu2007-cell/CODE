"""
GITwifi Suite - Modern Windows Native Clean Suite
Engineered for high performance, zero bloat, and resilient captive portal automation.
Developed with the help of Antigravity by StormDucky.

Features:
- Dual-Mode Shotgun Probing (Fastest captive portal detection)
- Resilient FortiGate Authentication with Multi-regex extraction
- HTTP / HTTPS CONNECT Tunneling Proxy Bridge for Hotspot Connection Sharing
- Profile Management & Auto-Switching
- Stealth Device-Fingerprint Spoofing
- Comprehensive Network & Port Diagnostics
- Windows System Tray & Native Toast / Audio Alerts
"""

from __future__ import annotations

import sys
import os
import copy
import time
import re
import json
import base64
import ctypes
from ctypes import wintypes
import socket
import select
import threading
import queue
import subprocess
import shutil
import ipaddress
from typing import Optional, Dict, Any, Callable, Set, Tuple
import requests
from requests.exceptions import RequestException, Timeout
from urllib.parse import urlparse, urlsplit, urlunsplit
import urllib3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageDraw, ImageTk

try:
    import winreg
    HAS_WINREG = True
except ImportError:
    winreg = None
    HAS_WINREG = False

# Optional Windows Sound library guard
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    winsound = None
    HAS_WINSOUND = False

# Optional System Tray library guard
try:
    import pystray
    from pystray import MenuItem as item
    HAS_PYSTRAY = True
except ImportError:
    pystray = None
    item = None
    HAS_PYSTRAY = False

# Windows High-DPI Awareness for crisp rendering
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# Disable noisy InsecureRequestWarning when dealing with self-signed captive portals
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# CONSTANTS & COMPILED REGEX PATTERNS
# ==========================================
CREATE_NO_WINDOW = 0x08000000

class AppConstants:
    DEFAULT_PORTAL_PORT: int = 1000
    DEFAULT_PROXY_PORT: int = 8888
    PROBE_URL: str = "http://connectivitycheck.gstatic.com/generate_204"
    HEADER_BUFFER_MAX: int = 8192
    SOCKET_CONNECT_TIMEOUT: float = 8.0
    PROBE_HTTP_TIMEOUT: float = 6.0
    AUTH_POST_TIMEOUT: float = 15.0
    KEEPALIVE_HTTP_TIMEOUT: float = 6.0
    LOGOUT_HTTP_TIMEOUT: float = 6.0
    SELECT_POLL_TIMEOUT: float = 10.0

# Precompiled Regular Expressions for High Performance
REGEX_MAGIC_FGT = re.compile(r"[?&]([0-9a-fA-F]{10,})")
REGEX_MAGIC_QUERY = re.compile(r"[?&]magic=([0-9a-fA-F]+)")
REGEX_MAGIC_INPUT1 = re.compile(r'name=["\']magic["\']\s+value=["\']([^"\']+)["\']')
REGEX_MAGIC_INPUT2 = re.compile(r'input[^>]*name=["\']magic["\'][^>]*value=["\']([^"\']+)["\']')
REGEX_KEEPALIVE_URL = re.compile(r"keepalive\?([0-9a-fA-F]+)")
REGEX_FGTAUTH_URL = re.compile(r"fgtauth\?([0-9a-fA-F]+)")
REGEX_LOGOUT_URL = re.compile(r"logout\?([0-9a-fA-F]+)")

# ==========================================
# WINDOWS NATIVE NETWORK TELEMETRY (MIB)
# ==========================================
class MIB_IF_ROW2(ctypes.Structure):
    _fields_ = [
        ('InterfaceLuid', ctypes.c_uint64),
        ('InterfaceIndex', wintypes.DWORD),
        ('InterfaceGuid', ctypes.c_byte * 16),
        ('Alias', wintypes.WCHAR * 257),
        ('Description', wintypes.WCHAR * 257),
        ('PhysicalAddressLength', wintypes.DWORD),
        ('PhysicalAddress', wintypes.BYTE * 32),
        ('PermanentPhysicalAddress', wintypes.BYTE * 32),
        ('Mtu', wintypes.DWORD),
        ('Type', wintypes.DWORD),
        ('TunnelType', ctypes.c_int),
        ('MediaType', ctypes.c_int),
        ('PhysicalMediumType', ctypes.c_int),
        ('AccessType', ctypes.c_int),
        ('DirectionType', ctypes.c_int),
        ('InterfaceAndOperStatusFlags', ctypes.c_byte),
        ('OperStatus', ctypes.c_int),
        ('AdminStatus', ctypes.c_int),
        ('MediaConnectState', ctypes.c_int),
        ('NetworkGuid', ctypes.c_byte * 16),
        ('ConnectionType', ctypes.c_int),
        ('TransmitLinkSpeed', ctypes.c_uint64),
        ('ReceiveLinkSpeed', ctypes.c_uint64),
        ('InOctets', ctypes.c_uint64),
        ('InUcastPkts', ctypes.c_uint64),
        ('InNUcastPkts', ctypes.c_uint64),
        ('InDiscards', ctypes.c_uint64),
        ('InErrors', ctypes.c_uint64),
        ('InUnknownProtos', ctypes.c_uint64),
        ('InUcastOctets', ctypes.c_uint64),
        ('InMulticastOctets', ctypes.c_uint64),
        ('InBroadcastOctets', ctypes.c_uint64),
        ('OutOctets', ctypes.c_uint64),
        ('OutUcastPkts', ctypes.c_uint64),
        ('OutNUcastPkts', ctypes.c_uint64),
        ('OutDiscards', ctypes.c_uint64),
        ('OutErrors', ctypes.c_uint64),
        ('OutUcastOctets', ctypes.c_uint64),
        ('OutMulticastOctets', ctypes.c_uint64),
        ('OutBroadcastOctets', ctypes.c_uint64),
        ('OutQLen', ctypes.c_uint64),
    ]

class MIB_IF_TABLE2(ctypes.Structure):
    _fields_ = [
        ('NumEntries', wintypes.ULONG),
        ('Table', MIB_IF_ROW2 * 1)
    ]

def get_system_network_io() -> Tuple[int, int]:
    """Retrieve cumulative (in_bytes, out_bytes) across active physical network adapters via iphlpapi."""
    try:
        pTable = ctypes.POINTER(MIB_IF_TABLE2)()
        if ctypes.windll.iphlpapi.GetIfTable2(ctypes.byref(pTable)) == 0:
            table = pTable.contents
            actual_table = ctypes.cast(
                ctypes.byref(table.Table),
                ctypes.POINTER(MIB_IF_ROW2 * table.NumEntries)
            ).contents
            tot_in, tot_out = 0, 0
            for row in actual_table:
                alias = str(row.Alias).strip()
                descr = str(row.Description).strip()
                # Exclude intermediate NDIS filters/schedulers and virtual/hotspot/VPN adapters to prevent double counting (Bug 41)
                is_excluded = any(x in alias.lower() or x in descr.lower() for x in [
                    'filter', 'scheduler', 'lightweight', 'wfp', 'qos', 'packet scheduler',
                    'virtual', 'wi-fi direct', 'direct virtual', 'vmware', 'virtualbox',
                    'hyper-v', 'vethernet', 'host-only', 'loopback', 'teredo', 'isatap',
                    'tap-windows', 'wireguard', 'tailscale', 'zerotier', 'npcap', 'pcap',
                    'bluetooth'
                ])
                if not is_excluded and row.OperStatus == 1 and row.Type != 24:
                    tot_in += row.InOctets
                    tot_out += row.OutOctets
            ctypes.windll.iphlpapi.FreeMibTable(pTable)
            return tot_in, tot_out
    except Exception:
        pass
    return 0, 0

# ==========================================
# PYINSTALLER SAFE PATHING
# ==========================================
def get_app_dir() -> str:
    """Return correct application directory whether run from source or PyInstaller .exe."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def _generate_app_icon(path: str) -> None:
    """Draw a styled Wi-Fi badge icon and save it as a multi-size .ico file."""
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    for sz in sizes:
        img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        cx, cy = sz // 2, sz // 2

        # Background circle - deep navy / slate
        r = sz // 2 - 1
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#1a1c23")

        # Wi-Fi arcs - accent blue
        arc_color = "#3d70f5"
        dot_color = "#80a5ff"
        margin = sz * 0.08
        for factor in [0.82, 0.56, 0.30]:
            ar = int((sz // 2 - margin) * factor)
            if ar < 2:
                continue
            x0, y0 = cx - ar, cy - ar
            x1, y1 = cx + ar, cy + ar
            width = max(1, sz // 26)
            draw.arc([x0, y0, x1, y1], start=210, end=330, fill=arc_color, width=width)

        # Center dot
        dr = max(2, sz // 18)
        draw.ellipse([cx - dr, cy + dr, cx + dr, cy + dr * 3], fill=dot_color)
        images.append(img)

    # In Pillow, save from largest image (256x256) as master canvas so all smaller frames are embedded correctly.
    images[-1].save(path, format="ICO", append_images=images[:-1], bitmap_format="bmp")

# ==========================================
# WINDOWS DPAPI CREDENTIAL ENCRYPTION
# ==========================================
class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]

def dpapi_encrypt(plain_text: str) -> str:
    """Encrypt a string using Windows DPAPI (user-specific key)."""
    if not plain_text:
        return ""
    try:
        data_bytes = plain_text.encode("utf-8")
        blob_in = DATA_BLOB(len(data_bytes), ctypes.cast(ctypes.create_string_buffer(data_bytes), ctypes.POINTER(ctypes.c_byte)))
        blob_out = DATA_BLOB()
        if ctypes.windll.crypt32.CryptProtectData(ctypes.byref(blob_in), "gitwifi", None, None, None, 0, ctypes.byref(blob_out)):
            encrypted = ctypes.string_at(blob_out.pbData, blob_out.cbData)
            ctypes.windll.kernel32.LocalFree(blob_out.pbData)
            return "dpapi:" + base64.b64encode(encrypted).decode("ascii")
        else:
            raise RuntimeError("CryptProtectData failed")
    except Exception as e:
        print(f"[Crypto] DPAPI encryption error: {e}")
        # Return empty string instead of leaking plaintext password to disk
        return ""

def dpapi_decrypt(cipher_text: str) -> str:
    """Decrypt a DPAPI string. Returns empty string on decryption failure to prevent sending ciphertext."""
    if not cipher_text:
        return ""
    if not cipher_text.startswith("dpapi:"):
        return cipher_text
    try:
        raw_b64 = cipher_text[6:]
        cipher_bytes = base64.b64decode(raw_b64.encode("ascii"))
        blob_in = DATA_BLOB(len(cipher_bytes), ctypes.cast(ctypes.create_string_buffer(cipher_bytes), ctypes.POINTER(ctypes.c_byte)))
        blob_out = DATA_BLOB()
        if ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)):
            decrypted = ctypes.string_at(blob_out.pbData, blob_out.cbData).decode("utf-8")
            ctypes.windll.kernel32.LocalFree(blob_out.pbData)
            return decrypted
        else:
            raise RuntimeError("CryptUnprotectData failed")
    except Exception as e:
        print(f"[Crypto] DPAPI decryption error: {e}")
        # Crucial: Never return ciphertext as plaintext password to avoid sending literal 'dpapi:...' strings
        return ""

CONFIG_PATH: str = os.path.join(get_app_dir(), "config.json")

DEFAULT_CONFIG = {
    "profiles": [
        {"name": "Primary", "username": "", "password": ""}
    ],
    "active_profile_index": 0,
    "user_agent_mode": "Windows Chrome",
    "custom_user_agent": "",
    "sound_alerts": True,
    "desktop_notifications": True,
    "keepalive_interval": 120,
    "adaptive_keepalive": True,
    "auto_reconnect": True,
    "auto_profile_switching": True,
    "auto_start_enabled": False,
    "idle_logout_enabled": False,
    "idle_logout_minutes": 30,
    "doh_fallback_enabled": False,
    "doh_endpoint": "https://1.1.1.1/dns-query",
    "proxy_enabled": False,
    "proxy_port": 8888,
    "proxy_sniff_headers": False,
    "trusted_portal_hosts": ["172.15.1.2"],
    "last_gateway": "",
    "last_magic": "",
    "portal_host": "",
    "portal_port": AppConstants.DEFAULT_PORTAL_PORT,
    "portal_scheme": "http",
    "live_monitor_enabled": True
}

SPOOF_USER_AGENTS = {
    "Windows Chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Windows Edge": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    "Android Pixel (Mobile Spoof)": "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
    "iPhone 15 (iOS Spoof)": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    "MacBook Safari": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15"
}

_config_lock = threading.RLock()

def load_settings() -> Dict[str, Any]:
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    if os.path.exists(CONFIG_PATH):
        try:
            # Bug 24 fix: Use utf-8-sig to automatically handle BOM and standard UTF-8
            with open(CONFIG_PATH, "r", encoding="utf-8-sig") as f:
                loaded = json.load(f)
            if not isinstance(loaded, dict):
                raise TypeError(f"Config root must be a dict, got {type(loaded).__name__}")
            for k, v in DEFAULT_CONFIG.items():
                if k not in loaded:
                    loaded[k] = copy.deepcopy(v)
            
            # Validate types to prevent crashes
            if not isinstance(loaded.get("profiles"), list):
                loaded["profiles"] = copy.deepcopy(DEFAULT_CONFIG["profiles"])
            if not isinstance(loaded.get("trusted_portal_hosts"), list):
                loaded["trusted_portal_hosts"] = ["172.15.1.2"]
            elif "172.15.1.2" not in loaded["trusted_portal_hosts"]:
                loaded["trusted_portal_hosts"].append("172.15.1.2")
            try:
                loaded["keepalive_interval"] = max(10, int(loaded.get("keepalive_interval", 120)))
            except (ValueError, TypeError):
                loaded["keepalive_interval"] = 120

            try:
                loaded["active_profile_index"] = max(0, int(loaded.get("active_profile_index", 0)))
            except (ValueError, TypeError):
                loaded["active_profile_index"] = 0

            cfg = loaded
        except (json.JSONDecodeError, OSError, TypeError, UnicodeError) as e:
            print(f"[Config] Error loading settings, backing up and using defaults: {e}")
            try:
                bak_path = CONFIG_PATH + f".corrupt.{int(time.time())}.bak"
                shutil.copy2(CONFIG_PATH, bak_path)
                print(f"[Config] Corrupt config saved to {bak_path}")
            except Exception:
                pass

    # Decrypt passwords in profiles if encrypted; preserve raw ciphertext if decryption fails (Bug 12)
    for p in cfg.get("profiles", []):
        if isinstance(p, dict) and "password" in p:
            raw_val = str(p["password"])
            decrypted = dpapi_decrypt(raw_val)
            if not decrypted and raw_val.startswith("dpapi:"):
                p["password"] = ""
                p["_password_raw"] = raw_val
            else:
                p["password"] = decrypted

    # Decrypt cached magic token if present (N1)
    if "last_magic" in cfg and isinstance(cfg["last_magic"], str):
        raw_m = cfg["last_magic"]
        if raw_m.startswith("dpapi:"):
            decrypted_m = dpapi_decrypt(raw_m)
            if not decrypted_m:
                cfg["_last_magic_raw"] = raw_m
                cfg["last_magic"] = ""
            else:
                cfg["last_magic"] = decrypted_m

    return cfg

def save_settings(cfg: Dict[str, Any]) -> None:
    tmp_path = CONFIG_PATH + ".tmp"
    try:
        with _config_lock:
            # Create a deep copy under lock to encrypt passwords on disk without modifying in-memory plaintext
            disk_cfg = copy.deepcopy(cfg)
            for p in disk_cfg.get("profiles", []):
                if isinstance(p, dict) and "password" in p:
                    pwd = p["password"]
                    if not pwd and p.get("_password_raw"):
                        # Keep existing ciphertext if password was not changed/empty
                        p["password"] = p["_password_raw"]
                    elif pwd:
                        enc = dpapi_encrypt(pwd)
                        if enc:
                            p["password"] = enc
                        elif p.get("_password_raw"):
                            # Bug 12 fix: If encrypt failed transiently, preserve existing valid ciphertext
                            p["password"] = p["_password_raw"]
                    p.pop("_password_raw", None)

            # N1: Encrypt last_magic before saving to disk
            if "last_magic" in disk_cfg and disk_cfg["last_magic"]:
                enc_m = dpapi_encrypt(disk_cfg["last_magic"])
                disk_cfg["last_magic"] = enc_m if enc_m else disk_cfg.get("_last_magic_raw", "")
            else:
                # Bug 59 fix: If last_magic is empty (e.g. user logged out or session ended), do NOT resurrect _last_magic_raw
                disk_cfg["last_magic"] = ""
            disk_cfg.pop("_last_magic_raw", None)

            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(disk_cfg, f, indent=4)
            os.replace(tmp_path, CONFIG_PATH)
    except Exception as e:
        print(f"[Config] Error saving config: {e}")

# ==========================================
# WINDOWS REGISTRY AUTOSTART MANAGEMENT
# ==========================================
RUN_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_REG_NAME = "GITwifi"

def is_auto_start_registered() -> bool:
    """Check if GITwifi is registered in HKCU Run registry key and points to an existing file."""
    if not HAS_WINREG:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_REG_KEY, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, RUN_REG_NAME)
            if not val:
                return False
            # Bug 46 fix: Verify the registered binary or script actually still exists on disk
            raw_path = val.split('"')[1] if '"' in val else val.split()[0]
            return os.path.exists(raw_path)
    except (FileNotFoundError, OSError):
        return False

def set_auto_start_registered(enable: bool) -> bool:
    """Register or remove GITwifi silent startup in HKCU Run registry key with --minimized flag."""
    if not HAS_WINREG:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_REG_KEY, 0, winreg.KEY_SET_VALUE) as key:
            if enable:
                if getattr(sys, "frozen", False):
                    cmd = f'"{sys.executable}" --minimized'
                else:
                    # Bug 46 fix: Case-insensitive python.exe replacement and dynamic __file__ path
                    py_exe = sys.executable
                    pyw_exe = re.sub(r'python\.exe$', 'pythonw.exe', py_exe, flags=re.IGNORECASE)
                    if not os.path.exists(pyw_exe):
                        pyw_exe = py_exe
                    script_path = os.path.abspath(__file__)
                    cmd = f'"{pyw_exe}" "{script_path}" --minimized'
                winreg.SetValueEx(key, RUN_REG_NAME, 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(key, RUN_REG_NAME)
                except FileNotFoundError:
                    pass
        return True
    except OSError as e:
        print(f"[Registry] Autostart update error: {e}")
        return False

# ==========================================
# WINDOWS USER IDLE TELEMETRY
# ==========================================
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("dwTime", wintypes.DWORD)
    ]

def get_system_idle_seconds() -> float:
    """Return seconds since user last pressed a key or moved the mouse using Windows API."""
    try:
        lii = LASTINPUTINFO()
        lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
        if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
            if hasattr(ctypes.windll.kernel32, "GetTickCount64"):
                ctypes.windll.kernel32.GetTickCount64.restype = ctypes.c_uint64
                now_ticks = ctypes.windll.kernel32.GetTickCount64()
            else:
                ctypes.windll.kernel32.GetTickCount.restype = ctypes.c_uint32
                now_ticks = ctypes.windll.kernel32.GetTickCount()
            last_input = lii.dwTime & 0xFFFFFFFF
            millis = (now_ticks & 0xFFFFFFFF) - last_input
            if millis < 0:
                millis += 0x100000000
            return max(0.0, float(millis) / 1000.0)
    except Exception:
        pass
    return 0.0

def get_hotspot_bind_ip(campus_ip: Optional[str] = None) -> str:
    """
    Find safe IP for hotspot proxy to avoid binding to open campus IP (0.0.0.0).
    Prefers virtual adapter / hotspot private subnets (192.168.137.x or other 192.168.x.x / 172.16-31.x.x).
    Falls back to 127.0.0.1 if no separate local interface exists.
    """
    try:
        if not campus_ip:
            s = None
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                campus_ip = s.getsockname()[0]
            except (socket.error, OSError):
                pass
            finally:
                if s:
                    try:
                        s.close()
                    except Exception:
                        pass

        hostname = socket.gethostname()
        all_ips = socket.gethostbyname_ex(hostname)[2]
        
        # 1. Look for Windows Mobile Hotspot default subnet (192.168.137.x)
        for ip in all_ips:
            if ip.startswith("192.168.137."):
                return ip

        # 2. Look for any private non-campus IP (including 10.x.x.x)
        for ip in all_ips:
            if ip != campus_ip and (ip.startswith("192.168.") or ip.startswith("10.") or re.match(r"172\.(1[6-9]|2\d|3[01])\.", ip)):
                return ip

    except (socket.error, OSError):
        pass

    return "127.0.0.1"

def get_default_gateway() -> Optional[str]:
    """Retrieve Windows default IPv4 gateway via 'route print' selecting the route with lowest metric (ignoring virtual/hotspot/APIPA routes - Bug 20)."""
    best_gw: Optional[str] = None
    lowest_metric: float = float("inf")
    try:
        out = subprocess.check_output(
            ["route", "print", "-4", "0.0.0.0"],
            text=True, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW
        )
        for line in out.splitlines():
            parts = line.split()
            # route print row format: Network   Netmask   Gateway   Interface   Metric
            if len(parts) >= 5 and parts[0] == "0.0.0.0" and parts[1] == "0.0.0.0":
                gw = parts[2]
                iface = parts[3]
                try:
                    metric = int(parts[4])
                except ValueError:
                    metric = 9999
                # Bug 20 fix: Exclude APIPA, loopback, and local Windows hotspot subnet (192.168.137.x)
                if not re.fullmatch(r"\d+\.\d+\.\d+\.\d+", gw) or gw == "0.0.0.0":
                    continue
                if gw.startswith("127.") or gw.startswith("169.254.") or gw == "192.168.137.1":
                    continue
                if iface.startswith("127.") or iface.startswith("169.254.") or iface.startswith("192.168.137."):
                    continue
                if metric < lowest_metric:
                    lowest_metric = metric
                    best_gw = gw
    except Exception:
        pass
    return best_gw


# ==========================================
# PROXY SERVER (HTTP CONNECT & TUNNELING)
# ==========================================
class HotspotProxyServer:
    def __init__(self, host: Optional[str] = None, port: int = AppConstants.DEFAULT_PROXY_PORT, logger: Optional[Callable[[str], None]] = None, campus_ip: Optional[str] = None):
        self.campus_ip: Optional[str] = campus_ip
        self.explicit_host: Optional[str] = host
        self.host: str = host or get_hotspot_bind_ip(campus_ip)
        self.port: int = port
        self.logger: Optional[Callable[[str], None]] = logger
        self.running: bool = False
        self.server_sock: Optional[socket.socket] = None
        self.thread: Optional[threading.Thread] = None
        self.active_sockets: Set[socket.socket] = set()
        self.sockets_lock: threading.Lock = threading.Lock()
        self.host_lock: threading.Lock = threading.Lock()
        self.active_clients: int = 0
        self.max_clients: int = 64
        self.clients_lock: threading.Lock = threading.Lock()
        # Feature 3: Data Usage & Bandwidth Metering (Atomic bytes counters)
        self.bytes_sent: int = 0
        self.bytes_recv: int = 0
        self.stats_lock: threading.Lock = threading.Lock()
        # Diagnostic Mode: Plaintext HTTP/CONNECT traffic header sniffing
        self.sniff_headers: bool = False

    def log(self, msg: str) -> None:
        if self.logger:
            self.logger(f"[Proxy] {msg}")

    def update_bind_host(self, campus_ip: Optional[str] = None) -> None:
        with self.host_lock:
            self.campus_ip = campus_ip
            old_host = self.host
            if self.explicit_host:
                self.host = self.explicit_host
            else:
                self.host = get_hotspot_bind_ip(campus_ip)
            new_host = self.host

        # Bug 31 fix: If bind host changed while proxy is running, restart listener on the new IP
        if self.running and old_host and new_host and old_host != new_host:
            self.log(f"[Proxy] Hotspot interface changed ({old_host} -> {new_host}). Rebinding proxy...")
            self.stop()
            self.start()

    def _register_socket(self, sock: socket.socket) -> None:
        with self.sockets_lock:
            self.active_sockets.add(sock)

    def _unregister_socket(self, sock: socket.socket) -> None:
        with self.sockets_lock:
            self.active_sockets.discard(sock)

    def start(self) -> bool:
        if self.running:
            return True
        try:
            if not isinstance(self.port, int) or not (1 <= self.port <= 65535):
                raise ValueError(f"Proxy port {self.port} is outside valid range (1-65535)")
            self.update_bind_host(self.campus_ip)
            with self.host_lock:
                bind_ip = self.host
            # Retry loop for TIME_WAIT / EADDRINUSE (Bug 17)
            bound = False
            for attempt in range(1, 4):
                try:
                    # Recreate socket on each attempt to ensure clean state after bind failure
                    if self.server_sock:
                        try:
                            self.server_sock.close()
                        except Exception:
                            pass
                    self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
                        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
                    else:
                        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    self.server_sock.bind((bind_ip, self.port))
                    bound = True
                    break
                except OSError as be:
                    # Windows WSAEADDRINUSE is 10048; standard errno is 48 or 98
                    if getattr(be, "winerror", None) == 10048 or getattr(be, "errno", None) in (48, 98, 10048):
                        if attempt < 3:
                            self.log(f"Proxy port {self.port} in TIME_WAIT / in use. Retrying bind in 1s (attempt {attempt}/3)...")
                            time.sleep(1.0)
                            continue
                    raise be

            if not bound:
                raise OSError(f"Could not bind to {bind_ip}:{self.port} after retries")

            self.server_sock.listen(50)
            self.server_sock.settimeout(1.0)
            self.running = True
            self.thread = threading.Thread(target=self._listen_loop, args=(self.server_sock,), daemon=True)
            self.thread.start()
            # N2: Accurate logging on loopback fallback vs interface bind
            if bind_ip == "127.0.0.1":
                self.log(f"Sharing Proxy active on loopback only ({bind_ip}:{self.port}) (hotspot clients won't be able to connect)")
            else:
                self.log(f"Sharing Proxy securely active on {bind_ip}:{self.port}")
            return True
        except Exception as e:
            self.running = False
            self.log(f"Failed to start proxy on {getattr(self, 'host', 'unknown')}:{self.port}: {e}")
            if self.server_sock:
                try:
                    self.server_sock.close()
                except Exception:
                    pass
                self.server_sock = None
            return False

    def stop(self) -> None:
        self.running = False
        with self.sockets_lock:
            for s in list(self.active_sockets):
                try:
                    s.shutdown(socket.SHUT_RDWR)
                except (socket.error, OSError):
                    pass
                try:
                    s.close()
                except (socket.error, OSError):
                    pass
            self.active_sockets.clear()

        if self.server_sock:
            try:
                self.server_sock.close()
            except (socket.error, OSError):
                pass
            self.server_sock = None
        self.log("Proxy stopped and active tunnels terminated.")

    def _listen_loop(self, sock: socket.socket) -> None:
        while self.running:
            try:
                client_sock, addr = sock.accept()
            except socket.timeout:
                continue
            except (socket.error, OSError) as e:
                # Bug 3 fix: Only terminate listen loop if the listening server socket itself is closed or invalidated
                if not self.running or sock.fileno() == -1:
                    break
                time.sleep(0.05)
                continue

            try:
                with self.clients_lock:
                    if self.active_clients >= self.max_clients:
                        try:
                            client_sock.sendall(b"HTTP/1.1 503 Service Unavailable\r\nConnection: close\r\n\r\nProxy client limit reached.\r\n")
                        except Exception:
                            pass
                        try:
                            client_sock.close()
                        except Exception:
                            pass
                        continue
                    self.active_clients += 1
                threading.Thread(target=self._client_worker_wrapper, args=(client_sock, addr), daemon=True).start()
            except Exception as client_err:
                try:
                    client_sock.close()
                except Exception:
                    pass

    def _client_worker_wrapper(self, client_sock: socket.socket, addr: Any) -> None:
        try:
            self._handle_client(client_sock, addr)
        finally:
            with self.clients_lock:
                self.active_clients = max(0, self.active_clients - 1)

    def _parse_target_host_port(self, target: str, default_port: int = 80) -> tuple[str, int]:
        if target.startswith("https://"):
            default_port = 443
        raw = target if (target.startswith("http://") or target.startswith("https://")) else ("http://" + target)
        try:
            parsed = urlsplit(raw)
            host = parsed.hostname or target.split("/")[0]
            port = parsed.port or default_port
            return host, port
        except Exception:
            host = target.split("/")[0]
            port = default_port
            if ":" in host:
                parts = host.rsplit(":", 1)
                try:
                    port = int(parts[1])
                    host = parts[0].strip("[]")
                except ValueError:
                    pass
            return host, port

    def _strip_proxy_headers(self, raw_request: bytes, client_ip: str = "Client") -> bytes:
        if b"\r\n\r\n" not in raw_request:
            return raw_request
        header_blob, body = raw_request.split(b"\r\n\r\n", 1)
        lines = header_blob.split(b"\r\n")
        
        # Convert absolute URI in the request line to relative path (e.g., GET http://example.com/foo;jsessionid=1?x=2 -> GET /foo;jsessionid=1?x=2)
        first_line_parts = lines[0].split(b" ", 2)
        req_method = "GET"
        req_path = "/"
        if len(first_line_parts) == 3:
            method, target_bytes, proto = first_line_parts
            req_method = method.decode("latin1", errors="ignore")
            target_str = target_bytes.decode("latin1", errors="ignore")
            req_path = target_str
            if target_str.startswith("http://") or target_str.startswith("https://"):
                parsed = urlsplit(target_str)
                path = parsed.path or "/"
                if parsed.query:
                    path += "?" + parsed.query
                req_path = path
                lines[0] = method + b" " + path.encode("latin1") + b" " + proto

        # Bug 4: Two-pass header processing for order-independent WebSocket detection
        is_websocket = False
        sniffed_host = ""
        sniffed_ua = ""
        for line in lines[1:]:
            lower = line.lower()
            if lower.startswith(b"upgrade:") and b"websocket" in lower:
                is_websocket = True
            elif lower.startswith(b"host:"):
                sniffed_host = line.split(b":", 1)[1].strip().decode("latin1", errors="ignore")
            elif lower.startswith(b"user-agent:"):
                sniffed_ua = line.split(b":", 1)[1].strip().decode("latin1", errors="ignore")

        # Diagnostic Mode: Sniff HTTP metadata (Bug 38 fix: scrub query parameters to protect user credentials/tokens)
        if self.sniff_headers:
            host_display = sniffed_host or "unknown-host"
            ua_display = f" | UA: {sniffed_ua}" if sniffed_ua else ""
            clean_path = req_path.split("?")[0] if "?" in req_path else req_path
            self.log(f"[Sniff] {client_ip} -> {req_method} http://{host_display}{clean_path}{ua_display}")

        cleaned_lines = [lines[0]]
        for line in lines[1:]:
            lower = line.lower()
            if (lower.startswith(b"proxy-connection:")
                    or lower.startswith(b"proxy-authenticate:")
                    or lower.startswith(b"proxy-authorization:")):
                continue
            if lower.startswith(b"connection:") and not is_websocket:
                continue
            cleaned_lines.append(line)

        if not is_websocket:
            cleaned_lines.append(b"Connection: close")
        return b"\r\n".join(cleaned_lines) + b"\r\n\r\n" + body

    def _is_safe_target(self, host: str, port: int) -> Optional[List[Tuple[str, int]]]:
        """
        Prevent open relay / SSRF exploitation against loopback, private RFC1918, link-local,
        unspecified (0.0.0.0), sensitive service ports, and the host PC's own interface IPs.
        Returns list of safe (resolved_ip, port) candidates, or None if unsafe/blocked. (Bug 6, Bug 33)
        """
        try:
            if port in (22, 23, 25, 445, 139, 3389, self.port):
                return None
            
            # Collect host machine's own local interface IPs to prevent hotspot clients from accessing host services
            local_host_ips = {"127.0.0.1", "::1"}
            try:
                for info in socket.getaddrinfo(socket.gethostname(), None):
                    local_host_ips.add(info[4][0])
            except Exception:
                pass

            addrs = socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
            safe_targets = []
            for family, socktype, proto, canonname, sockaddr in addrs:
                ip_str = sockaddr[0]
                if ip_str in local_host_ips:
                    return None
                ip_obj = ipaddress.ip_address(ip_str)
                # Check for loopback, IPv4-mapped IPv6, link-local, unspecified, reserved, or private IPs
                if ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_unspecified or ip_obj.is_reserved or ip_obj.is_private:
                    return None
                if isinstance(ip_obj, ipaddress.IPv6Address) and ip_obj.ipv4_mapped:
                    mapped = ip_obj.ipv4_mapped
                    if mapped.is_loopback or mapped.is_link_local or mapped.is_unspecified or mapped.is_reserved or mapped.is_private:
                        return None
                    if str(mapped) in local_host_ips:
                        return None
                target_cand = (ip_str, port)
                if target_cand not in safe_targets:
                    safe_targets.append(target_cand)
            return safe_targets if safe_targets else None
        except Exception:
            return None

    def _handle_client(self, client_sock: socket.socket, addr: Any) -> None:
        remote_sock = None
        try:
            request = b""
            # Bug 36 fix: Add an overall header read timeout deadline (15s) to guard against slowloris-style hangs
            header_deadline = time.monotonic() + 15.0
            while b"\r\n\r\n" not in request and len(request) < AppConstants.HEADER_BUFFER_MAX:
                remaining = header_deadline - time.monotonic()
                if remaining <= 0:
                    break
                client_sock.settimeout(min(AppConstants.SELECT_POLL_TIMEOUT, remaining))
                chunk = client_sock.recv(2048)
                if not chunk:
                    break
                request += chunk

            if not request or b"\r\n" not in request:
                client_sock.close()
                return

            # Bug 2: Guard against partial requests lacking \r\n\r\n
            if b"\r\n\r\n" not in request:
                client_sock.sendall(b"HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\nPartial or malformed HTTP request.\r\n")
                client_sock.close()
                return

            header_part, trailing_bytes = request.split(b"\r\n\r\n", 1)
            first_line = header_part.decode("latin1", errors="ignore").split("\r\n")[0]
            parts = first_line.split()
            if len(parts) < 3:
                client_sock.sendall(b"HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\nMalformed HTTP request.\r\n")
                client_sock.close()
                return

            method, target, _ = parts
            client_ip = addr[0] if isinstance(addr, (list, tuple)) and addr else str(addr)

            if method == "CONNECT":
                try:
                    host, port = self._parse_target_host_port(target, default_port=443)
                except (UnicodeError, ValueError):
                    client_sock.sendall(b"HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\nInvalid CONNECT destination.\r\n")
                    client_sock.close()
                    return

                if self.sniff_headers:
                    self.log(f"[Sniff] {client_ip} -> CONNECT {host}:{port} (Encrypted Tunnel)")

                safe_targets = self._is_safe_target(host, port)
                if not safe_targets:
                    client_sock.sendall(b"HTTP/1.1 403 Forbidden\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\nAccess to local/restricted target forbidden.\r\n")
                    client_sock.close()
                    return
                # Bug 33 fix: Dual-stack fallback across all resolved safe addresses
                conn_err = None
                for cand in safe_targets:
                    try:
                        remote_sock = socket.create_connection(cand, timeout=AppConstants.SOCKET_CONNECT_TIMEOUT)
                        break
                    except Exception as ce:
                        conn_err = ce
                        continue
                if not remote_sock:
                    client_sock.sendall(f"HTTP/1.1 502 Bad Gateway\r\nConnection: close\r\n\r\nUpstream connect failed: {conn_err}\r\n".encode("utf-8"))
                    client_sock.close()
                    return

                client_sock.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                # Forward any bytes client sent immediately after CONNECT header
                if trailing_bytes:
                    remote_sock.sendall(trailing_bytes)
                    with self.stats_lock:
                        self.bytes_sent += len(trailing_bytes)
            else:
                try:
                    host, port = self._parse_target_host_port(target, default_port=80)
                except (UnicodeError, ValueError):
                    client_sock.sendall(b"HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\nInvalid target host.\r\n")
                    client_sock.close()
                    return

                sanitized_request = self._strip_proxy_headers(request, client_ip=client_ip)
                safe_targets = self._is_safe_target(host, port)
                if not safe_targets:
                    client_sock.sendall(b"HTTP/1.1 403 Forbidden\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\nAccess to local/restricted target forbidden.\r\n")
                    client_sock.close()
                    return
                # Bug 33 fix: Dual-stack fallback across all resolved safe addresses
                conn_err = None
                for cand in safe_targets:
                    try:
                        remote_sock = socket.create_connection(cand, timeout=AppConstants.SOCKET_CONNECT_TIMEOUT)
                        break
                    except Exception as ce:
                        conn_err = ce
                        continue
                if not remote_sock:
                    client_sock.sendall(f"HTTP/1.1 502 Bad Gateway\r\nConnection: close\r\n\r\nUpstream connect failed: {conn_err}\r\n".encode("utf-8"))
                    client_sock.close()
                    return
                remote_sock.sendall(sanitized_request)
                with self.stats_lock:
                    self.bytes_sent += len(sanitized_request)

            self._register_socket(client_sock)
            if remote_sock:
                self._register_socket(remote_sock)
            self._pipe_sockets(client_sock, remote_sock)
        except (socket.error, OSError, TimeoutError, UnicodeError):
            pass
        finally:
            for s in (client_sock, remote_sock):
                if s:
                    self._unregister_socket(s)
                    try:
                        s.close()
                    except (socket.error, OSError):
                        pass

    def _pipe_sockets(self, s1: socket.socket, s2: socket.socket) -> None:
        s1.settimeout(30)
        s2.settimeout(30)
        active_sockets = [s1, s2]
        idle_ticks = 0
        try:
            while self.running and active_sockets:
                r, _, _ = select.select(active_sockets, [], [], AppConstants.SELECT_POLL_TIMEOUT)
                if not r:
                    idle_ticks += 1
                    if idle_ticks >= 30:  # 30 × 10s = 5 minutes idle → close pipe
                        return
                    continue
                idle_ticks = 0
                for sock in r:
                    other = s2 if sock is s1 else s1
                    try:
                        data = sock.recv(16384)
                        if not data:
                            # Half-close: socket closed by peer, send SHUT_WR to other and stop reading from this socket
                            if sock in active_sockets:
                                active_sockets.remove(sock)
                            try:
                                other.shutdown(socket.SHUT_WR)
                            except (socket.error, OSError):
                                return
                            if not active_sockets:
                                return
                            continue
                        other.sendall(data)
                        with self.stats_lock:
                            if sock is s1:
                                self.bytes_sent += len(data)
                            else:
                                self.bytes_recv += len(data)
                    except (socket.error, OSError):
                        return
        except (socket.error, OSError):
            pass


# ==========================================
# AUTHENTICATION & FORTIGATE ENGINE
# ==========================================
class GitWifiCore:
    def __init__(self, status_cb=None, log_cb=None, profile_switch_cb=None):
        self.config = load_settings()
        self.status_cb = status_cb
        self.log_cb = log_cb
        self.profile_switch_cb = profile_switch_cb
        self.session = requests.Session()
        self.status = "Disconnected"
        self.running = False
        self.worker_thread = None
        self.keepalive_url = None
        self.current_magic = None
        self.portal_host = self.config.get("portal_host") or "-"
        self.gateway_ip = self.config.get("last_gateway") or "-"
        self.portal_port = self.config.get("portal_port") or AppConstants.DEFAULT_PORTAL_PORT
        self.portal_scheme = self.config.get("portal_scheme") or "http"
        self.portal_type: str = "auto"
        self.local_ip = "-"
        self.session_start = None
        self.user_signed_out = False
        self.last_connected_ssid: Optional[str] = None
        self.last_connected_profile: Optional[str] = None
        self.session_lock: threading.Lock = threading.Lock()
        self.failed_login_attempts: int = 0
        self.max_login_retries: int = 5
        self.error_backoff_seconds: float = 30.0

        self.state_lock = threading.Lock()
        self.cycle_event = threading.Event()

        # Adaptive Keepalive Tuning state
        self.current_keepalive_interval: int = max(10, int(self.config.get("keepalive_interval", 120)))
        self.keepalive_consecutive_successes: int = 0
        self.keepalive_consecutive_failures: int = 0

        self.proxy_server = HotspotProxyServer(port=self.config.get("proxy_port", 8888), logger=self.log)
        self.proxy_server.sniff_headers = self.config.get("proxy_sniff_headers", False)

    def update_config(self, key: str, value: Any, save: bool = True) -> None:
        """Thread-safe update of core configuration dictionary with optional disk persistence (Bug 13)."""
        with _config_lock:
            self.config[key] = value
            if save:
                save_settings(self.config)

    def get_verify_tls(self, url: Optional[str] = None) -> Union[bool, str]:
        """
        Return CA bundle path or TLS verification boolean (Bug 5).
        Captive portals typically use self-signed certificates or private CAs;
        if custom_ca_bundle is configured in settings and exists on disk, it is used.
        """
        ca_bundle = self.config.get("custom_ca_bundle")
        if ca_bundle and os.path.isfile(ca_bundle):
            return ca_bundle
        return self.config.get("verify_tls", False)

    def log(self, text):
        ts = time.strftime("[%H:%M:%S] ")
        line = ts + text
        print(line)
        if self.log_cb:
            self.log_cb(line)

    def set_status(self, new_status):
        with self.state_lock:
            if self.status == new_status:
                return
            self.status = new_status
        if self.status_cb:
            self.status_cb(new_status)

    def alert(self, kind: str) -> None:
        if not HAS_WINSOUND or not self.config.get("sound_alerts", True):
            return
        try:
            if kind == "ok":
                winsound.MessageBeep(winsound.MB_OK)
            elif kind == "fail":
                winsound.MessageBeep(winsound.MB_ICONHAND)
        except Exception:
            pass

    def get_user_agent(self):
        mode = self.config.get("user_agent_mode", "Windows Chrome")
        if mode == "Custom":
            return self.config.get("custom_user_agent") or SPOOF_USER_AGENTS["Windows Chrome"]
        return SPOOF_USER_AGENTS.get(mode, SPOOF_USER_AGENTS["Windows Chrome"])

    def resolve_profile_for_network(self, current_gateway: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Feature 2: Auto-Profile Switching based on Default Gateway / Subnet match.
        If auto_profile_switching is enabled, matches the discovered gateway against
        each profile's 'gateway_match' rule. Automatically updates active_profile_index.
        """
        profiles = self.config.get("profiles", [])
        if not profiles:
            return None

        if self.config.get("auto_profile_switching", True) and current_gateway and current_gateway != "-":
            # Bug 19 fix: Sort rules by specificity (exact IP first, CIDR subnets next, then longest prefix match)
            candidates = []
            for i, p in enumerate(profiles):
                match_val = str(p.get("gateway_match", "")).strip()
                if not match_val:
                    continue
                score = 0
                is_matched = False
                if match_val == current_gateway:
                    is_matched = True
                    score = 1000
                elif "/" in match_val:
                    try:
                        net = ipaddress.ip_network(match_val, strict=False)
                        if ipaddress.ip_address(current_gateway) in net:
                            is_matched = True
                            score = 500 + net.prefixlen
                    except Exception:
                        pass
                elif current_gateway.startswith(match_val):
                    # Ensure prefix ends with a dot or matches boundary to avoid 10.17 matching 10.170.x.x
                    if match_val.endswith(".") or current_gateway.startswith(match_val + "."):
                        is_matched = True
                        score = 100 + len(match_val)
                
                if is_matched:
                    candidates.append((score, i, p, match_val))

            if candidates:
                candidates.sort(key=lambda x: x[0], reverse=True)
                _, best_idx, best_prof, matched_rule = candidates[0]
                curr_idx = self.config.get("active_profile_index", 0)
                if best_idx != curr_idx:
                    self.log(f"[Auto-Profile] Gateway '{current_gateway}' matched rule '{matched_rule}' (specificity score {candidates[0][0]}). Auto-switching to profile '{best_prof.get('name')}' (#{best_idx + 1})")
                    self.update_config("active_profile_index", best_idx, save=True)
                    if hasattr(self, "profile_switch_cb") and callable(self.profile_switch_cb):
                        try:
                            self.profile_switch_cb(best_idx)
                        except Exception:
                            pass
                return best_prof

        # Fallback to current active profile index
        return self.get_active_profile()

    def get_active_profile(self):
        with _config_lock:
            profiles = self.config.get("profiles", [])
            idx = self.config.get("active_profile_index", 0)
            if profiles and 0 <= idx < len(profiles):
                return profiles[idx]
            if profiles and idx >= len(profiles):
                self.log(f"[Config] active_profile_index ({idx}) is out of range (have {len(profiles)} profiles). Falling back to first profile.")
                self.config["active_profile_index"] = 0
                try:
                    save_settings(self.config)
                except Exception as e:
                    self.log(f"[Config] Failed to persist active_profile_index reset: {e}")
                return profiles[0]
            return None

    def start(self):
        if not self.running:
            self.running = True
            self.cycle_event.clear()
            if self.config.get("proxy_enabled", False):
                try:
                    self.proxy_server.start()
                except Exception as pe:
                    self.log(f"Proxy failed to start during initialization: {pe}")
            if self.worker_thread and self.worker_thread.is_alive():
                return
            self.worker_thread = threading.Thread(target=self._cycle, daemon=True)
            self.worker_thread.start()

    def stop(self):
        self.running = False
        self.cycle_event.set()
        self.proxy_server.stop()
        self.set_status("Disconnected")

    def interrupt_cycle(self):
        self.cycle_event.set()

    def _cycle(self):
        while self.running:
            self.cycle_event.clear()
            try:
                if self.user_signed_out:
                    self.cycle_event.wait(3.0)
                    continue

                # Auto-detect gateway first so profile auto-switching can match network
                curr_gw = get_default_gateway() or self.gateway_ip
                profile = self.resolve_profile_for_network(curr_gw)
                if not profile or not profile.get("username"):
                    self.set_status("No Profile Configured")
                    self.cycle_event.wait(5.0)
                    continue

                # Lockout prevention: Check if max retries exceeded on rejected credentials
                if self.failed_login_attempts >= self.max_login_retries:
                    self.set_status("Login Paused (Retries Exceeded)")
                    self.log(f"Login paused after {self.failed_login_attempts} failed attempts to prevent account lockout. Click 'Force Re-Probe' or switch profile to retry.")
                    self.cycle_event.wait(300)
                    continue

                self.session.headers.update({"User-Agent": self.get_user_agent()})
                connected = self._run_shotgun_authentication(profile, gw=curr_gw)

                if connected:
                    self.failed_login_attempts = 0
                    self.error_backoff_seconds = 30.0
                elif self.status == "Login Rejected":
                    self.failed_login_attempts += 1
                    self.log(f"Consecutive failed login attempts: {self.failed_login_attempts}/{self.max_login_retries}")
                    # Check auto_reconnect before sleeping to avoid unnecessary 120s delay
                    if not self.config.get("auto_reconnect", True):
                        self.log("Auto-reconnect is disabled. Waiting for manual Re-Probe.")
                        self.cycle_event.wait()
                        continue
                    self.cycle_event.wait(120)
                elif self.status in ("Error", "Untrusted Portal"):
                    # Bug 14: Exponential backoff on Error or Untrusted Portal (30s -> 60s -> 120s -> max 300s)
                    self.log(f"Encountered status '{self.status}'. Backing off probe for {int(self.error_backoff_seconds)}s.")
                    # Check auto_reconnect before sleeping
                    if not self.config.get("auto_reconnect", True):
                        self.log("Auto-reconnect is disabled. Waiting for manual Re-Probe.")
                        self.cycle_event.wait()
                        continue
                    self.cycle_event.wait(self.error_backoff_seconds)
                    self.error_backoff_seconds = min(300.0, self.error_backoff_seconds * 2.0)
                    continue

                # Honor auto_reconnect setting: If disconnected and auto_reconnect is disabled, pause until manual user action (Bug 8)
                if not connected and not self.config.get("auto_reconnect", True):
                    self.log("Auto-reconnect is disabled in config. Waiting indefinitely for manual Re-Probe.")
                    self.cycle_event.wait()
                    continue

                with self.state_lock:
                    has_keepalive = bool(connected and self.keepalive_url)

                # Validate keepalive_interval to prevent hammering or crashes on invalid/zero values
                raw_interval = self.config.get("keepalive_interval", 120)
                try:
                    interval_val = max(10, int(raw_interval))
                except (ValueError, TypeError):
                    interval_val = 120

                # Feature 4: Use adaptive keepalive interval if enabled
                if self.config.get("adaptive_keepalive", True):
                    interval_val = max(10, self.current_keepalive_interval)

                if has_keepalive:
                    wait_sec = interval_val
                    while self.running and wait_sec > 0:
                        with self.state_lock:
                            if not self.keepalive_url or self.user_signed_out:
                                break
                        if self.cycle_event.wait(min(5.0, wait_sec)):
                            self.cycle_event.clear()
                            break
                        wait_sec -= 5

                    with self.state_lock:
                        should_ping = bool(self.running and self.keepalive_url and not self.user_signed_out)
                    if should_ping:
                        self._ping_keepalive()

                elif connected and not self.user_signed_out:
                    wait_sec = interval_val
                    while self.running and wait_sec > 0:
                        if self.user_signed_out:
                            break
                        if self.cycle_event.wait(min(5.0, wait_sec)):
                            self.cycle_event.clear()
                            break
                        wait_sec -= 5

                self.cycle_event.wait(6.0)

            except Exception as e:
                self.log(f"Cycle error: {e}")
                self.cycle_event.wait(10)

    def _run_shotgun_authentication(self, profile: Optional[Dict[str, Any]], gw: Optional[str] = None) -> bool:
        if not profile:
            return False
        try:
            was_connected = (self.status == "Connected")
            if not was_connected:
                self.set_status("Shotgun Probing...")

            # Adapt to network transitions (Bug 15, Bug 55)
            active_gw = gw or get_default_gateway()
            if active_gw and active_gw != "-":
                if self.gateway_ip != "-" and self.gateway_ip != active_gw:
                    self.log(f"[Network] Gateway transitioned from {self.gateway_ip} to {active_gw}. Resetting portal parameters.")
                    self.portal_host = active_gw
                    self.portal_port = AppConstants.DEFAULT_PORTAL_PORT
                    self.portal_scheme = "http"
                    with self.state_lock:
                        self.keepalive_url = None
                        self.current_magic = None
                self.gateway_ip = active_gw

            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                try:
                    s.connect(("8.8.8.8", 80))
                    self.local_ip = s.getsockname()[0]
                finally:
                    s.close()
                self.proxy_server.update_bind_host(self.local_ip)
            except (socket.error, OSError):
                try:
                    self.local_ip = socket.gethostbyname(socket.gethostname())
                except (socket.error, OSError):
                    self.local_ip = "127.0.0.1"
                self.proxy_server.update_bind_host(self.local_ip)

            probe_url = AppConstants.PROBE_URL
            try:
                resp = self.session.get(probe_url, allow_redirects=True, timeout=AppConstants.PROBE_HTTP_TIMEOUT, verify=False)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as initial_err:
                # If DNS failed or connection timed out, the client is likely behind a captive portal gating DNS.
                # Try candidate fallback probes in prioritized order:
                fallback_candidates = []
                trusted_hosts = self.config.get("trusted_portal_hosts", [])
                is_campus = (
                    self.gateway_ip == "172.7.0.1" or
                    "172.15.1.2" in trusted_hosts or
                    self.portal_host == "172.15.1.2" or
                    self.config.get("last_gateway") == "172.7.0.1"
                )
                if is_campus:
                    fallback_candidates.append("http://172.15.1.2:8000/index.html")

                # Outbound Internet IP (triggers captive portal redirect when gateway intercepts port 80)
                fallback_candidates.append("http://1.1.1.1:80/")

                # Gateway IP (captures direct gateway portals e.g. FortiGate)
                if self.gateway_ip and self.gateway_ip != "-":
                    fallback_candidates.append(f"http://{self.gateway_ip}:80/")

                # Previously saved portal host if different
                if self.portal_host and self.portal_host not in ("-", "172.15.1.2", self.gateway_ip):
                    p_scheme = self.portal_scheme or "http"
                    p_port = self.portal_port or 80
                    fallback_candidates.append(f"{p_scheme}://{self.portal_host}:{p_port}/")

                fallback_resp = None
                for target in fallback_candidates:
                    try:
                        f_resp = self.session.get(target, allow_redirects=True, timeout=3.5, verify=False)
                        norm_f_url = (f_resp.url or "").rstrip("/") + "/"
                        norm_target = target.rstrip("/") + "/"

                        if f_resp.status_code == 204:
                            fallback_resp = f_resp
                            break

                        if f_resp.url and norm_f_url != norm_target:
                            fallback_resp = f_resp
                            break

                        if f_resp.status_code == 200 and any(kw in f_resp.text for kw in ("/api/captiveportal", "inputUsername", "inputPassword")):
                            fallback_resp = f_resp
                            break

                        if "index-view-container" in f_resp.text or "web switch" in str(f_resp.headers).lower():
                            try:
                                opn_resp = self.session.get("http://172.15.1.2:8000/index.html", timeout=3.0, verify=False)
                                if opn_resp.status_code == 200 and ("/api/captiveportal" in opn_resp.text or "inputUsername" in opn_resp.text):
                                    fallback_resp = opn_resp
                                    break
                            except Exception:
                                pass
                            fallback_resp = f_resp
                            break

                        if f_resp.status_code == 200 and any(kw in f_resp.text.lower() for kw in ("login", "captiveportal", "magic", "password", "fgtauth")):
                            fallback_resp = f_resp
                            break
                    except Exception:
                        continue

                if fallback_resp is not None:
                    resp = fallback_resp
                else:
                    raise initial_err
            
            if resp.status_code == 204:
                # Bug 9: Online and unrestricted — restore session_start whenever it's None regardless of was_connected
                if not self.session_start:
                    self.session_start = time.time()

                # Online and unrestricted: If we had a cached session for this gateway/portal, restore keepalive
                if not self.keepalive_url:
                    saved_gw = self.config.get("last_gateway")
                    p_host = self.portal_host if (self.portal_host and self.portal_host != "-") else self.gateway_ip
                    if p_host and p_host != "-":
                        if self.portal_type == "opnsense" or self.portal_port == 8000:
                            self.keepalive_url = f"{self.portal_scheme}://{p_host}:{self.portal_port}/api/captiveportal/access/status/"
                        elif self.config.get("last_magic") and saved_gw and (saved_gw == self.gateway_ip):
                            self.current_magic = self.config.get("last_magic")
                            self.keepalive_url = f"{self.portal_scheme}://{p_host}:{self.portal_port}/keepalive?{self.current_magic}"
                            self.log(f"Restored active FortiGate session token from cache for gateway {self.gateway_ip}")

                if not was_connected:
                    self.set_status("Connected")
                    self.log("Shotgun Probe passed: Online and unrestricted.")
                    self.alert("ok")
                return True

            portal_url = resp.url
            self.log(f"Portal redirect captured: {portal_url}")

            parsed_portal = urlparse(portal_url)
            redirect_host = parsed_portal.hostname or ""
            redirect_scheme = parsed_portal.scheme or "http"
            if parsed_portal.port:
                redirect_port = parsed_portal.port
            elif redirect_scheme == "https":
                redirect_port = 443
            else:
                redirect_port = 80

            # Bug 18 fix: Handle in-place captive portals answering probe URL with 200 login page
            probe_hostname = urlparse(probe_url).hostname
            if redirect_host.lower() == (probe_hostname or "").lower():
                # Check if it returned a captive portal login page on the probe URL
                is_inplace_portal = any(kw in resp.text.lower() for kw in ("login", "captiveportal", "magic", "inputusername", "password", "fgtauth"))
                if is_inplace_portal and self.gateway_ip and self.gateway_ip != "-":
                    self.log("Detected in-place captive portal serving login directly on probe URL. Redirecting target to gateway.")
                    redirect_host = self.gateway_ip
                    redirect_port = self.portal_port if (self.portal_port and self.portal_port not in (80, 443)) else 80
                    portal_url = f"{redirect_scheme}://{redirect_host}:{redirect_port}/"
                else:
                    self.log(f"Probe returned non-204 ({resp.status_code}) without redirect. Preserving gateway {self.gateway_ip}.")
                    self.set_status("Disconnected")
                    return False

            # Bug 3: Validate redirect host against config allow-list, campus network, and gateway
            trusted_hosts = self.config.get("trusted_portal_hosts", [])
            campus_hosts = {"172.15.1.2", "172.15.1.1"}
            is_valid_portal_target = (
                (redirect_host and redirect_host == self.gateway_ip) or
                (redirect_host and redirect_host in campus_hosts) or
                (redirect_host and redirect_host in trusted_hosts) or
                (redirect_host and any(str(h) == redirect_host for h in trusted_hosts))
            )
            if not is_valid_portal_target:
                self.log(f"[Security] Captive portal redirected to unlisted host '{redirect_host}' (gateway: {self.gateway_ip}). Refusing to send credentials. Add host to Settings -> Trusted Hosts if legitimate.")
                self.set_status("Untrusted Portal")
                return False

            # If redirected to an access point/switch landing page (e.g., 172.7.0.1:80 Web Switch) without login inputs,
            # query the known college captive portal (172.15.1.2:8000) directly to fetch the actual login state.
            # Bug 16 fix: Only trigger if current gateway is 172.7.0.1 or 172.15.1.2 is explicitly trusted
            trusted_portal_hosts = self.config.get("trusted_portal_hosts", [])
            is_campus_network = (
                self.gateway_ip == "172.7.0.1" or
                "172.15.1.2" in trusted_portal_hosts or
                any("172.15.1.2" in str(h) for h in trusted_portal_hosts) or
                redirect_host == "172.15.1.2"
            )
            if is_campus_network and ("Server': 'Web Switch'" in str(resp.headers) or "index-view-container" in resp.text or 
                (redirect_host == self.gateway_ip and redirect_port == 80 and "/api/captiveportal" not in resp.text and "magic" not in resp.text)):
                self.log(f"Gateway {redirect_host}:80 is an AP switch page. Checking dedicated captive portal (172.15.1.2:8000)...")
                try:
                    opn_test = self.session.get("http://172.15.1.2:8000/index.html", timeout=3.5, verify=False)
                    if opn_test.status_code == 200 and ("/api/captiveportal" in opn_test.text or "inputUsername" in opn_test.text or ":8000" in opn_test.url):
                        resp = opn_test
                        portal_url = "http://172.15.1.2:8000/index.html"
                        redirect_host = "172.15.1.2"
                        redirect_port = 8000
                        redirect_scheme = "http"
                        self.log("Redirected discovery to OPNsense portal at 172.15.1.2:8000")
                except Exception as opn_err:
                    self.log(f"Direct probe to 172.15.1.2:8000: {opn_err}")

            # Store redirect host into self.portal_host
            self.portal_host = redirect_host
            self.portal_port = redirect_port
            self.portal_scheme = redirect_scheme

            # Check if user clicked sign out while probe/discovery was in-flight
            with self.state_lock:
                if self.user_signed_out:
                    self.log("Authentication cancelled: User initiated sign out.")
                    return False

            # Validate password is ready and not corrupted
            pwd = profile.get("password", "")
            if not pwd:
                self.log("Cannot authenticate: Profile password is empty or decryption failed.")
                self.set_status("Error")
                return False

            # Detect Portal Engine: OPNsense/pfSense vs FortiGate
            is_opnsense = ("/api/captiveportal/" in resp.text or 
                           "/api/captiveportal/" in portal_url or 
                           "inputUsername" in resp.text or 
                           redirect_host == "172.15.1.2" or
                           ":8000" in portal_url)

            keepalive_url = None

            if is_opnsense:
                self.portal_type = "opnsense"
                # Bug 17 fix: Reset current_magic on OPNsense branch to avoid persisting stale FortiGate tokens
                self.current_magic = None
                self.log(f"Detected OPNsense Captive Portal on {self.portal_host}:{self.portal_port}")
                self.set_status("Logging In...")

                api_logon_url = f"{self.portal_scheme}://{self.portal_host}:{self.portal_port}/api/captiveportal/access/logon/"
                self.log(f"Authenticating via OPNsense API as [{profile.get('name', 'User')}] ({profile['username']})...")
                
                auth_payload = {
                    "user": profile["username"],
                    "password": pwd
                }
                headers = {"X-Requested-With": "XMLHttpRequest"}
                auth_resp = self.session.post(api_logon_url, data=auth_payload, headers=headers,
                                               timeout=AppConstants.AUTH_POST_TIMEOUT, verify=False)
                
                # Check sign-out race condition
                with self.state_lock:
                    if self.user_signed_out:
                        self.log("Session cancelled post-auth: User signed out during handshake.")
                        return False

                auth_success = False
                api_explicit_rejection = False
                try:
                    data = auth_resp.json()
                    if data.get("clientState") == "AUTHORIZED":
                        auth_success = True
                    elif data.get("clientState") in ("NOT_AUTHORIZED", "REJECTED", "ERROR") or "user" in data:
                        api_explicit_rejection = True
                        self.log(f"OPNsense logon API rejected credentials: {data}")
                    else:
                        self.log(f"OPNsense logon response: {data}")
                except Exception:
                    if auth_resp.status_code == 200 and "AUTHORIZED" in auth_resp.text:
                        auth_success = True

                if api_explicit_rejection:
                    self.set_status("Login Rejected")
                    self.log("OPNsense credentials rejected. Verify username/password.")
                    self.alert("fail")
                    return False

                if not auth_success and auth_resp.status_code != 200:
                    self.log(f"OPNsense logon returned HTTP {auth_resp.status_code}")

                # For OPNsense, keepalive is maintained by monitoring the session status API endpoint
                keepalive_url = f"{self.portal_scheme}://{self.portal_host}:{self.portal_port}/api/captiveportal/access/status/"

            else:
                self.portal_type = "fortigate"
                self.current_magic = None
                if "fgtauth" in portal_url or "magic" in portal_url:
                    m = REGEX_MAGIC_FGT.search(portal_url)
                    if m:
                        self.current_magic = m.group(1)
                if not self.current_magic:
                    m = REGEX_MAGIC_QUERY.search(portal_url)
                    if m:
                        self.current_magic = m.group(1)
                if not self.current_magic:
                    m = REGEX_MAGIC_INPUT1.search(resp.text)
                    if not m:
                        m = REGEX_MAGIC_INPUT2.search(resp.text)
                    if m:
                        self.current_magic = m.group(1)

                if not self.current_magic:
                    self.set_status("Redirected (No Magic)")
                    self.log("Captive portal intercepted but magic token was not extracted. Retrying...")
                    return False

                self.log(f"Extracted FortiGate magic token: {self.current_magic}")
                self.set_status("Logging In...")

                post_url = portal_url.split("?")[0]
                payload = {
                    "4Tredir": probe_url,
                    "magic":   self.current_magic,
                    "username": profile["username"],
                    "password": pwd,
                }
                self.log(f"Authenticating as [{profile.get('name', 'User')}] ({profile['username']})...")
                auth_resp = self.session.post(post_url, data=payload, allow_redirects=False, timeout=AppConstants.AUTH_POST_TIMEOUT, verify=False)

                # Re-check sign-out race condition immediately after POST
                with self.state_lock:
                    if self.user_signed_out:
                        self.log("Session cancelled post-auth: User signed out during handshake.")
                        return False

                if auth_resp.status_code in (301, 302, 303, 307, 308) and "Location" in auth_resp.headers:
                    loc = auth_resp.headers["Location"]
                    if "generate_204" not in loc and "connectivitycheck" not in loc:
                        portal_base = f"{self.portal_scheme}://{self.portal_host}:{self.portal_port}"
                        if loc.startswith("/"):
                            keepalive_url = portal_base + loc
                        elif loc.startswith("http"):
                            keepalive_url = loc
                        else:
                            keepalive_url = portal_base + "/" + loc
                        self.log(f"Keepalive URL from Location header: {keepalive_url}")

                if not keepalive_url:
                    km = REGEX_KEEPALIVE_URL.search(auth_resp.text)
                    if not km:
                        km = REGEX_FGTAUTH_URL.search(auth_resp.text)
                    if km:
                        base = post_url.rsplit('/', 1)[0]
                        keepalive_url = f"{base}/keepalive?{km.group(1)}"
                        self.log(f"Keepalive URL from HTML body: {keepalive_url}")

            # Re-probe to confirm internet access with retry/grace period for firewall rules to take effect
            auth_ok = False
            verify_inconclusive = False
            # Campus networks (OPNsense/pfSense) can take up to 8-10 seconds to update pf tables and unblock DNS.
            max_verif_retries = 6 if is_opnsense else 3
            verif_delay = 1.5 if is_opnsense else 0.5
            for retry_idx in range(max_verif_retries):
                try:
                    time.sleep(verif_delay)  # Allow firewall NAT/pf table rules to populate
                    verify_resp = self.session.get(probe_url, allow_redirects=True,
                                                   timeout=AppConstants.PROBE_HTTP_TIMEOUT, verify=False)
                    # Positive verification: HTTP 204 from standard probe endpoint
                    if verify_resp.status_code == 204:
                        auth_ok = True
                        break
                    elif verify_resp.status_code == 200:
                        v_url = verify_resp.url or ""
                        # Bug 1 fix: Do not accept re-displayed login pages as success
                        is_portal_redirect = (
                            ":8000" in v_url or "captiveportal" in v_url or "fgtauth" in v_url or
                            "magic" in v_url or "inputUsername" in verify_resp.text or
                            "login" in v_url.lower() or "authentication" in verify_resp.text.lower()
                        )
                        if not is_portal_redirect and len(verify_resp.content) > 0:
                            auth_ok = True
                            break
                    
                    self.log(f"Post-auth verification attempt {retry_idx + 1}/{max_verif_retries} returned HTTP {verify_resp.status_code} ({verify_resp.url}). Retrying...")
                except Exception as verify_err:
                    verify_inconclusive = True
                    self.log(f"Post-auth verification attempt {retry_idx + 1}/{max_verif_retries} waiting for firewall/DNS ({verify_err})...")

            # If HTTP probe was inconclusive, check OPNsense status API directly
            if not auth_ok and is_opnsense:
                try:
                    status_url = f"{self.portal_scheme}://{self.portal_host}:{self.portal_port}/api/captiveportal/access/status/"
                    st_resp = self.session.post(status_url, data={"user": "", "password": ""},
                                                headers={"X-Requested-With": "XMLHttpRequest"},
                                                timeout=6.0, verify=False)
                    if st_resp.status_code == 200 and st_resp.json().get("clientState") == "AUTHORIZED":
                        self.log("OPNsense status API confirmed: clientState is AUTHORIZED (firewall rules active).")
                        auth_ok = True
                    elif auth_success and not api_explicit_rejection:
                        self.log("OPNsense logon API was AUTHORIZED. Treating session as active.")
                        auth_ok = True
                except Exception as st_err:
                    self.log(f"OPNsense status API fallback check error: {st_err}")
                    if auth_success and not api_explicit_rejection:
                        auth_ok = True

            # Final sign-out race check before recording Connected status
            with self.state_lock:
                if self.user_signed_out:
                    self.log("Session discarded: User signed out.")
                    return False

            if auth_ok:
                with self.state_lock:
                    self.keepalive_url = keepalive_url
                    self.session_start = time.time()
                
                # Persist active token, gateway, and portal parameters (Bug 11, Bug 13, N1)
                if self.current_magic:
                    self.update_config("last_magic", self.current_magic, save=False)
                self.update_config("last_gateway", self.gateway_ip, save=False)
                self.update_config("portal_host", self.portal_host, save=False)
                self.update_config("portal_port", self.portal_port, save=False)
                self.update_config("portal_scheme", self.portal_scheme, save=True)

                self.set_status("Connected")
                if keepalive_url:
                    self.log(f"Connection authorized by firewall for {profile['username']}! (Keepalive registered)")
                else:
                    self.log(f"Connection authorized by firewall for {profile['username']}! (Direct probe verified)")
                self.alert("ok")

                # Feature 5: Automated DNS-over-HTTPS (DoH) Telemetry & Check
                if self.config.get("doh_fallback_enabled", False):
                    threading.Thread(target=self._verify_doh_resolution, daemon=True).start()

                return True
            else:
                with self.state_lock:
                    self.session_start = None
                if verify_inconclusive and not auth_ok:
                    self.set_status("Probe Timeout")
                    self.log("[Auth] Network verification probe timed out after login. Retrying next cycle...")
                    return False
                else:
                    self.set_status("Login Rejected")
                    self.log("Credentials rejected or access not permitted by portal. Verify username/password.")
                    self.alert("fail")
                    return False

        except RequestException as e:
            with self.state_lock:
                self.session_start = None
            self.set_status("Disconnected")
            err_str = str(e)
            if "NameResolutionError" in err_str or "getaddrinfo failed" in err_str:
                self.log("[Probe] Network offline or DNS resolving paused (waiting for Wi-Fi connection)...")
            elif "Connection refused" in err_str:
                self.log(f"[Probe] Connection refused by portal/gateway ({self.gateway_ip}).")
            elif "ConnectTimeout" in err_str or "timed out" in err_str:
                self.log(f"[Probe] Probe request timed out (gateway {self.gateway_ip} unreachable).")
            else:
                self.log(f"Portal network error: {e}")
            return False
        except (KeyError, ValueError) as e:
            with self.state_lock:
                self.session_start = None
            self.set_status("Error")
            self.log(f"Data format error: {e}")
            return False

    def _ping_keepalive(self) -> None:
        with self.state_lock:
            url = self.keepalive_url
        if not url:
            return
        t0 = time.time()
        try:
            self.log("Dispatching keepalive ping...")
            verify_opt = self.get_verify_tls(url)
            with self.session_lock:
                if "/api/captiveportal/" in url:
                    # OPNsense status check ping
                    headers = {"X-Requested-With": "XMLHttpRequest"}
                    r = self.session.post(url, data={"user": "", "password": ""}, headers=headers,
                                          timeout=AppConstants.KEEPALIVE_HTTP_TIMEOUT, verify=verify_opt)
                else:
                    # For FortiGate: ping keepalive endpoint without following redirects (an expired session 302-redirects to login)
                    r = self.session.get(url, timeout=AppConstants.KEEPALIVE_HTTP_TIMEOUT, allow_redirects=False, verify=verify_opt)
            rtt_ms = int((time.time() - t0) * 1000)
            if "/api/captiveportal/" in url:
                is_authorized = False
                try:
                    is_authorized = (r.json().get("clientState") == "AUTHORIZED")
                except Exception:
                    is_authorized = (r.status_code == 200)

                if is_authorized:
                    self.keepalive_consecutive_successes += 1
                    self.keepalive_consecutive_failures = 0
                    self.log(f"OPNsense session verified active ({rtt_ms}ms).")
                    return
                else:
                    self.keepalive_consecutive_failures += 1
                    self.log(f"OPNsense keepalive check returned unauthorized (HTTP {r.status_code}, attempt {self.keepalive_consecutive_failures}/3).")
                    if self.keepalive_consecutive_failures >= 3:
                        self.log("OPNsense session lost after 3 failed checks. Resetting session.")
                        with self.state_lock:
                            self.keepalive_url = None
                            self.session_start = None
                        with _config_lock:
                            self.config["last_magic"] = ""
                            save_settings(self.config)
                    return
            if r.status_code == 200 and ("keepalive" in r.text.lower() or "ok" in r.text.lower() or len(r.text) < 500):
                self.keepalive_consecutive_successes += 1
                self.keepalive_consecutive_failures = 0
                try:
                    base_cfg_interval = max(10, int(self.config.get("keepalive_interval", 120)))
                except (ValueError, TypeError):
                    base_cfg_interval = 120

                # Feature 4: Adaptive keepalive interval tuning
                if self.config.get("adaptive_keepalive", True):
                    # If high latency (>1500ms), step down interval to keep firewall session warm
                    if rtt_ms > 1500:
                        self.current_keepalive_interval = max(30, int(self.current_keepalive_interval * 0.75))
                        self.log(f"Keepalive acknowledged ({rtt_ms}ms, high latency). Scaled interval down to {self.current_keepalive_interval}s.")
                    elif self.keepalive_consecutive_successes >= 3 and self.current_keepalive_interval < base_cfg_interval:
                        self.current_keepalive_interval = min(base_cfg_interval, self.current_keepalive_interval + 15)
                        self.log(f"Keepalive acknowledged ({rtt_ms}ms, stable). Scaled interval up to {self.current_keepalive_interval}s.")
                    else:
                        self.log(f"Keepalive acknowledged ({rtt_ms}ms). Next ping in {self.current_keepalive_interval}s.")
                else:
                    self.log(f"Keepalive acknowledged ({rtt_ms}ms).")
            else:
                self.keepalive_consecutive_failures += 1
                self.log(f"Keepalive responded with HTTP {r.status_code} (attempt {self.keepalive_consecutive_failures}/3).")
                if self.keepalive_consecutive_failures >= 3:
                    self.log("Keepalive failed 3 consecutive times. Resetting session.")
                    with self.state_lock:
                        self.keepalive_url = None
                        self.session_start = None
                    with _config_lock:
                        self.config["last_magic"] = ""
                        save_settings(self.config)
        except RequestException as e:
            self.keepalive_consecutive_failures += 1
            self.log(f"Keepalive ping transient failure ({e}) [attempt {self.keepalive_consecutive_failures}/3]")
            if self.config.get("adaptive_keepalive", True):
                self.current_keepalive_interval = max(20, self.current_keepalive_interval // 2)
                self.keepalive_consecutive_successes = 0
            if self.keepalive_consecutive_failures >= 3:
                self.log("Keepalive failed after 3 consecutive attempts. Clearing keepalive token.")
                with self.state_lock:
                    self.keepalive_url = None
                    self.session_start = None
                with _config_lock:
                    self.config["last_magic"] = ""
                    save_settings(self.config)

    def _verify_doh_resolution(self) -> None:
        """
        Feature 5: Automated DNS-over-HTTPS fallback probe.
        Verifies whether local UDP 53 resolution is poisoned/blocked by the portal,
        and tests Cloudflare 1.1.1.1 DoH resolution endpoint.
        """
        endpoint = self.config.get("doh_endpoint", "https://1.1.1.1/dns-query")
        self.log(f"[DoH] Testing DNS-over-HTTPS endpoint ({endpoint})...")
        t0 = time.time()
        try:
            r = requests.get(f"{endpoint}?name=google.com", headers={"accept": "application/dns-json"}, timeout=4.0, verify=False)
            ms = int((time.time() - t0) * 1000)
            if r.status_code == 200:
                data = r.json()
                if "Answer" in data or data.get("Status") == 0:
                    self.log(f"[DoH] Cloudflare DoH operational ({ms}ms). Secure external DNS available.")
                else:
                    self.log(f"[DoH] Warning: DoH returned 200 but response lacks valid answer (possible gateway interception).")
            else:
                self.log(f"[DoH] DoH endpoint returned status {r.status_code}.")
        except Exception as e:
            self.log(f"[DoH] DNS-over-HTTPS verification failed: {e}")

    def logout(self, disconnect_wifi: bool = True) -> None:
        with self.state_lock:
            self.user_signed_out = True
            magic = self.current_magic
            target_host = self.portal_host if (self.portal_host and self.portal_host != "-") else self.gateway_ip
            is_opn = (self.portal_type == "opnsense" or self.portal_port == 8000)

        if target_host == "-" or not target_host:
            gw = get_default_gateway()
            if gw:
                target_host = gw
                with self.state_lock:
                    self.gateway_ip = gw

        # 1. Terminate session (OPNsense or FortiGate)
        if target_host and target_host != "-":
            try:
                verify_opt = self.get_verify_tls()
                with self.session_lock:
                    if is_opn:
                        logoff_url = f"{self.portal_scheme}://{target_host}:{self.portal_port}/api/captiveportal/access/logoff/"
                        self.log(f"Terminating OPNsense session: {logoff_url}")
                        headers = {"X-Requested-With": "XMLHttpRequest"}
                        self.session.post(logoff_url, data={"user": "", "password": ""}, headers=headers,
                                          timeout=AppConstants.LOGOUT_HTTP_TIMEOUT, verify=verify_opt)
                    else:
                        if not magic:
                            try:
                                p_resp = self.session.get(f"http://{target_host}:{self.portal_port}/", timeout=3.0, verify=verify_opt)
                                km = REGEX_LOGOUT_URL.search(p_resp.text) or REGEX_KEEPALIVE_URL.search(p_resp.text)
                                if km:
                                    magic = km.group(1)
                            except Exception:
                                pass

                        if magic:
                            logout_url = f"{self.portal_scheme}://{target_host}:{self.portal_port}/logout?{magic}"
                            self.log(f"Terminating FortiGate session: {logout_url}")
                            self.session.get(logout_url, timeout=AppConstants.LOGOUT_HTTP_TIMEOUT, verify=verify_opt)
                        else:
                            logout_url = f"{self.portal_scheme}://{target_host}:{self.portal_port}/logout"
                            self.log(f"Sending brute-force logout request: {logout_url}")
                            self.session.get(logout_url, timeout=AppConstants.LOGOUT_HTTP_TIMEOUT, verify=verify_opt)
            except requests.exceptions.ConnectTimeout:
                self.log(f"Portal target {target_host} unreachable (connection timed out).")
            except requests.exceptions.ConnectionError as ce:
                ce_msg = str(ce).lower()
                if "refused" in ce_msg or "unreachable" in ce_msg or "failed to establish" in ce_msg:
                    self.log(f"Portal unreachable ({target_host}): connection refused or host down.")
                else:
                    self.log("Portal logout request completed.")
            except (RequestException, Timeout) as e:
                self.log(f"Portal logout endpoint ping: {e}")

        # 2. Safely Disconnect OS Wi-Fi Adapter (Bulletproof)
        if disconnect_wifi:
            try:
                out = subprocess.check_output(
                    ["netsh", "wlan", "show", "interfaces"],
                    text=True, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW
                )
                for line in out.splitlines():
                    line_str = line.strip()
                    if ":" in line_str:
                        k, v = [x.strip() for x in line_str.split(":", 1)]
                        k_lower = k.lower()
                        if "profile" in k_lower and v and v != "Unknown":
                            self.last_connected_profile = v
                        elif "ssid" in k_lower and "bssid" not in k_lower and v and v != "Unknown":
                            self.last_connected_ssid = v
            except Exception:
                pass

            try:
                subprocess.run(
                    ["netsh", "wlan", "disconnect"], 
                    capture_output=True, 
                    creationflags=CREATE_NO_WINDOW,
                    check=False
                )
                self.log("OS global Wi-Fi disconnect dispatched.")
            except Exception as e:
                self.log(f"WLAN disconnect error: {e}")

        with self.state_lock:
            self.keepalive_url = None
            self.current_magic = None
            self.session_start = None
            # Bug 23 fix: Do not override user_signed_out if the user clicked Force Re-Probe while logout was running
            if not self.user_signed_out:
                self.user_signed_out = True

        # Purge cached magic tokens from memory and storage on explicit sign-out
        # Note: _config_lock acquired outside state_lock to maintain consistent lock ordering
        with _config_lock:
            self.config["last_magic"] = ""
            save_settings(self.config)

        self.cycle_event.set()
        self.set_status("Logged Out")
        self.log("Session signed out. Auto-reconnect paused — click Force Re-Probe to reconnect.")

# ==========================================
# MODERN CLEAN WINDOWS GUI & TRAY APP
# ==========================================
class GitWifiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GITwifi - Clean Windows Suite")
        self.root.geometry("820x580")
        self.root.minsize(740, 520)

        self._apply_app_icon()
        self.log_queue: queue.Queue = queue.Queue()
        self.status_queue: queue.Queue = queue.Queue()
        # Queue for callables dispatched from pystray thread → Tkinter main thread (Items 16 & 17)
        self.tray_action_queue: queue.Queue = queue.Queue()
        self.editor_mode: str = "new" 
        self.editing_index: Optional[int] = None

        self.core = GitWifiCore(status_cb=self._on_status, log_cb=self._on_log, profile_switch_cb=self._on_auto_profile_switch)
        self.last_notified_state = None

        self._apply_dark_theme()
        self._build_interface()
        self._setup_tray_icon()
        # Item 17: If pystray is available, minimize to tray on close; otherwise offer to quit gracefully
        if HAS_PYSTRAY and getattr(self, "tray", None):
            self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        else:
            self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        self.root.after(300, self.core.start)
        self._tick_timer()
        self._flush_log_queue()

        # Bug 10 fix: If started with --minimized, verify tray icon was actually created before withdrawing
        if "--minimized" in sys.argv:
            if getattr(self, "tray", None):
                self.root.withdraw()
            else:
                self.root.iconify()

    def _apply_app_icon(self) -> None:
        icon_path = os.path.join(get_app_dir(), "app_icon.ico")
        if not os.path.exists(icon_path):
            try:
                _generate_app_icon(icon_path)
            except Exception:
                pass
        try:
            self.root.iconbitmap(icon_path)
        except Exception:
            pass
        try:
            img = Image.open(icon_path)
            tk_img = ImageTk.PhotoImage(img)
            self.root.iconphoto(True, tk_img)
            self._icon_ref = tk_img
        except Exception:
            pass

    def _apply_dark_theme(self):
        self.bg = "#121316"
        self.panel = "#1a1b20"
        self.card = "#22232a"
        self.accent = "#3d70f5"
        self.accent_hover = "#2a5cd9"
        self.fg = "#eaeaea"
        self.dim = "#9da3ae"

        self.root.configure(bg=self.bg)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=self.bg, foreground=self.fg, font=("Segoe UI", 9))
        style.configure("TNotebook", background=self.bg, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.panel, foreground=self.fg, padding=[16, 9], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", self.accent)], foreground=[("selected", "#ffffff")])
        style.configure("Card.TFrame", background=self.card, relief="flat")
        style.configure("Card.TLabel", background=self.card, foreground=self.fg)
        style.configure("Action.TButton", font=("Segoe UI", 9, "bold"), background=self.accent, foreground="#ffffff", padding=[12, 6])
        style.map("Action.TButton", background=[("active", self.accent_hover)])
        style.configure("Danger.TButton", font=("Segoe UI", 9, "bold"), background="#d9383a", foreground="#ffffff", padding=[12, 6])
        style.map("Danger.TButton", background=[("active", "#b8282a")])

    def _build_interface(self):
        header = tk.Frame(self.root, bg=self.panel, height=56)
        header.pack(fill=tk.X, side=tk.TOP)

        lbl = tk.Label(header, text="🌐 GITwifi Native Engine", font=("Segoe UI", 13, "bold"), bg=self.panel, fg="#ffffff")
        lbl.pack(side=tk.LEFT, padx=18, pady=12)

        self.status_pill = tk.Label(header, text="● Disconnected", font=("Segoe UI", 10, "bold"), bg="#2d2e38", fg="#d9383a", padx=12, pady=4)
        self.status_pill.pack(side=tk.RIGHT, padx=18)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

        self.tab_dash = ttk.Frame(self.notebook)
        self.tab_profiles = ttk.Frame(self.notebook)
        self.tab_live = ttk.Frame(self.notebook)
        self.tab_proxy = ttk.Frame(self.notebook)
        self.tab_diag = ttk.Frame(self.notebook)
        self.tab_stealth = ttk.Frame(self.notebook)
        self.tab_settings = ttk.Frame(self.notebook)
        self.tab_logs = ttk.Frame(self.notebook)

        # Live Network Monitor state
        self.live_mon_prev_io = get_system_network_io()
        self.live_mon_prev_time = time.time()
        self.live_mon_ping_val: Optional[int] = None
        self.live_mon_loss_val: int = 0
        self.live_mon_ping_history = []
        self.live_mon_worker_running = True
        self.live_mon_wake_event = threading.Event()

        self.notebook.add(self.tab_dash, text=" Dashboard ")
        self.notebook.add(self.tab_profiles, text=" Profiles ")
        if self.core.config.get("live_monitor_enabled", True):
            self.notebook.add(self.tab_live, text=" Live Monitor ")
        self.notebook.add(self.tab_proxy, text=" Hotspot Sharing ")
        self.notebook.add(self.tab_diag, text=" Network Diagnostics ")
        self.notebook.add(self.tab_stealth, text=" Stealth Fingerprint ")
        self.notebook.add(self.tab_settings, text=" Settings ")
        self.notebook.add(self.tab_logs, text=" Live Feed ")

        self._init_dashboard()
        self._init_profiles()
        self._init_live_monitor()
        self._init_proxy()
        self._init_diagnostics()
        self._init_stealth()
        self._init_settings()
        self._init_logs()

        # Start background ping/loss worker thread
        threading.Thread(target=self._live_monitor_ping_worker, daemon=True).start()

    def _init_dashboard(self):
        frame = self.tab_dash

        card1 = ttk.Frame(frame, style="Card.TFrame", padding=16)
        card1.pack(fill=tk.X, padx=14, pady=10)

        ttk.Label(card1, text="Session Overview", font=("Segoe UI", 12, "bold"), style="Card.TLabel").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        ttk.Label(card1, text="Active Profile:", style="Card.TLabel").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.lbl_profile = ttk.Label(card1, text="None", font=("Segoe UI", 10, "bold"), style="Card.TLabel", foreground=self.accent)
        self.lbl_profile.grid(row=1, column=1, sticky=tk.W, padx=10, pady=3)

        ttk.Label(card1, text="Active Duration:", style="Card.TLabel").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.lbl_timer = ttk.Label(card1, text="00:00:00", style="Card.TLabel")
        self.lbl_timer.grid(row=2, column=1, sticky=tk.W, padx=10, pady=3)

        ttk.Label(card1, text="Local IPv4 Address:", style="Card.TLabel").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.lbl_ip = ttk.Label(card1, text="-", style="Card.TLabel")
        self.lbl_ip.grid(row=3, column=1, sticky=tk.W, padx=10, pady=3)

        ttk.Label(card1, text="Gateway Controller IP:", style="Card.TLabel").grid(row=4, column=0, sticky=tk.W, pady=3)
        self.lbl_gw = ttk.Label(card1, text="-", style="Card.TLabel")
        self.lbl_gw.grid(row=4, column=1, sticky=tk.W, padx=10, pady=3)

        card2 = ttk.Frame(frame, style="Card.TFrame", padding=16)
        card2.pack(fill=tk.X, padx=14, pady=6)

        ttk.Label(card2, text="Quick Commands", font=("Segoe UI", 12, "bold"), style="Card.TLabel").pack(anchor=tk.W, pady=(0, 10))

        bar = tk.Frame(card2, bg=self.card)
        bar.pack(fill=tk.X)
        ttk.Button(bar, text="⚡ Force Re-Probe", style="Action.TButton", command=self._force_probe).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(bar, text="🛑 Disconnect & Sign Out", style="Danger.TButton", command=lambda: threading.Thread(target=self.core.logout, daemon=True).start()).pack(side=tk.LEFT)

    def _init_profiles(self):
        frame = self.tab_profiles
        box = ttk.Frame(frame, padding=12)
        box.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(box, style="Card.TFrame", padding=12)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        ttk.Label(left, text="Saved Profiles", font=("Segoe UI", 11, "bold"), style="Card.TLabel").pack(anchor=tk.W, pady=(0, 6))

        self.profiles_lb = tk.Listbox(left, bg=self.bg, fg="#ffffff", selectbackground=self.accent, font=("Segoe UI", 10), bd=0, highlightthickness=1, highlightbackground="#31343f", exportselection=False)
        self.profiles_lb.pack(fill=tk.BOTH, expand=True, pady=4)
        self.profiles_lb.bind("<<ListboxSelect>>", self._on_profile_picked)

        r_btns = tk.Frame(left, bg=self.card)
        r_btns.pack(fill=tk.X, pady=6)
        ttk.Button(r_btns, text="⭐ Set Active", style="Action.TButton", command=self._set_active_profile).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(r_btns, text="✏️ Edit", style="Action.TButton", command=self._start_edit_profile).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(r_btns, text="🗑 Delete", style="Danger.TButton", command=self._del_profile).pack(side=tk.LEFT)

        right = ttk.Frame(box, style="Card.TFrame", padding=14)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        top_editor_bar = tk.Frame(right, bg=self.card)
        top_editor_bar.pack(fill=tk.X, pady=(0, 10))

        self.lbl_editor_mode = ttk.Label(top_editor_bar, text="Mode: [New Profile]", font=("Segoe UI", 11, "bold"), style="Card.TLabel", foreground=self.accent)
        self.lbl_editor_mode.pack(side=tk.LEFT)

        ttk.Button(top_editor_bar, text="➕ New Profile", style="Action.TButton", command=self._start_new_profile).pack(side=tk.RIGHT)

        ttk.Label(right, text="Profile Name (Label):", style="Card.TLabel").pack(anchor=tk.W, pady=(4, 2))
        self.e_pname = tk.Entry(right, bg=self.bg, fg="#ffffff", insertbackground="#fff", bd=0, font=("Segoe UI", 10))
        self.e_pname.pack(fill=tk.X, ipady=4, pady=(0, 8))

        ttk.Label(right, text="Username (Admission / Roll No):", style="Card.TLabel").pack(anchor=tk.W, pady=(4, 2))
        self.e_puser = tk.Entry(right, bg=self.bg, fg="#ffffff", insertbackground="#fff", bd=0, font=("Segoe UI", 10))
        self.e_puser.pack(fill=tk.X, ipady=4, pady=(0, 8))

        ttk.Label(right, text="Password:", style="Card.TLabel").pack(anchor=tk.W, pady=(4, 2))
        self.e_ppass = tk.Entry(right, show="●", bg=self.bg, fg="#ffffff", insertbackground="#fff", bd=0, font=("Segoe UI", 10))
        self.e_ppass.pack(fill=tk.X, ipady=4, pady=(0, 4))

        self.show_pwd_var = tk.BooleanVar(value=False)
        self.chk_show_pwd = tk.Checkbutton(
            right,
            text="Show Password",
            variable=self.show_pwd_var,
            bg=self.card,
            fg="#ffffff",
            selectcolor="#121316",
            activebackground=self.card,
            activeforeground="#ffffff",
            font=("Segoe UI", 9),
            command=self._toggle_password_visibility
        )
        self.chk_show_pwd.pack(anchor=tk.W, pady=(0, 6))

        ttk.Label(right, text="Auto-Switch Gateway / Subnet Rule (Optional):", style="Card.TLabel").pack(anchor=tk.W, pady=(4, 2))
        self.e_pgateway = tk.Entry(right, bg=self.bg, fg="#ffffff", insertbackground="#fff", bd=0, font=("Segoe UI", 10))
        self.e_pgateway.pack(fill=tk.X, ipady=4, pady=(0, 4))
        ttk.Label(right, text="e.g. 10.17.0.1 (exact gateway) or 10.17. (subnet prefix)", font=("Segoe UI", 8), style="Card.TLabel", foreground=self.dim).pack(anchor=tk.W, pady=(0, 8))

        self.btn_save_profile = ttk.Button(right, text="💾 Save Profile", style="Action.TButton", command=self._save_profile_fields)
        self.btn_save_profile.pack(anchor=tk.W)

        self._refresh_profiles_view()

    def _init_proxy(self):
        frame = self.tab_proxy

        card = ttk.Frame(frame, style="Card.TFrame", padding=16)
        card.pack(fill=tk.BOTH, expand=True, padx=14, pady=12)

        ttk.Label(card, text="Hotspot & Multi-Device Internet Sharing", font=("Segoe UI", 12, "bold"), style="Card.TLabel").pack(anchor=tk.W, pady=(0, 6))
        
        info = (
            "Share your authenticated Wi-Fi connection with phones, consoles, smart TVs, or other laptops.\n"
            "1. Turn on Windows Mobile Hotspot in Windows Settings.\n"
            "2. Connect other devices to your Windows Hotspot.\n"
            "3. On their Wi-Fi settings, set Manual Proxy to this PC's IP and Port below."
        )
        ttk.Label(card, text=info, wraplength=700, style="Card.TLabel", foreground=self.dim).pack(anchor=tk.W, pady=(0, 14))

        self.proxy_var = tk.BooleanVar(value=self.core.config.get("proxy_enabled", False))
        tk.Checkbutton(card, text="Enable Local Sharing Proxy Server", variable=self.proxy_var, font=("Segoe UI", 10, "bold"), bg=self.card, fg="#ffffff", selectcolor="#121316", activebackground=self.card, activeforeground="#ffffff", command=self._toggle_proxy).pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(card, text="Proxy Port:", style="Card.TLabel").pack(anchor=tk.W, pady=(4, 2))
        self.e_proxy_port = tk.Entry(card, bg=self.bg, fg="#ffffff", insertbackground="#fff", bd=0, font=("Segoe UI", 10), width=15)
        self.e_proxy_port.insert(0, str(self.core.config.get("proxy_port", 8888)))
        self.e_proxy_port.pack(anchor=tk.W, ipady=4, pady=(0, 12))

        if self.core.proxy_server.running:
            status_text = f"Proxy is currently: Running on port {self.core.proxy_server.port}"
        elif self.core.config.get("proxy_enabled", False):
            # Bug 7: Show "Starting..." at launch before core.start() has fired
            status_text = "Proxy is currently: Starting..."
            self.root.after(600, self._refresh_proxy_label)
        else:
            status_text = "Proxy is currently: Stopped"
        self.lbl_proxy_status = ttk.Label(card, text=status_text, font=("Segoe UI", 10, "bold"), style="Card.TLabel", foreground=self.accent)
        self.lbl_proxy_status.pack(anchor=tk.W, pady=(4, 6))

        # Proxy Traffic Header Sniffing (Diagnostic Mode)
        self.sniff_var = tk.BooleanVar(value=self.core.config.get("proxy_sniff_headers", False))
        tk.Checkbutton(
            card,
            text="Log HTTP Traffic Metadata (Diagnostic Mode: Host, UA, URI to Live Feed)",
            variable=self.sniff_var,
            font=("Segoe UI", 9),
            bg=self.card,
            fg="#ffffff",
            selectcolor="#121316",
            activebackground=self.card,
            activeforeground="#ffffff",
            command=self._toggle_proxy_sniffing
        ).pack(anchor=tk.W, pady=(0, 10))

        # Feature 3: Data Usage & Live Bandwidth Metering Dashboard
        meter_card = ttk.Frame(card, style="Card.TFrame", padding=12)
        meter_card.pack(fill=tk.X, pady=(4, 0))

        ttk.Label(meter_card, text="📊 Live Hotspot Bandwidth & Usage Meter", font=("Segoe UI", 11, "bold"), style="Card.TLabel").pack(anchor=tk.W, pady=(0, 6))

        stats_grid = tk.Frame(meter_card, bg=self.card)
        stats_grid.pack(fill=tk.X)

        ttk.Label(stats_grid, text="Active Tunnel Clients:", style="Card.TLabel").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.lbl_proxy_clients = ttk.Label(stats_grid, text="0", font=("Segoe UI", 9, "bold"), style="Card.TLabel", foreground="#5af78e")
        self.lbl_proxy_clients.grid(row=0, column=1, sticky=tk.W, padx=10, pady=2)

        ttk.Label(stats_grid, text="Total Downloaded (Recv):", style="Card.TLabel").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.lbl_proxy_recv = ttk.Label(stats_grid, text="0.00 MB", font=("Segoe UI", 9, "bold"), style="Card.TLabel", foreground=self.accent)
        self.lbl_proxy_recv.grid(row=1, column=1, sticky=tk.W, padx=10, pady=2)

        ttk.Label(stats_grid, text="Total Uploaded (Sent):", style="Card.TLabel").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.lbl_proxy_sent = ttk.Label(stats_grid, text="0.00 MB", font=("Segoe UI", 9, "bold"), style="Card.TLabel", foreground="#f39c12")
        self.lbl_proxy_sent.grid(row=2, column=1, sticky=tk.W, padx=10, pady=2)

        ttk.Button(meter_card, text="🔄 Reset Counters", style="Action.TButton", command=self._reset_proxy_counters).pack(anchor=tk.W, pady=(8, 0))

    def _refresh_proxy_label(self):
        """Update proxy status label once startup completes (Bug 7)."""
        if hasattr(self, "lbl_proxy_status"):
            if self.core.proxy_server.running:
                self.lbl_proxy_status.config(text=f"Proxy is currently: Running on port {self.core.proxy_server.port}")
            elif self.core.config.get("proxy_enabled", False):
                self.lbl_proxy_status.config(text="Proxy is currently: Failed to start")
            else:
                self.lbl_proxy_status.config(text="Proxy is currently: Stopped")

    def _init_live_monitor(self):
        frame = self.tab_live

        # Top Metric Cards Grid
        top_grid = tk.Frame(frame, bg=self.bg)
        top_grid.pack(fill=tk.X, padx=14, pady=(10, 6))

        # Card 1: Download Speed
        c_down = ttk.Frame(top_grid, style="Card.TFrame", padding=14)
        c_down.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        ttk.Label(c_down, text="⬇ Download Speed", font=("Segoe UI", 10), style="Card.TLabel", foreground=self.dim).pack(anchor=tk.W)
        self.lbl_live_down = tk.Label(c_down, text="0.0 KB/s", font=("Segoe UI", 18, "bold"), bg=self.card, fg="#2ecc71")
        self.lbl_live_down.pack(anchor=tk.W, pady=(4, 0))

        # Card 2: Upload Speed
        c_up = ttk.Frame(top_grid, style="Card.TFrame", padding=14)
        c_up.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3)
        ttk.Label(c_up, text="⬆ Upload Speed", font=("Segoe UI", 10), style="Card.TLabel", foreground=self.dim).pack(anchor=tk.W)
        self.lbl_live_up = tk.Label(c_up, text="0.0 KB/s", font=("Segoe UI", 18, "bold"), bg=self.card, fg="#3498db")
        self.lbl_live_up.pack(anchor=tk.W, pady=(4, 0))

        # Card 3: Ping / Latency
        c_ping = ttk.Frame(top_grid, style="Card.TFrame", padding=14)
        c_ping.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3)
        ttk.Label(c_ping, text="⚡ Latency (Ping)", font=("Segoe UI", 10), style="Card.TLabel", foreground=self.dim).pack(anchor=tk.W)
        self.lbl_live_ping = tk.Label(c_ping, text="-- ms", font=("Segoe UI", 18, "bold"), bg=self.card, fg="#f1c40f")
        self.lbl_live_ping.pack(anchor=tk.W, pady=(4, 0))

        # Card 4: Packet Loss
        c_loss = ttk.Frame(top_grid, style="Card.TFrame", padding=14)
        c_loss.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))
        ttk.Label(c_loss, text="📉 Packet Loss", font=("Segoe UI", 10), style="Card.TLabel", foreground=self.dim).pack(anchor=tk.W)
        self.lbl_live_loss = tk.Label(c_loss, text="0%", font=("Segoe UI", 18, "bold"), bg=self.card, fg="#2ecc71")
        self.lbl_live_loss.pack(anchor=tk.W, pady=(4, 0))

        # Middle Details Card: Session Data Usage & Network Target
        card_details = ttk.Frame(frame, style="Card.TFrame", padding=16)
        card_details.pack(fill=tk.X, padx=14, pady=6)

        ttk.Label(card_details, text="Cumulative Session Network Usage & Telemetry", font=("Segoe UI", 11, "bold"), style="Card.TLabel").grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))

        ttk.Label(card_details, text="Total Received (In):", style="Card.TLabel").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.lbl_live_total_in = ttk.Label(card_details, text="0.00 MB", font=("Segoe UI", 10, "bold"), style="Card.TLabel")
        self.lbl_live_total_in.grid(row=1, column=1, sticky=tk.W, padx=10, pady=3)

        ttk.Label(card_details, text="Total Sent (Out):", style="Card.TLabel").grid(row=1, column=2, sticky=tk.W, pady=3)
        self.lbl_live_total_out = ttk.Label(card_details, text="0.00 MB", font=("Segoe UI", 10, "bold"), style="Card.TLabel")
        self.lbl_live_total_out.grid(row=1, column=3, sticky=tk.W, padx=10, pady=3)

        ttk.Label(card_details, text="Gateway Ping Target:", style="Card.TLabel").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.lbl_live_gw_target = ttk.Label(card_details, text="-", style="Card.TLabel")
        self.lbl_live_gw_target.grid(row=2, column=1, sticky=tk.W, padx=10, pady=3)

        ttk.Label(card_details, text="Portal Controller Target:", style="Card.TLabel").grid(row=2, column=2, sticky=tk.W, pady=3)
        self.lbl_live_portal_target = ttk.Label(card_details, text="-", style="Card.TLabel")
        self.lbl_live_portal_target.grid(row=2, column=3, sticky=tk.W, padx=10, pady=3)

        # Bottom History Chart / Log Box
        card_hist = ttk.Frame(frame, style="Card.TFrame", padding=14)
        card_hist.pack(fill=tk.BOTH, expand=True, padx=14, pady=(6, 12))

        ttk.Label(card_hist, text="Real-Time Ping & Latency Trend", font=("Segoe UI", 11, "bold"), style="Card.TLabel").pack(anchor=tk.W, pady=(0, 6))
        self.live_mon_box = tk.Text(card_hist, bg=self.bg, fg="#5af78e", font=("Consolas", 9), bd=0, padx=8, pady=8, height=8)
        self.live_mon_box.pack(fill=tk.BOTH, expand=True)
        self.live_mon_box.insert(tk.END, "Real-time network telemetry initialized. Polling speed, latency, and packet loss...\n")
        self.live_mon_box.config(state=tk.DISABLED)

    def _live_monitor_ping_worker(self):
        """Dedicated background daemon measuring ICMP latency and packet loss."""
        while self.live_mon_worker_running:
            try:
                # Bug 40 fix: If user disabled Live Monitor in settings, don't waste CPU spawning ping.exe
                if not self.core.config.get("live_monitor_enabled", True):
                    self.live_mon_wake_event.wait(3.0)
                    self.live_mon_wake_event.clear()
                    continue

                # Target Gateway first, fallback to Internet DNS 1.1.1.1
                gw = self.core.gateway_ip if (self.core.gateway_ip and self.core.gateway_ip != "-") else "1.1.1.1"
                ping_target = gw
                cmd = ["ping", "-n", "2", "-w", "800", ping_target]
                res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore", creationflags=CREATE_NO_WINDOW)
                out = res.stdout

                # Bug 39 fix: Language-agnostic regex matching for Windows in any regional display language
                # Match: 'time=12ms', 'time<1ms', 'Average = 12ms', 'Moyenne = 12ms', 'Media = 12ms', etc.
                m_avg = re.search(r"=\s*(\d+)ms", out, re.IGNORECASE)
                if not m_avg:
                    m_avg = re.search(r"[=<](\d+)ms", out, re.IGNORECASE)
                m_loss = re.search(r"(\d+)%", out)

                # If gateway drops ICMP echo (managed switch protection), test Internet DNS directly
                if (not m_avg or (m_loss and int(m_loss.group(1)) == 100)) and ping_target != "1.1.1.1":
                    ping_target = "1.1.1.1"
                    cmd = ["ping", "-n", "2", "-w", "800", ping_target]
                    res = subprocess.run(cmd, capture_output=True, text=True, errors="ignore", creationflags=CREATE_NO_WINDOW)
                    out = res.stdout
                    m_avg = re.search(r"=\s*(\d+)ms", out, re.IGNORECASE)
                    if not m_avg:
                        m_avg = re.search(r"[=<](\d+)ms", out, re.IGNORECASE)
                    m_loss = re.search(r"(\d+)%", out)

                if m_avg:
                    self.live_mon_ping_val = int(m_avg.group(1))
                else:
                    self.live_mon_ping_val = None

                if m_loss:
                    self.live_mon_loss_val = int(m_loss.group(1))
                else:
                    self.live_mon_loss_val = 100 if self.live_mon_ping_val is None else 0

                ts = time.strftime("%H:%M:%S")
                lat_str = f"{self.live_mon_ping_val}ms" if self.live_mon_ping_val is not None else "Timeout"
                target_label = "Gateway" if ping_target == gw else "Internet (1.1.1.1)"
                entry = f"[{ts}] Ping {target_label}: {lat_str} | Loss: {self.live_mon_loss_val}%\n"

                def _append_ui(line=entry):
                    if hasattr(self, "live_mon_box"):
                        self.live_mon_box.config(state=tk.NORMAL)
                        self.live_mon_box.insert(tk.END, line)
                        self.live_mon_box.see(tk.END)
                        # Keep max 50 lines
                        lines_cnt = int(self.live_mon_box.index("end-1c").split(".")[0])
                        if lines_cnt > 50:
                            self.live_mon_box.delete("1.0", "10.0")
                        self.live_mon_box.config(state=tk.DISABLED)

                self._tray_dispatch(_append_ui)

            except Exception:
                pass
            self.live_mon_wake_event.wait(3.0)
            self.live_mon_wake_event.clear()

    def _init_diagnostics(self):
        frame = self.tab_diag
        card = ttk.Frame(frame, style="Card.TFrame", padding=16)
        card.pack(fill=tk.BOTH, expand=True, padx=14, pady=12)

        ttk.Label(card, text="Real-Time Network Diagnostics", font=("Segoe UI", 12, "bold"), style="Card.TLabel").pack(anchor=tk.W, pady=(0, 8))

        self.btn_diag = ttk.Button(card, text="⚡ Run Comprehensive Health Check", style="Action.TButton", command=self._execute_diag)
        self.btn_diag.pack(anchor=tk.W, pady=(0, 10))

        self.diag_box = tk.Text(card, bg=self.bg, fg="#5af78e", font=("Consolas", 10), bd=0, padx=10, pady=10)
        self.diag_box.pack(fill=tk.BOTH, expand=True)
        self.diag_box.insert(tk.END, "Ready to test latency, gateway ping, DNS, and HTTP/HTTPS access.\n")
        self.diag_box.config(state=tk.DISABLED)

    def _init_stealth(self):
        frame = self.tab_stealth
        card = ttk.Frame(frame, style="Card.TFrame", padding=16)
        card.pack(fill=tk.BOTH, expand=True, padx=14, pady=12)

        ttk.Label(card, text="Device Fingerprint & Anti-Detection", font=("Segoe UI", 12, "bold"), style="Card.TLabel").pack(anchor=tk.W, pady=(0, 6))
        desc = "Disguise your device HTTP headers as a mobile phone or another browser to evade desktop tracking or portal rate-limiting policies:"
        ttk.Label(card, text=desc, wraplength=700, style="Card.TLabel", foreground=self.dim).pack(anchor=tk.W, pady=(0, 12))

        ttk.Label(card, text="Selected User-Agent Fingerprint:", style="Card.TLabel").pack(anchor=tk.W, pady=(4, 2))
        self.ua_selection = tk.StringVar(value=self.core.config.get("user_agent_mode", "Windows Chrome"))
        ua_combo = ttk.Combobox(card, textvariable=self.ua_selection, values=list(SPOOF_USER_AGENTS.keys()) + ["Custom"], state="readonly", font=("Segoe UI", 10))
        ua_combo.pack(anchor=tk.W, fill=tk.X, pady=(0, 10))
        ua_combo.bind("<<ComboboxSelected>>", self._on_ua_pick)

        ttk.Label(card, text="Header Value (editable when 'Custom' is selected):", style="Card.TLabel").pack(anchor=tk.W, pady=(4, 2))
        self.ua_preview = tk.Text(card, height=3, bg=self.bg, fg="#ffffff", font=("Consolas", 9), bd=0)
        self.ua_preview.pack(fill=tk.X, pady=(0, 12))
        self._refresh_ua_preview()

        ttk.Button(card, text="Save Fingerprint", style="Action.TButton", command=self._commit_stealth).pack(anchor=tk.W)

    def _init_settings(self):
        frame = self.tab_settings

        # Canvas with Scrollbar for Settings tab
        canvas = tk.Canvas(frame, bg=self.bg, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_content = ttk.Frame(canvas, style="Card.TFrame")

        scroll_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas_window = canvas.create_window((0, 0), window=scroll_content, anchor="nw")

        def _on_canvas_configure(e):
            canvas.itemconfig(canvas_window, width=e.width)

        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.configure(xscrollcommand=None, yscrollcommand=scrollbar.set)

        # Bug 50 fix: Restrict mousewheel scrolling strictly to when cursor enters Settings canvas, and handle precision trackpad delta
        def _on_mousewheel(event):
            delta = event.delta
            if delta != 0:
                steps = int(-1 * (delta / 120))
                if steps == 0:
                    steps = -1 if delta > 0 else 1
                canvas.yview_scroll(steps, "units")

        def _bind_mousewheel(e):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def _unbind_mousewheel(e):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)
        scroll_content.bind("<Enter>", _bind_mousewheel)
        scroll_content.bind("<Leave>", _unbind_mousewheel)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- SECTION 1: System & Automation Preferences ---
        card1 = ttk.Frame(scroll_content, style="Card.TFrame", padding=14)
        card1.pack(fill=tk.X, padx=12, pady=(10, 6))

        ttk.Label(card1, text="System & Automation Preferences", font=("Segoe UI", 11, "bold"), style="Card.TLabel").pack(anchor=tk.W, pady=(0, 6))

        self.autostart_var = tk.BooleanVar(value=is_auto_start_registered())
        tk.Checkbutton(card1, text="Start automatically on Windows boot (Silent / Minimized to Tray)", variable=self.autostart_var, bg=self.card, fg="#ffffff", selectcolor="#121316", activebackground=self.card, activeforeground="#ffffff", command=self._toggle_autostart).pack(anchor=tk.W, pady=2)

        self.autoprof_var = tk.BooleanVar(value=self.core.config.get("auto_profile_switching", True))
        tk.Checkbutton(card1, text="Auto-switch profile based on gateway/subnet match rule", variable=self.autoprof_var, bg=self.card, fg="#ffffff", selectcolor="#121316", activebackground=self.card, activeforeground="#ffffff", command=self._save_toggles).pack(anchor=tk.W, pady=2)

        self.adapt_ka_var = tk.BooleanVar(value=self.core.config.get("adaptive_keepalive", True))
        tk.Checkbutton(card1, text="Adaptive keepalive tuning (auto-scales interval under high latency)", variable=self.adapt_ka_var, bg=self.card, fg="#ffffff", selectcolor="#121316", activebackground=self.card, activeforeground="#ffffff", command=self._save_toggles).pack(anchor=tk.W, pady=2)

        idle_bar = tk.Frame(card1, bg=self.card)
        idle_bar.pack(anchor=tk.W, pady=2)
        self.idle_logout_var = tk.BooleanVar(value=self.core.config.get("idle_logout_enabled", False))
        tk.Checkbutton(idle_bar, text="Idle auto-logout after user inactivity:", variable=self.idle_logout_var, bg=self.card, fg="#ffffff", selectcolor="#121316", activebackground=self.card, activeforeground="#ffffff", command=self._save_toggles).pack(side=tk.LEFT)
        self.e_idle_mins = tk.Entry(idle_bar, width=4, bg=self.bg, fg="#ffffff", insertbackground="#fff", bd=0, font=("Segoe UI", 9))
        self.e_idle_mins.insert(0, str(self.core.config.get("idle_logout_minutes", 30)))
        self.e_idle_mins.pack(side=tk.LEFT, padx=6)
        self.e_idle_mins.bind("<FocusOut>", self._save_idle_mins)
        self.e_idle_mins.bind("<Return>", self._save_idle_mins)
        ttk.Label(idle_bar, text="minutes", style="Card.TLabel").pack(side=tk.LEFT)

        # --- SECTION 2: Network & DNS Preferences ---
        card2 = ttk.Frame(scroll_content, style="Card.TFrame", padding=14)
        card2.pack(fill=tk.X, padx=12, pady=6)

        ttk.Label(card2, text="Network, DNS & Probe Endpoints", font=("Segoe UI", 11, "bold"), style="Card.TLabel").pack(anchor=tk.W, pady=(0, 6))

        self.doh_var = tk.BooleanVar(value=self.core.config.get("doh_fallback_enabled", False))
        tk.Checkbutton(card2, text="Automated DNS-over-HTTPS fallback (Cloudflare 1.1.1.1 DoH when UDP DNS 53 is blocked)", variable=self.doh_var, bg=self.card, fg="#ffffff", selectcolor="#121316", activebackground=self.card, activeforeground="#ffffff", command=self._save_toggles).pack(anchor=tk.W, pady=2)

        probe_bar = tk.Frame(card2, bg=self.card)
        probe_bar.pack(fill=tk.X, pady=4)
        ttk.Label(probe_bar, text="Base Keepalive Interval:", style="Card.TLabel").pack(side=tk.LEFT)
        self.e_ka_interval = tk.Entry(probe_bar, width=5, bg=self.bg, fg="#ffffff", insertbackground="#fff", bd=0, font=("Segoe UI", 9))
        self.e_ka_interval.insert(0, str(self.core.config.get("keepalive_interval", 120)))
        self.e_ka_interval.pack(side=tk.LEFT, padx=6)
        ttk.Label(probe_bar, text="seconds (recommended: 60 - 180s)", font=("Segoe UI", 8), style="Card.TLabel", foreground=self.dim).pack(side=tk.LEFT)
        ttk.Button(probe_bar, text="Apply", style="Action.TButton", command=self._save_keepalive_interval).pack(side=tk.RIGHT)

        # --- SECTION 3: Trusted Portal Hosts Whitelist ---
        card3 = ttk.Frame(scroll_content, style="Card.TFrame", padding=14)
        card3.pack(fill=tk.X, padx=12, pady=6)

        ttk.Label(card3, text="Trusted Portal Redirect Hosts (Whitelist)", font=("Segoe UI", 11, "bold"), style="Card.TLabel").pack(anchor=tk.W, pady=(0, 4))
        ttk.Label(card3, text="Captive portal redirects will only be authenticated if they match your gateway or a domain in this list.", font=("Segoe UI", 8), style="Card.TLabel", foreground=self.dim).pack(anchor=tk.W, pady=(0, 6))

        hosts_frame = tk.Frame(card3, bg=self.card)
        hosts_frame.pack(fill=tk.X, pady=2)

        self.hosts_lb = tk.Listbox(hosts_frame, height=3, bg=self.bg, fg="#ffffff", selectbackground=self.accent, font=("Consolas", 9), bd=0)
        self.hosts_lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        hosts_btns = tk.Frame(hosts_frame, bg=self.card)
        hosts_btns.pack(side=tk.RIGHT, fill=tk.Y)

        self.e_new_host = tk.Entry(card3, bg=self.bg, fg="#ffffff", insertbackground="#fff", bd=0, font=("Segoe UI", 9))
        self.e_new_host.pack(fill=tk.X, pady=(6, 4))

        host_action_bar = tk.Frame(card3, bg=self.card)
        host_action_bar.pack(fill=tk.X)
        ttk.Button(host_action_bar, text="➕ Add Host", style="Action.TButton", command=self._add_trusted_host).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(host_action_bar, text="🗑 Remove Selected", style="Danger.TButton", command=self._remove_trusted_host).pack(side=tk.LEFT)

        self._refresh_trusted_hosts()

        # --- SECTION 4: Audio & Notifications ---
        card4 = ttk.Frame(scroll_content, style="Card.TFrame", padding=14)
        card4.pack(fill=tk.X, padx=12, pady=6)

        ttk.Label(card4, text="Audio & Alert Preferences", font=("Segoe UI", 11, "bold"), style="Card.TLabel").pack(anchor=tk.W, pady=(0, 6))

        self.snd_var = tk.BooleanVar(value=self.core.config.get("sound_alerts", True))
        tk.Checkbutton(card4, text="Audible chimes on connection state changes", variable=self.snd_var, bg=self.card, fg="#ffffff", selectcolor="#121316", activebackground=self.card, activeforeground="#ffffff", command=self._save_toggles).pack(anchor=tk.W, pady=2)

        self.ntf_var = tk.BooleanVar(value=self.core.config.get("desktop_notifications", True))
        tk.Checkbutton(card4, text="Desktop tray notifications", variable=self.ntf_var, bg=self.card, fg="#ffffff", selectcolor="#121316", activebackground=self.card, activeforeground="#ffffff", command=self._save_toggles).pack(anchor=tk.W, pady=2)

        self.live_mon_var = tk.BooleanVar(value=self.core.config.get("live_monitor_enabled", True))
        tk.Checkbutton(card4, text="Enable Live Network Monitor Tab (Speed, Ping, Packet Loss, Data Usage)", variable=self.live_mon_var, bg=self.card, fg="#ffffff", selectcolor="#121316", activebackground=self.card, activeforeground="#ffffff", command=self._toggle_live_monitor_tab).pack(anchor=tk.W, pady=2)

        # --- SECTION 5: Backup, Restore & Quick Diagnostics Tools ---
        card5 = ttk.Frame(scroll_content, style="Card.TFrame", padding=14)
        card5.pack(fill=tk.X, padx=12, pady=(6, 14))

        ttk.Label(card5, text="Configuration Backup & Windows System Tools", font=("Segoe UI", 11, "bold"), style="Card.TLabel").pack(anchor=tk.W, pady=(0, 8))

        tools_bar = tk.Frame(card5, bg=self.card)
        tools_bar.pack(fill=tk.X, pady=2)

        ttk.Button(tools_bar, text="💾 Backup Config (JSON)", style="Action.TButton", command=self._export_config).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(tools_bar, text="📂 Restore Config", style="Action.TButton", command=self._import_config).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(tools_bar, text="🧹 Flush Windows DNS", style="Action.TButton", command=self._flush_windows_dns).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(tools_bar, text="📋 Copy Network Details", style="Action.TButton", command=self._copy_network_details).pack(side=tk.LEFT)

    def _refresh_trusted_hosts(self):
        if not hasattr(self, "hosts_lb"):
            return
        self.hosts_lb.delete(0, tk.END)
        hosts = self.core.config.get("trusted_portal_hosts", [])
        for h in hosts:
            self.hosts_lb.insert(tk.END, h)

    def _add_trusted_host(self):
        raw = self.e_new_host.get().strip().lower()
        if not raw:
            return
        # Bug 30 fix: Normalize input (e.g. http://172.15.1.2:8000/ -> 172.15.1.2)
        if "://" in raw:
            parsed = urlsplit(raw)
            h = parsed.hostname or raw
        else:
            h = raw.split("/")[0].split(":")[0]
        h = h.strip("[]")
        if not h:
            return

        with _config_lock:
            hosts = self.core.config.get("trusted_portal_hosts", [])
            if h not in hosts:
                hosts.append(h)
                self.core.config["trusted_portal_hosts"] = hosts
                save_settings(self.core.config)
                self.core.log(f"[Security] Added normalized host '{h}' to trusted portal hosts allow-list.")
        self.e_new_host.delete(0, tk.END)
        self._refresh_trusted_hosts()

    def _remove_trusted_host(self):
        sel = self.hosts_lb.curselection()
        if not sel:
            return
        idx = sel[0]
        with _config_lock:
            hosts = self.core.config.get("trusted_portal_hosts", [])
            if 0 <= idx < len(hosts):
                removed = hosts.pop(idx)
                self.core.config["trusted_portal_hosts"] = hosts
                save_settings(self.core.config)
                self.core.log(f"[Security] Removed '{removed}' from trusted portal hosts allow-list.")
        self._refresh_trusted_hosts()

    def _save_keepalive_interval(self):
        val_text = self.e_ka_interval.get().strip()
        try:
            val = int(val_text)
            if not (10 <= val <= 600):
                raise ValueError("Must be between 10 and 600 seconds.")
            with _config_lock:
                self.core.config["keepalive_interval"] = val
                self.core.current_keepalive_interval = val
                save_settings(self.core.config)
            self.core.log(f"[Config] Keepalive interval updated to {val}s.")
            messagebox.showinfo("Settings", f"Keepalive interval updated to {val}s.")
        except ValueError as e:
            messagebox.showerror("Invalid Interval", f"Invalid keepalive interval: {e}")

    def _save_idle_mins(self, event=None):
        val_text = self.e_idle_mins.get().strip()
        try:
            val = int(val_text)
            if not (1 <= val <= 720):
                raise ValueError("Must be between 1 and 720 minutes.")
            with _config_lock:
                self.core.config["idle_logout_minutes"] = val
                save_settings(self.core.config)
            self.core.log(f"[Config] Idle logout threshold updated to {val}m.")
        except ValueError as e:
            # Revert to last valid config value on invalid input
            valid_val = self.core.config.get("idle_logout_minutes", 30)
            self.e_idle_mins.delete(0, tk.END)
            self.e_idle_mins.insert(0, str(valid_val))

    def _export_config(self):
        dest = filedialog.asksaveasfilename(
            title="Backup GITwifi Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"gitwifi_config_backup_{int(time.time())}.json"
        )
        if not dest:
            return
        try:
            # Bug 27 fix: If config.json doesn't exist on disk yet, save current in-memory config
            with _config_lock:
                save_settings(self.core.config)
            with open(CONFIG_PATH, "r", encoding="utf-8-sig") as f_in:
                data = json.load(f_in)
            # Remove transient session tokens from exported file
            data.pop("last_magic", None)
            data.pop("_last_magic_raw", None)
            with open(dest, "w", encoding="utf-8") as f_out:
                json.dump(data, f_out, indent=4)
            self.core.log(f"[Config] Backup saved to: {dest}")
            messagebox.showinfo("Backup Success", f"Configuration backup saved successfully to:\n{dest}")
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to save backup: {e}")

    def _import_config(self):
        src = filedialog.askopenfilename(
            title="Restore GITwifi Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not src:
            return
        if not messagebox.askyesno("Confirm Restore", "Restoring configuration will overwrite current settings and reload profiles. Continue?"):
            return
        try:
            with open(src, "r", encoding="utf-8-sig") as f:
                loaded = json.load(f)
            if not isinstance(loaded, dict) or "profiles" not in loaded:
                raise ValueError("Invalid configuration file format.")
            
            with _config_lock:
                shutil.copy2(src, CONFIG_PATH)
                new_cfg = load_settings()
                self.core.config = new_cfg

            # Bug 26 fix: Refresh all UI controls and variables with the newly restored configuration
            self._refresh_profiles_view()
            self._refresh_trusted_hosts()
            if hasattr(self, "doh_var"):
                self.doh_var.set(new_cfg.get("doh_fallback_enabled", False))
            if hasattr(self, "snd_var"):
                self.snd_var.set(new_cfg.get("sound_alerts", True))
            if hasattr(self, "ntf_var"):
                self.ntf_var.set(new_cfg.get("desktop_notifications", True))
            if hasattr(self, "live_mon_var"):
                self.live_mon_var.set(new_cfg.get("live_monitor_enabled", True))
            if hasattr(self, "autoprof_var"):
                self.autoprof_var.set(new_cfg.get("auto_profile_switching", True))
            if hasattr(self, "adapt_ka_var"):
                self.adapt_ka_var.set(new_cfg.get("adaptive_keepalive", True))
            if hasattr(self, "idle_logout_var"):
                self.idle_logout_var.set(new_cfg.get("idle_logout_enabled", False))
            if hasattr(self, "e_ka_interval"):
                self.e_ka_interval.delete(0, tk.END)
                self.e_ka_interval.insert(0, str(new_cfg.get("keepalive_interval", 120)))
            if hasattr(self, "e_idle_mins"):
                self.e_idle_mins.delete(0, tk.END)
                self.e_idle_mins.insert(0, str(new_cfg.get("idle_logout_minutes", 30)))
            if hasattr(self, "ua_selection"):
                self.ua_selection.set(new_cfg.get("spoof_ua_mode", "Windows Chrome"))
                self._refresh_ua_preview()
            if hasattr(self, "sniff_var"):
                self.sniff_var.set(new_cfg.get("proxy_sniff_headers", False))
                self.core.proxy_server.sniff_headers = new_cfg.get("proxy_sniff_headers", False)
            if hasattr(self, "e_proxy_port"):
                self.e_proxy_port.delete(0, tk.END)
                self.e_proxy_port.insert(0, str(new_cfg.get("proxy_port", 8888)))
            if hasattr(self, "proxy_var"):
                desired_proxy = new_cfg.get("proxy_enabled", False)
                self.proxy_var.set(desired_proxy)
                self._toggle_proxy()

            self.core.log("[Config] Configuration restored successfully from backup.")
            messagebox.showinfo("Restore Success", "Configuration successfully imported and reloaded.")
        except Exception as e:
            messagebox.showerror("Restore Error", f"Failed to import configuration: {e}")

    def _flush_windows_dns(self):
        try:
            res = subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True, creationflags=CREATE_NO_WINDOW, check=False)
            if res.returncode == 0:
                self.core.log("[System] Windows DNS Resolver Cache flushed successfully (ipconfig /flushdns).")
                messagebox.showinfo("DNS Flushed", "Windows DNS Resolver Cache successfully flushed.")
            else:
                self.core.log(f"[System] Windows DNS flush exited with error code {res.returncode}: {res.stderr or res.stdout}")
                messagebox.showwarning("DNS Flush Notice", f"DNS flush command returned code {res.returncode}.\n{res.stderr or res.stdout}")
        except Exception as e:
            self.core.log(f"[System] Failed to execute DNS cache flush: {e}")
            messagebox.showerror("DNS Flush Error", f"Failed to execute DNS cache flush: {e}")

    def _copy_network_details(self):
        ka_url = self.core.keepalive_url or "None"
        if ka_url != "None" and "?" in ka_url:
            base_url, _ = ka_url.split("?", 1)
            ka_url = f"{base_url}?[REDACTED_TOKEN]"

        info_lines = [
            f"Local IPv4:       {self.core.local_ip}",
            f"Default Gateway:  {self.core.gateway_ip}",
            f"Portal Host:      {self.core.portal_host}:{self.core.portal_port}",
            f"Connection State: {self.core.status}",
            f"Keepalive URL:    {ka_url}"
        ]
        text = "\n".join(info_lines)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.core.log("[System] Network configuration details copied to Windows clipboard.")
        messagebox.showinfo("Copied", "Network details copied to clipboard:\n\n" + text)

    def _init_logs(self):
        frame = self.tab_logs
        self.feed_box = tk.Text(frame, bg=self.bg, fg=self.fg, font=("Consolas", 9), bd=0, padx=10, pady=10)
        self.feed_box.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

    def _toggle_password_visibility(self):
        show_char = "" if self.show_pwd_var.get() else "●"
        self.e_ppass.config(show=show_char)

    def _start_new_profile(self):
        self.editor_mode = "new"
        self.editing_index = None
        self.lbl_editor_mode.config(text="Mode: [New Profile]", foreground=self.accent)
        self.btn_save_profile.config(text="➕ Add & Save Profile")
        self.e_pname.delete(0, tk.END)
        self.e_pname.insert(0, "New Profile")
        self.e_puser.delete(0, tk.END)
        self.e_ppass.delete(0, tk.END)
        if hasattr(self, "e_pgateway"):
            self.e_pgateway.delete(0, tk.END)
        self.show_pwd_var.set(False)
        self._toggle_password_visibility()

    def _start_edit_profile(self):
        sel = self.profiles_lb.curselection()
        if not sel:
            messagebox.showinfo("Select Profile", "Please select a profile from the list to edit.")
            return
        idx = sel[0]
        profiles = self.core.config.get("profiles", [])
        if idx < len(profiles):
            self.editor_mode = "edit"
            self.editing_index = idx
            p = profiles[idx]
            self.lbl_editor_mode.config(text=f"Mode: [Editing Profile #{idx + 1}]", foreground="#f39c12")
            self.btn_save_profile.config(text="💾 Update Profile")
            self.e_pname.delete(0, tk.END)
            self.e_pname.insert(0, p.get("name", ""))
            self.e_puser.delete(0, tk.END)
            self.e_puser.insert(0, p.get("username", ""))
            self.e_ppass.delete(0, tk.END)
            self.e_ppass.insert(0, p.get("password", ""))
            if hasattr(self, "e_pgateway"):
                self.e_pgateway.delete(0, tk.END)
                self.e_pgateway.insert(0, p.get("gateway_match", ""))
            self.show_pwd_var.set(False)
            self._toggle_password_visibility()

    def _on_status(self, st):
        self.status_queue.put(st)

    def _apply_status(self, st):
        # Bug 49 fix: Explicit status color map replacing brittle 'ing' substring check
        status_colors = {
            "Connected": "#2ecc71",
            "Connecting": "#f1c40f",
            "Probing...": "#f1c40f",
            "Shotgun Probing...": "#f1c40f",
            "Logging In...": "#f1c40f",
            "Authenticating...": "#f1c40f",
            "Refreshing...": "#f1c40f",
            "Untrusted Portal": "#e67e22",
            "No Profile Configured": "#e67e22",
            "Login Paused (Retries Exceeded)": "#e67e22",
            "Credentials Rejected": "#e74c3c",
            "Probe Timeout": "#e67e22",
            "Disconnected": "#e74c3c",
            "Error": "#e74c3c",
        }
        col = status_colors.get(st, "#f1c40f" if any(st.startswith(x) for x in ("Log", "Prob", "Conn", "Auth")) else "#e74c3c")
        self.status_pill.config(text=f"● {st}", fg=col)
        self._refresh_network_labels()
        self._update_tray(st)

    def _refresh_network_labels(self):
        if hasattr(self, "lbl_ip"):
            self.lbl_ip.config(text=self.core.local_ip)
            self.lbl_gw.config(text=self.core.gateway_ip)

    def _on_log(self, text):
        self.log_queue.put(text)

    def _on_auto_profile_switch(self, new_idx: int):
        """Schedule UI profile list and label refresh on Tkinter main thread when auto-profile switches (Bug 19)."""
        self.tray_action_queue.put(self._refresh_profiles_view)

    def _flush_log_queue(self):
        try:
            # Bug 6: Safely drain and execute tray callables on the Tkinter main thread
            try:
                while True:
                    action_item = self.tray_action_queue.get_nowait()
                    if callable(action_item):
                        action_item()
                    elif isinstance(action_item, tuple) and len(action_item) >= 1:
                        fn, *args = action_item
                        fn(*args)
            except queue.Empty:
                pass

            try:
                while True:
                    self._apply_status(self.status_queue.get_nowait())
            except queue.Empty:
                pass

            # Periodically refresh IP and gateway labels even if status hasn't changed
            self._refresh_network_labels()

            batch = []
            try:
                while len(batch) < 50:
                    msg = self.log_queue.get_nowait()
                    batch.append(msg)
            except queue.Empty:
                pass

            if batch and hasattr(self, "feed_box"):
                self.feed_box.insert(tk.END, "\n".join(batch) + "\n")
                self.feed_box.see(tk.END)
                if int(self.feed_box.index("end-1c").split(".")[0]) > 2000:
                    self.feed_box.delete("1.0", "500.0")
        except Exception as e:
            print(f"[UI] Error updating log/status queue: {e}")
        finally:
            self.root.after(100, self._flush_log_queue)

    def _tick_timer(self):
        try:
            # 1. Update session duration timer
            if self.core.status == "Connected" and self.core.session_start:
                s = int(time.time() - self.core.session_start)
                h, m, sec = s // 3600, (s % 3600) // 60, s % 60
                self.lbl_timer.config(text=f"{h:02d}:{m:02d}:{sec:02d}")
            else:
                self.lbl_timer.config(text="00:00:00")

            # 2. Update Live Bandwidth Metering (Feature 3)
            if hasattr(self, "lbl_proxy_recv") and hasattr(self, "lbl_proxy_sent"):
                proxy = self.core.proxy_server
                with proxy.stats_lock:
                    bs = proxy.bytes_sent
                    br = proxy.bytes_recv
                with proxy.clients_lock:
                    active_c = proxy.active_clients

                def _fmt_bytes(b: int) -> str:
                    if b >= 1073741824:
                        return f"{b / 1073741824:.2f} GB"
                    if b >= 1048576:
                        return f"{b / 1048576:.2f} MB"
                    if b >= 1024:
                        return f"{b / 1024:.1f} KB"
                    return f"{b} B"

                self.lbl_proxy_recv.config(text=_fmt_bytes(br))
                self.lbl_proxy_sent.config(text=_fmt_bytes(bs))
                if hasattr(self, "lbl_proxy_clients"):
                    self.lbl_proxy_clients.config(text=str(active_c))

            # 3. Live Network Monitor Telemetry (Speed, Ping, Packet Loss, Data Usage)
            if hasattr(self, "lbl_live_down") and self.core.config.get("live_monitor_enabled", True):
                try:
                    now = time.time()
                    dt = max(0.1, now - self.live_mon_prev_time)
                    cur_in, cur_out = get_system_network_io()
                    
                    prev_in, prev_out = self.live_mon_prev_io
                    if cur_in >= prev_in and cur_out >= prev_out:
                        speed_in = (cur_in - prev_in) / dt
                        speed_out = (cur_out - prev_out) / dt
                    else:
                        speed_in, speed_out = 0.0, 0.0

                    self.live_mon_prev_io = (cur_in, cur_out)
                    self.live_mon_prev_time = now

                    def _fmt_rate(bps: float) -> str:
                        if bps >= 1048576:
                            return f"{bps / 1048576:.2f} MB/s"
                        if bps >= 1024:
                            return f"{bps / 1024:.1f} KB/s"
                        return f"{int(bps)} B/s"

                    def _fmt_total(b: int) -> str:
                        if b >= 1073741824:
                            return f"{b / 1073741824:.2f} GB"
                        if b >= 1048576:
                            return f"{b / 1048576:.2f} MB"
                        if b >= 1024:
                            return f"{b / 1024:.1f} KB"
                        return f"{b} B"

                    self.lbl_live_down.config(text=_fmt_rate(speed_in))
                    self.lbl_live_up.config(text=_fmt_rate(speed_out))
                    self.lbl_live_total_in.config(text=_fmt_total(cur_in))
                    self.lbl_live_total_out.config(text=_fmt_total(cur_out))

                    # Update Ping & Loss display
                    if self.live_mon_ping_val is not None:
                        p_col = "#2ecc71" if self.live_mon_ping_val < 50 else ("#f1c40f" if self.live_mon_ping_val < 150 else "#e74c3c")
                        self.lbl_live_ping.config(text=f"{self.live_mon_ping_val} ms", fg=p_col)
                    else:
                        self.lbl_live_ping.config(text="-- ms", fg="#e74c3c")

                    loss_col = "#2ecc71" if self.live_mon_loss_val == 0 else ("#f1c40f" if self.live_mon_loss_val < 20 else "#e74c3c")
                    self.lbl_live_loss.config(text=f"{self.live_mon_loss_val}%", fg=loss_col)

                    # Targets
                    self.lbl_live_gw_target.config(text=self.core.gateway_ip)
                    p_host = self.core.portal_host if (self.core.portal_host and self.core.portal_host != "-") else self.core.gateway_ip
                    self.lbl_live_portal_target.config(text=f"{p_host}:{self.core.portal_port}")

                except Exception:
                    pass

            # 4. Idle Auto-Logout Evaluation (Feature 6 & Bug 8/44 fix)
            if self.core.status == "Connected" and self.core.config.get("idle_logout_enabled", False):
                with self.core.state_lock:
                    already_logging_out = self.core.user_signed_out or getattr(self.core, "_logout_in_progress", False)
                if not already_logging_out:
                    try:
                        allowed_idle_mins = max(1, int(self.core.config.get("idle_logout_minutes", 30)))
                    except (ValueError, TypeError):
                        allowed_idle_mins = 30
                    idle_sec = get_system_idle_seconds()
                    
                    # Check if proxy has active hotspot clients connected (Bug 44 fix)
                    proxy_active = False
                    if getattr(self.core, "proxy_server", None):
                        with self.core.proxy_server.clients_lock:
                            proxy_active = (self.core.proxy_server.active_clients > 0)

                    if idle_sec >= (allowed_idle_mins * 60) and not proxy_active:
                        with self.core.state_lock:
                            self.core._logout_in_progress = True
                        self.core.log(f"[Idle Guard] System idle for {int(idle_sec // 60)}m (threshold: {allowed_idle_mins}m). Triggering auto-logout...")
                        def _do_idle_logout():
                            try:
                                self.core.logout()
                            finally:
                                with self.core.state_lock:
                                    self.core._logout_in_progress = False
                        threading.Thread(target=_do_idle_logout, daemon=True).start()
        except Exception as e:
            print(f"[Timer] Unhandled error in tick_timer: {e}")
        finally:
            self.root.after(1000, self._tick_timer)

    def _reset_proxy_counters(self):
        proxy = self.core.proxy_server
        with proxy.stats_lock:
            proxy.bytes_sent = 0
            proxy.bytes_recv = 0
        if hasattr(self, "lbl_proxy_recv"):
            self.lbl_proxy_recv.config(text="0.00 MB")
            self.lbl_proxy_sent.config(text="0.00 MB")
        self.core.log("[Proxy] Bandwidth usage counters reset to 0.")

    def _refresh_profiles_view(self):
        self.profiles_lb.delete(0, tk.END)
        profiles = self.core.config.get("profiles", [])
        act = self.core.config.get("active_profile_index", 0)
        for i, p in enumerate(profiles):
            mark = "⭐ " if i == act else "   "
            gw_tag = f" [{p['gateway_match']}]" if p.get("gateway_match") else ""
            self.profiles_lb.insert(tk.END, f"{mark}{p.get('name', 'Profile')} ({p.get('username')}){gw_tag}")

        active_prof = self.core.get_active_profile()
        if active_prof:
            self.lbl_profile.config(text=f"{active_prof.get('name', 'Profile')} ({active_prof.get('username')})")
        else:
            self.lbl_profile.config(text="None Configured")

    def _on_profile_picked(self, event):
        sel = self.profiles_lb.curselection()
        if sel:
            idx = sel[0]
            profiles = self.core.config.get("profiles", [])
            if idx < len(profiles):
                p = profiles[idx]
                self.editor_mode = "edit"
                self.editing_index = idx
                self.lbl_editor_mode.config(text=f"Mode: [Editing Profile #{idx + 1}]", foreground="#f39c12")
                self.btn_save_profile.config(text="💾 Update Profile")
                self.e_pname.delete(0, tk.END)
                self.e_pname.insert(0, p.get("name", ""))
                self.e_puser.delete(0, tk.END)
                self.e_puser.insert(0, p.get("username", ""))
                self.e_ppass.delete(0, tk.END)
                self.e_ppass.insert(0, p.get("password", ""))
                if hasattr(self, "e_pgateway"):
                    self.e_pgateway.delete(0, tk.END)
                    self.e_pgateway.insert(0, p.get("gateway_match", ""))
                self.show_pwd_var.set(False)
                self._toggle_password_visibility()

    def _save_profile_fields(self):
        name = self.e_pname.get().strip() or "Profile"
        user = self.e_puser.get().strip()
        pwd = self.e_ppass.get()  # Do NOT strip — passwords may have intentional spaces
        gw_rule = self.e_pgateway.get().strip() if hasattr(self, "e_pgateway") else ""

        if not user or not pwd:
            messagebox.showwarning("Notice", "Username and password cannot be empty.")
            return

        with _config_lock:
            profiles = self.core.config.get("profiles", [])
            was_single_empty = (len(profiles) == 1 and not profiles[0].get("username"))

            prof_entry = {"name": name, "username": user, "password": pwd}
            if gw_rule:
                prof_entry["gateway_match"] = gw_rule

            if self.editor_mode == "edit" and self.editing_index is not None and self.editing_index < len(profiles):
                saved_idx = self.editing_index
                profiles[saved_idx] = prof_entry
                msg = f"Profile '{name}' updated successfully."
            else:
                if was_single_empty:
                    # User filled in the initial empty profile
                    profiles[0] = prof_entry
                    saved_idx = 0
                    msg = f"Profile '{name}' configured successfully."
                else:
                    profiles.append(prof_entry)
                    saved_idx = len(profiles) - 1
                    msg = f"New profile '{name}' added successfully."

            self.core.config["profiles"] = profiles

            # Bug 10a: First real profile auto-activation and probe
            active_idx = self.core.config.get("active_profile_index", 0)
            should_activate_and_probe = False
            if was_single_empty or len(profiles) == 1:
                self.core.config["active_profile_index"] = 0
                self.core.failed_login_attempts = 0
                should_activate_and_probe = True
            elif saved_idx == active_idx:
                # Bug 10b: Editing active profile password resets retry counter
                self.core.failed_login_attempts = 0
                should_activate_and_probe = True

            save_settings(self.core.config)

        self._refresh_profiles_view()
        messagebox.showinfo("Success", msg)
        self._start_new_profile()

        if should_activate_and_probe:
            was_connected = (self.core.status == "Connected")
            def _edit_probe_worker():
                if was_connected:
                    self.core.log("Logging out of previous session before authenticating updated active profile...")
                    self.core.logout(disconnect_wifi=False)
                self._force_probe(reconnect_wlan=False)
            threading.Thread(target=_edit_probe_worker, daemon=True).start()

    def _set_active_profile(self):
        sel = self.profiles_lb.curselection()
        if not sel:
            return
        new_idx = sel[0]
        current_idx = self.core.config.get("active_profile_index", 0)
        if new_idx == current_idx:
            return
        was_connected = (self.core.status == "Connected")
        if was_connected:
            if not messagebox.askyesno(
                "Switch Profile",
                "You are currently connected. Switching the active profile will log out of the current portal session and authenticate with the new credentials. Continue?"
            ):
                return
        with _config_lock:
            self.core.config["active_profile_index"] = new_idx
            self.core.failed_login_attempts = 0
            save_settings(self.core.config)
        self._refresh_profiles_view()
        self.core.log(f"Active profile switched to profile #{new_idx + 1}")
        
        # Bug 7 fix: If connected, explicitly terminate old portal session so the firewall demands new credentials
        def _switch_worker():
            if was_connected:
                self.core.log("Logging out of previous session before authenticating new profile...")
                self.core.logout(disconnect_wifi=False)
            self._force_probe(reconnect_wlan=False)

        threading.Thread(target=_switch_worker, daemon=True).start()

    def _del_profile(self):
        sel = self.profiles_lb.curselection()
        if not sel:
            return
        del_idx = sel[0]
        with _config_lock:
            profiles = self.core.config.get("profiles", [])
            if del_idx >= len(profiles):
                return
            target_prof = profiles[del_idx]
            prof_name = target_prof.get("name", f"Profile #{del_idx+1}")
            active_idx = self.core.config.get("active_profile_index", 0)
            is_active = (del_idx == active_idx)

        # Bug 10c: Warn explicitly if deleting the active profile
        if is_active:
            confirm_msg = (
                f"Profile '{prof_name}' is currently ACTIVE.\n\n"
                "Deleting the active profile will disconnect any active session. Are you sure you want to delete it?"
            )
        else:
            confirm_msg = f"Are you sure you want to delete profile '{prof_name}'?"

        if not messagebox.askyesno("Confirm Delete", confirm_msg):
            return

        with _config_lock:
            del profiles[del_idx]
            self.core.config["profiles"] = profiles

            if not profiles:
                self.core.config["active_profile_index"] = 0
                self.core.set_status("No Profile Configured")
            elif is_active:
                # If deleted profile was active, set active to 0 (or next valid)
                new_act = min(del_idx, len(profiles) - 1)
                self.core.config["active_profile_index"] = new_act
                self.core.failed_login_attempts = 0
            elif del_idx < active_idx:
                self.core.config["active_profile_index"] = active_idx - 1

            save_settings(self.core.config)

        self._refresh_profiles_view()
        self._start_new_profile()

        if is_active:
            was_connected = (self.core.status == "Connected")
            def _del_probe_worker():
                if was_connected:
                    self.core.log("Logging out of previous session before authenticating new profile...")
                    self.core.logout(disconnect_wifi=False)
                if profiles:
                    self._force_probe(reconnect_wlan=False)
                else:
                    self.core.interrupt_cycle()

            if profiles:
                messagebox.showinfo("Profile Deleted", f"Active profile was deleted. Switched to '{profiles[self.core.config['active_profile_index']].get('name', 'Profile')}'.")
                threading.Thread(target=_del_probe_worker, daemon=True).start()
            else:
                messagebox.showinfo("Profile Deleted", "Active profile was deleted. No profiles remain configured.")
                threading.Thread(target=_del_probe_worker, daemon=True).start()

    def _force_probe(self, reconnect_wlan: bool = True):
        self.core.failed_login_attempts = 0
        self.core.error_backoff_seconds = 30.0
        with self.core.state_lock:
            self.core.keepalive_url = None
            self.core.user_signed_out = False
            wlan_target = self.core.last_connected_profile or self.core.last_connected_ssid
            if not reconnect_wlan:
                wlan_target = None

        if reconnect_wlan and wlan_target:
            try:
                subprocess.Popen(["netsh", "wlan", "connect", f"name={wlan_target}"], creationflags=CREATE_NO_WINDOW)
                self.core.log(f"Reconnecting to Wi-Fi: {wlan_target}")
            except Exception as e:
                self.core.log(f"WLAN reconnect error: {e}")
            self.core.last_connected_ssid = None
            self.core.last_connected_profile = None

        self.core.interrupt_cycle()

    def _save_toggles(self):
        with _config_lock:
            self.core.config["sound_alerts"] = self.snd_var.get()
            self.core.config["desktop_notifications"] = self.ntf_var.get()
            if hasattr(self, "autoprof_var"):
                self.core.config["auto_profile_switching"] = self.autoprof_var.get()
            if hasattr(self, "adapt_ka_var"):
                self.core.config["adaptive_keepalive"] = self.adapt_ka_var.get()
            if hasattr(self, "idle_logout_var"):
                self.core.config["idle_logout_enabled"] = self.idle_logout_var.get()
            if hasattr(self, "e_idle_mins"):
                try:
                    self.core.config["idle_logout_minutes"] = max(1, int(self.e_idle_mins.get().strip()))
                except ValueError:
                    pass
            if hasattr(self, "doh_var"):
                self.core.config["doh_fallback_enabled"] = self.doh_var.get()
            if hasattr(self, "live_mon_var"):
                self.core.config["live_monitor_enabled"] = self.live_mon_var.get()
            save_settings(self.core.config)

    def _toggle_live_monitor_tab(self):
        enabled = self.live_mon_var.get()
        with _config_lock:
            self.core.config["live_monitor_enabled"] = enabled
            save_settings(self.core.config)

        # Tab index 2 is between Profiles and Hotspot Sharing
        if enabled:
            if str(self.tab_live) not in self.notebook.tabs():
                self.notebook.insert(2, self.tab_live, text=" Live Monitor ")
                self.core.log("[UI] Live Network Monitor tab enabled.")
            if hasattr(self, "lbl_live_ping"):
                ping_txt = f"{self.live_mon_ping_val} ms" if self.live_mon_ping_val is not None else "-- ms"
                self.lbl_live_ping.config(text=ping_txt)
            if hasattr(self, "lbl_live_loss"):
                self.lbl_live_loss.config(text=f"{self.live_mon_loss_val}%")
            if hasattr(self, "live_mon_wake_event"):
                self.live_mon_wake_event.set()
        else:
            if str(self.tab_live) in self.notebook.tabs():
                self.notebook.forget(self.tab_live)
                self.core.log("[UI] Live Network Monitor tab hidden.")

    def _toggle_autostart(self):
        enable = self.autostart_var.get()
        success = set_auto_start_registered(enable)
        if success:
            with _config_lock:
                self.core.config["auto_start_enabled"] = enable
                save_settings(self.core.config)
            msg = "GITwifi will now launch automatically on Windows boot (minimized to tray)." if enable else "Automatic Windows startup disabled."
            self.core.log(f"[Autostart] {msg}")
        else:
            messagebox.showwarning("Autostart Warning", "Could not update Windows registry Run key.")
            self.autostart_var.set(is_auto_start_registered())

    def _toggle_proxy(self):
        enable = self.proxy_var.get()
        if enable:
            port_text = self.e_proxy_port.get().strip()
            try:
                p = int(port_text)
                if not (1 <= p <= 65535):
                    raise ValueError("Port must be between 1 and 65535.")
            except ValueError as ve:
                messagebox.showerror("Invalid Proxy Port", f"Invalid proxy port '{port_text}'. Please enter a number between 1 and 65535.")
                self.proxy_var.set(False)
                return

            port_changed = (self.core.proxy_server.port != p)
            self.core.proxy_server.port = p
            if port_changed and self.core.proxy_server.running:
                self.core.proxy_server.stop()
            started = self.core.proxy_server.start()

            if started and self.core.proxy_server.running:
                with _config_lock:
                    self.core.config["proxy_port"] = p
                    self.core.config["proxy_enabled"] = True
                    save_settings(self.core.config)
                self.lbl_proxy_status.config(text=f"Proxy is currently: Running on port {self.core.proxy_server.port}")
            else:
                with _config_lock:
                    self.core.config["proxy_enabled"] = False
                    save_settings(self.core.config)
                self.proxy_var.set(False)
                self.lbl_proxy_status.config(text="Proxy is currently: Failed to start")
        else:
            with _config_lock:
                self.core.config["proxy_enabled"] = False
                save_settings(self.core.config)
            self.core.proxy_server.stop()
            self.lbl_proxy_status.config(text="Proxy is currently: Stopped")

    def _toggle_proxy_sniffing(self):
        val = self.sniff_var.get()
        self.core.proxy_server.sniff_headers = val
        with _config_lock:
            self.core.config["proxy_sniff_headers"] = val
            save_settings(self.core.config)
        state_str = "ENABLED" if val else "DISABLED"
        self.core.log(f"[Proxy] HTTP traffic metadata sniffing {state_str}. Host, UA, and requested URIs will {'' if val else 'not '}be logged.")

    def _on_ua_pick(self, event=None):
        self._refresh_ua_preview()

    def _refresh_ua_preview(self):
        mode = self.ua_selection.get()
        if mode == "Custom":
            # Load stored custom UA or fall back to Chrome preset as starting point
            val = self.core.config.get("custom_user_agent") or SPOOF_USER_AGENTS["Windows Chrome"]
            # Allow editing only for Custom mode (Item 30)
            self.ua_preview.config(state=tk.NORMAL)
        else:
            val = SPOOF_USER_AGENTS.get(mode, SPOOF_USER_AGENTS["Windows Chrome"])
            # Preset modes: show the value but prevent editing
            self.ua_preview.config(state=tk.NORMAL)
        self.ua_preview.delete("1.0", tk.END)
        self.ua_preview.insert(tk.END, val)
        if mode != "Custom":
            self.ua_preview.config(state=tk.DISABLED)

    def _commit_stealth(self):
        mode = self.ua_selection.get()
        with _config_lock:
            self.core.config["user_agent_mode"] = mode
            if mode == "Custom":
                # Ensure text box is readable when saving (it may be disabled if mode was just switched)
                self.ua_preview.config(state=tk.NORMAL)
                # Bug 51 fix: Strip all internal \r and \n to prevent requests.exceptions.InvalidHeader
                raw_ua = self.ua_preview.get("1.0", tk.END)
                clean_ua = " ".join(raw_ua.split())
                self.core.config["custom_user_agent"] = clean_ua
            save_settings(self.core.config)
            self.core.error_backoff_seconds = 30.0
        messagebox.showinfo("Stealth", "User-Agent spoofing settings saved.")

    def _execute_diag(self):
        if hasattr(self, "btn_diag"):
            self.btn_diag.config(state=tk.DISABLED)
        self.diag_box.config(state=tk.NORMAL)
        self.diag_box.delete("1.0", tk.END)
        self.diag_box.insert(tk.END, "[*] Running comprehensive network & DoH telemetry check...\n\n")

        def _work():
            lines = []
            gw = self.core.gateway_ip if (self.core.gateway_ip and self.core.gateway_ip != "-") else get_default_gateway() or "127.0.0.1"
            portal_port = self.core.portal_port or AppConstants.DEFAULT_PORTAL_PORT
            local_ip = self.core.local_ip

            lines.append("=== 1. WI-FI HARDWARE & LINK TELEMETRY ===")
            try:
                # N3 Note: netsh wlan output labels (SSID, Signal, etc.) are English-only by design.
                # Native multi-language support would require direct Windows WLAN API (wlanapi.dll via ctypes).
                # Use errors='replace' to avoid locale/encoding failures on non-ASCII SSIDs
                result = subprocess.run(
                    ["netsh", "wlan", "show", "interfaces"],
                    capture_output=True, text=True, errors="replace", creationflags=CREATE_NO_WINDOW
                )
                output = result.stdout
                
                ssid, signal, rx_rate, tx_rate, channel = "Unknown", "Unknown", "Unknown", "Unknown", "Unknown"
                for line in output.splitlines():
                    line_str = line.strip()
                    if ":" not in line_str:
                        continue
                    k, v = [x.strip() for x in line_str.split(":", 1)]
                    k_lower = k.lower()
                    if "bssid" not in k_lower and "ssid" in k_lower:
                        ssid = v
                    elif "signal" in k_lower:
                        signal = v
                    elif "receive rate" in k_lower or "rx rate" in k_lower:
                        rx_rate = v
                    elif "transmit rate" in k_lower or "tx rate" in k_lower:
                        tx_rate = v
                    elif "channel" in k_lower:
                        channel = v

                if ssid == "Unknown":
                    lines.append("• Wi-Fi Telemetry:        No active Wi-Fi interface detected in netsh.")
                else:
                    lines.append(f"• Active SSID:            {ssid}")
                    lines.append(f"• Signal Strength:        {signal}")
                    lines.append(f"• Link Speed (Rx / Tx):   {rx_rate} Mbps / {tx_rate} Mbps")
                    lines.append(f"• Wi-Fi Channel:          {channel}")
            except Exception as e:
                lines.append(f"• Wi-Fi Telemetry:        FAILED ({e})")

            target_portal_host = self.core.portal_host if (self.core.portal_host and self.core.portal_host != "-") else gw
            portal_label = "OPNsense Portal" if (self.core.portal_type == "opnsense" or portal_port == 8000) else "Captive Portal"

            lines.append("\n=== 2. GATEWAY & PORTAL DAEMON HEALTH ===")
            lines.append(f"• Local IP:               {local_ip}")
            lines.append(f"• Default Gateway:        {gw}")
            lines.append(f"• {portal_label} Host:     {target_portal_host}:{portal_port}")

            t0 = time.time()
            s_portal = None
            try:
                s_portal = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s_portal.settimeout(2.0)
                s_portal.connect((target_portal_host, portal_port))
                ms = int((time.time() - t0) * 1000)
                lines.append(f"• Portal Port {portal_port}:      OPEN ({ms}ms)")
            except Exception as e:
                lines.append(f"• Portal Port {portal_port}:      BLOCKED/UNREACHABLE ({e})")
            finally:
                if s_portal:
                    try:
                        s_portal.close()
                    except Exception:
                        pass

            lines.append("\n=== 3. ENCRYPTED DNS (DoH) & ROUTING ===")
            
            t0 = time.time()
            try:
                dns_query = (
                    b"\xaa\xbb"
                    b"\x01\x00"
                    b"\x00\x01"
                    b"\x00\x00\x00\x00\x00\x00"
                    b"\x06google\x03com\x00"
                    b"\x00\x01"
                    b"\x00\x01"
                )
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(2.0)
                try:
                    s.sendto(dns_query, (gw, 53))
                    s.recv(512)
                finally:
                    s.close()
                ms = int((time.time() - t0) * 1000)
                lines.append(f"• Gateway UDP DNS (53):   PASS ({ms}ms)")
            except Exception:
                lines.append("• Gateway UDP DNS (53):   BLOCKED")

            t0 = time.time()
            # Bug 42 fix: Use configured DoH server endpoint
            doh_endpoint = self.core.config.get("doh_endpoint") or self.core.config.get("doh_server", "https://1.1.1.1/dns-query")
            doh_label = "Cloudflare DoH (1.1.1.1)" if "1.1.1.1" in doh_endpoint else f"Configured DoH ({doh_endpoint.split('//')[-1].split('/')[0]})"
            try:
                req_url = f"{doh_endpoint}?name=google.com" if "?" not in doh_endpoint else f"{doh_endpoint}&name=google.com"
                r = requests.get(req_url, 
                                 headers={"accept": "application/dns-json"}, 
                                 timeout=3, verify=False)
                ms = int((time.time() - t0) * 1000)
                # Validate response body actually contains DNS Answer to eliminate captive portal false positives
                if r.status_code == 200:
                    try:
                        doh_data = r.json()
                        if "Answer" in doh_data or doh_data.get("Status") == 0:
                            lines.append(f"• {doh_label}: PASS ({ms}ms)")
                        else:
                            lines.append(f"• {doh_label}: GATED (Non-DNS 200 Interception)")
                    except Exception:
                        lines.append(f"• {doh_label}: GATED (Invalid DNS JSON / Portal Intercept)")
                else:
                    lines.append(f"• {doh_label}: GATED (HTTP {r.status_code})")
            except Exception:
                lines.append(f"• {doh_label}: BLOCKED (Portal Interception Active)")

            lines.append("\n=== 4. MULTI-HOP LATENCY CHECK ===")
            targets = [
                ("Gateway (HTTP/80)", gw, 80),
                ("Portal Host", target_portal_host, portal_port),
                ("Cloudflare (HTTPS)", "1.1.1.1", 443),
                ("Google (HTTPS)", "8.8.8.8", 443)
            ]
            for target_name, target_ip, target_p in targets:
                t0 = time.time()
                s_hop = None
                try:
                    s_hop = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s_hop.settimeout(2.0)
                    s_hop.connect((target_ip, target_p))
                    ms = int((time.time() - t0) * 1000)
                    lines.append(f"• Latency to {target_name:20s} ({target_ip}:{target_p}): {ms}ms")
                except Exception:
                    lines.append(f"• Latency to {target_name:20s} ({target_ip}:{target_p}): TIMEOUT")
                finally:
                    if s_hop:
                        try:
                            s_hop.close()
                        except Exception:
                            pass

            lines.append(f"\n• Current Session Status: {self.core.status}")

            def _done():
                self.diag_box.insert(tk.END, "\n".join(lines) + "\n\n[✓] Diagnostic check completed.\n")
                self.diag_box.config(state=tk.NORMAL)
                self.diag_box.see(tk.END)
                if hasattr(self, "btn_diag"):
                    self.btn_diag.config(state=tk.NORMAL)

            self._tray_dispatch(_done)

        threading.Thread(target=_work, daemon=True).start()

    # --- SYSTEM TRAY ---
    def _tray_dispatch(self, fn: Callable, *args) -> None:
        """Safely schedule a callable on the Tkinter main thread via tray_action_queue (Bug 6)."""
        if args:
            self.tray_action_queue.put((fn, *args))
        else:
            self.tray_action_queue.put(fn)

    def _create_icon(self, color="red"):
        im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.ellipse([6, 6, 58, 58], fill=color)
        d.ellipse([20, 20, 44, 44], fill="white")
        d.ellipse([27, 27, 37, 37], fill=color)
        return im

    def _setup_tray_icon(self):
        if not HAS_PYSTRAY:
            self.tray = None
            return
        try:
            menu = pystray.Menu(
                item("Open GITwifi", lambda icon, it: self._tray_dispatch(self.restore_from_tray), default=True),
                item("Force Re-Probe", lambda icon, it: self._tray_dispatch(self._force_probe)),
                item("Logout", lambda icon, it: self._tray_dispatch(
                    lambda: threading.Thread(target=self.core.logout, daemon=True).start()
                )),
                pystray.Menu.SEPARATOR,
                item("Quit", lambda icon, it: self._tray_dispatch(self.quit_app))
            )
            self.tray = pystray.Icon("GITwifi", self._create_icon("red"), "GITwifi Engine", menu)
            threading.Thread(target=self.tray.run, daemon=True).start()
        except Exception as e:
            self.tray = None
            print(f"[Tray] System tray initialization warning: {e}")

    def _update_tray(self, st):
        c = "green" if st == "Connected" else ("orange" if "ing" in st.lower() else "red")
        if HAS_PYSTRAY and getattr(self, "tray", None):
            try:
                self.tray.icon = self._create_icon(c)
                self.tray.title = f"GITwifi: {st}"

                if self.core.config.get("desktop_notifications", True):
                    if st == "Connected" and self.last_notified_state != "Connected":
                        self.last_notified_state = "Connected"
                        self.tray.notify("You are connected to the network.", "GITwifi")
                    elif st != "Connected" and self.last_notified_state == "Connected":
                        # Bug 15: Only send "Disconnected" notification for terminal failure states
                        terminal_failure_states = {
                            "Disconnected", "Logged Out", "Login Rejected",
                            "Error", "Untrusted Portal", "Login Paused (Retries Exceeded)"
                        }
                        if st in terminal_failure_states:
                            self.last_notified_state = st
                            notify_msg = "Connection lost." if st == "Disconnected" else f"Disconnected: {st}"
                            self.tray.notify(notify_msg, "GITwifi")
            except Exception:
                pass

    def minimize_to_tray(self):
        if HAS_PYSTRAY and getattr(self, "tray", None):
            self.root.withdraw()
        else:
            self.root.iconify()

    def restore_from_tray(self):
        def _restore():
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
        self._tray_dispatch(_restore)

    def quit_app(self):
        self.live_mon_worker_running = False
        if hasattr(self, "live_mon_wake_event"):
            self.live_mon_wake_event.set()
        self.core.stop()
        if HAS_PYSTRAY and getattr(self, "tray", None):
            try:
                self.tray.stop()
            except Exception:
                pass
        self._tray_dispatch(self.root.destroy)

_SINGLE_INSTANCE_MUTEX = None

def _acquire_single_instance_lock() -> bool:
    """Ensure only one instance of GITwifi runs at a time using a named Win32 mutex."""
    global _SINGLE_INSTANCE_MUTEX
    try:
        import ctypes
        from ctypes import wintypes
        ERROR_ALREADY_EXISTS = 183
        mutex_name = "Local\\GITwifi_Suite_SingleInstanceMutex_Default"
        _SINGLE_INSTANCE_MUTEX = ctypes.windll.kernel32.CreateMutexW(None, wintypes.BOOL(False), mutex_name)
        last_err = ctypes.windll.kernel32.GetLastError()
        if last_err == ERROR_ALREADY_EXISTS:
            return False
        return True
    except Exception:
        return True

if __name__ == "__main__":
    if not _acquire_single_instance_lock():
        # Another instance is already running; exit gracefully without corrupting state
        try:
            # Try to bring the existing window to front if found
            import ctypes
            hwnd = ctypes.windll.user32.FindWindowW(None, "GITwifi - Clean Windows Suite")
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 9) # SW_RESTORE
                ctypes.windll.user32.SetForegroundWindow(hwnd)
        except Exception:
            pass
        sys.exit(0)

    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("GITwifi.Suite.App")
    except Exception:
        pass

    root = tk.Tk()
    app = GitWifiApp(root)
    root.mainloop()
