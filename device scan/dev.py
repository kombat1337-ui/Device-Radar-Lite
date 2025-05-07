"""
device_radar_custom.py

Real-Time Device Radar with enhanced GUI and reliable ARP scanning:
 - Manual subnet selection
 - ARP scanning via scapy.arping for reliable interface detection
 - Debug logs for interface, arping results
 - Clickable device dots colored by OS
 - Customizable troll message input
 - Tooltips on hover
"""

import threading
import time
import socket
import math
import random
import tkinter as tk
from tkinter import ttk, messagebox
import ipaddress
from scapy.all import ARP, Ether, srp, conf, arping

# Utility for getting local subnet
from utils.network_utils import get_local_subnet

# === Configuration ===
DEFAULT_SUBNET = get_local_subnet()
SCAN_INTERVAL = 30
TROLL_PORTS   = [1900, 5353, 5555, 137]
OS_COLORS = {
    'Windows': 'blue',
    'Apple':   'gray',
    'Android': 'green',
    'Unknown': 'white'
}

print(f"[DEBUG] Initial subnet: {DEFAULT_SUBNET}")
print(f"[DEBUG] Scapy default iface: {conf.iface}")

# === Tooltip helper ===
class ToolTip:
    def __init__(self, widget, text=''):
        self.widget = widget
        self.text   = text
        self.tip    = None

    def show(self, x, y):
        if self.tip or not self.text:
            return
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(self.tip, text=self.text,
                       bg='yellow', fg='black', font=('Consolas', 10))
        lbl.pack()

    def hide(self):
        if self.tip:
            self.tip.destroy()
            self.tip = None

# === Main Application ===
class DeviceRadarApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Device Radar Custom")
        self.configure(bg="#111")
        self.attributes('-fullscreen', True)
        self.bind("<Escape>", lambda e: self.toggle_fullscreen())
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Style
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TButton', font=('Arial', 12), padding=5)

        # --- Control Frame ---
        ctrl = ttk.Frame(self, padding=10)
        ctrl.pack(fill='x')

        ttk.Label(ctrl, text="Subnet:", foreground='white', background='#111').pack(side='left')
        self.subnet_var = tk.StringVar(value=DEFAULT_SUBNET)
        self.subnet_entry = ttk.Entry(ctrl, textvariable=self.subnet_var, width=20)
        self.subnet_entry.pack(side='left', padx=5)
        ttk.Button(ctrl, text="Set", command=self.update_subnet).pack(side='left', padx=(0,20))

        ttk.Label(ctrl, text="Devices:", foreground='white', background='#111').pack(side='left')
        self.info_label = ttk.Label(ctrl, text="…", foreground='lime', background='#111')
        self.info_label.pack(side='left', padx=(5,20))

        ttk.Label(ctrl, text="Troll msg:", foreground='white', background='#111').pack(side='left')
        self.msg_entry = ttk.Entry(ctrl, width=30)
        self.msg_entry.insert(0, "You have been spotted 😈")
        self.msg_entry.pack(side='left', padx=5)
        self.troll_btn = ttk.Button(ctrl, text="Troll", command=self.troll_selected, state='disabled')
        self.troll_btn.pack(side='left', padx=5)

        # --- Radar Canvas ---
        self.canvas = tk.Canvas(self, bg='#222')
        self.canvas.pack(fill='both', expand=True)
        self.width, self.height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.center = (self.width//2, self.height//2)
        self.radius = min(self.center) - 100
        self.scan_angle = 0

        # Data
        self.devices = []
        self.tooltips = {}
        self.selected = None

        # Initial scan + start threads
        self.scan_network()
        conf.verb = 0
        self.running = True
        threading.Thread(target=self.scan_loop, daemon=True).start()
        self.animate()

    def update_subnet(self):
        val = self.subnet_var.get().strip()
        try:
            ipaddress.IPv4Network(val, strict=False)
            global DEFAULT_SUBNET
            DEFAULT_SUBNET = val
            self.info_label.config(text="Subnet set")
            print(f"[DEBUG] Subnet manually set to: {val}")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid subnet: {e}")

    def toggle_fullscreen(self):
        fs = not self.attributes('-fullscreen')
        self.attributes('-fullscreen', fs)

    def on_close(self):
        self.running = False
        self.destroy()

    def scan_loop(self):
        while self.running:
            self.scan_network()
            time.sleep(SCAN_INTERVAL)

    def scan_network(self):
        subnet = self.subnet_var.get()
        print(f"[DEBUG] ARP scanning {subnet} using arping...")
        try:
            ans, _ = arping(subnet, timeout=3, verbose=False)
        except Exception as e:
            print(f"[ERROR] arping failed: {e}")
            ans = []
        print(f"[DEBUG] arping responses: {len(ans)}")

        found = []
        for snd, r in ans:
            ip, mac = r.psrc, r.hwsrc
            print(f"[DEBUG] {ip} @ {mac}")
            try:
                host = socket.gethostbyaddr(ip)[0]
            except:
                host = ip
            vendor = mac.upper().replace(':','')[:6]
            os_guess = 'Unknown'
            if vendor.startswith('5C1F'): os_guess='Apple'
            elif vendor.startswith('FCFB'): os_guess='Windows'
            elif vendor.startswith('A1B2'): os_guess='Android'
            found.append({'ip':ip, 'mac':mac, 'host':host, 'os':os_guess})

        # Update device list
        self.devices.clear()
        self.tooltips.clear()
        self.troll_btn.state(['disabled'])
        for d in found:
            ang  = random.uniform(0, 2*math.pi)
            dist = random.uniform(50, self.radius)
            x = self.center[0] + dist*math.cos(ang)
            y = self.center[1] + dist*math.sin(ang)
            d.update({'x':x, 'y':y})
            self.devices.append(d)

        self.info_label.config(text=f"{len(self.devices)} devices found")

    def draw_radar(self):
        self.canvas.delete('all')
        # Concentric circles
        for r in range(100, self.radius+1, 100):
            self.canvas.create_oval(
                self.center[0]-r, self.center[1]-r,
                self.center[0]+r, self.center[1]+r,
                outline='#444'
            )
        # Scan line
        ang = math.radians(self.scan_angle)
        x2 = self.center[0] + self.radius*math.cos(ang)
        y2 = self.center[1] + self.radius*math.sin(ang)
        self.canvas.create_line(self.center[0], self.center[1], x2, y2,
                                fill='lime', width=3)

        # Draw devices
        for d in self.devices:
            color = OS_COLORS.get(d['os'], 'white')
            dot = self.canvas.create_oval(
                d['x']-8, d['y']-8,
                d['x']+8, d['y']+8,
                fill=color, outline=''
            )
            self.canvas.tag_bind(dot, '<Button-1>', lambda e, dev=d: self.on_select(dev))
            tip_text = f"{d['host']}\n{d['ip']}\n{d['mac']}\nOS: {d['os']}"
            tip = ToolTip(self.canvas, text=tip_text)
            self.tooltips[dot] = tip
            self.canvas.tag_bind(dot, '<Enter>', lambda e, t=tip: t.show(e.x_root+10, e.y_root+10))
            self.canvas.tag_bind(dot, '<Leave>', lambda e, t=tip: t.hide())

    def animate(self):
        self.scan_angle = (self.scan_angle + 3) % 360
        self.draw_radar()
        self.after(50, self.animate)

    def on_select(self, dev):
        """Handle selection: update label and enable troll."""
        self.selected = dev
        self.info_label.config(text=f"Selected: {dev['host']} ({dev['ip']})")
        self.troll_btn.state(['!disabled'])

    def troll_selected(self):
        """Send UDP troll message to selected device and report status."""
        if not self.selected:
            return
        msg = self.msg_entry.get().encode('utf-8')
        ip = self.selected['ip']
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        results = []
        for p in TROLL_PORTS:
            try:
                sock.sendto(msg, (ip, p))
                results.append((p, True))
            except Exception:
                results.append((p, False))
        # Build report
        report = f"Troll sent to {self.selected['host']} ({ip})\n"
        success_ports = [str(p) for p, ok in results if ok]
        fail_ports    = [str(p) for p, ok in results if not ok]
        if success_ports:
            report += "Succeeded on ports: " + ", ".join(success_ports) + "\n"
        if fail_ports:
            report += "Failed on ports: " + ", ".join(fail_ports)
        # Update label and show dialog
        self.info_label.config(text=f"Last troll: {self.selected['host']} ({ip})")
        messagebox.showinfo("Troll Report", report)

if __name__ == '__main__':
    app = DeviceRadarApp()
    app.mainloop()
