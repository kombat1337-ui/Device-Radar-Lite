# Device-Radar-Lite

A lightweight real-time network scanner and “trolling” tool with a simple full-screen radar GUI.
## ⚙️ Features

- **ARP-based host discovery** via Scapy’s `arping`  
- **Full-screen radar animation** with rotating sweep  
- **Clickable device dots** colored by guessed OS (Windows, Apple, Android, Unknown)  
- **Tooltips on hover** showing hostname, IP, MAC and OS  
- **Manual subnet entry** (CIDR notation) with validation  
- **Custom UDP “troll” messages** sent to multiple ports  
- **Configurable scan interval** (default 30 s)  
- **Debug logging** to console for easy troubleshooting  

---

## 📋 Requirements

- Python 3.7+  
- [Scapy](https://scapy.net/)  
- `utils/network_utils.py` utility (must provide `get_local_subnet()`)

pip install scapy
 Usage:
Clone or copy device_radar_custom.py and the utils/network_utils.py into the same folder.
Install dependencies:
pip install scapy
Run.


Controls:
Escape or click the window’s close button to exit full-screen / quit
Set Subnet: enter your LAN CIDR (e.g. 192.168.1.0/24) and click Set
Troll msg: type a custom message and click Troll after selecting a device
Click any dot on the radar to select a host (enables the Troll button)


🔧 Configuration
DEFAULT_SUBNET in the code is determined by get_local_subnet(). You can override it on-screen.
SCAN_INTERVAL (seconds between scans): default 30 s—change in the source.
TROLL_PORTS: list of UDP ports to probe for trolling. Default: [1900, 5353, 5555, 137].
OS_COLORS: mapping of guessed OS names to radar dot colors.

Disclaimer: Use only on networks you own or have permission to test. Unauthorized network scanning or spoofing may be illegal.
