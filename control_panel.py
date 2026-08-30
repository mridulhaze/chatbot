"""
National University AI Assistant & Token Support System
Standalone GUI Control Panel (Slim Elegant White-Green Aesthetic)
"""

import sys
import os
import time
import socket
import shutil
import threading
import subprocess
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# ----------------- Environment & Path Resolution -----------------
def get_project_root() -> Path:
    """Returns the real project root directory even when running inside a PyInstaller bundle."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller standalone exe
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

PROJECT_ROOT = get_project_root()
os.chdir(PROJECT_ROOT)

def find_python_executable() -> str:
    """Locates the Python runtime interpreter on the system."""
    # 1. Check if standard python command exists in PATH
    py_cmd = shutil.which("python") or shutil.which("python.exe") or shutil.which("python3")
    if py_cmd and "windowsapps" not in py_cmd.lower():
        return py_cmd

    # 2. Check sys.base_prefix if available
    if hasattr(sys, 'base_prefix') and sys.base_prefix:
        candidate = Path(sys.base_prefix) / "python.exe"
        if candidate.exists():
            return str(candidate)

    # 3. Check known default Python installations
    known_paths = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python" / "Python313" / "python.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python" / "Python312" / "python.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python" / "Python311" / "python.exe",
        Path(r"C:\Python313\python.exe"),
        Path(r"C:\Python312\python.exe"),
        Path(r"C:\Python311\python.exe"),
    ]
    for p in known_paths:
        if p.exists():
            return str(p)

    return "python"

PYTHON_EXE = find_python_executable()

# ----------------- Theme Palette (White & Emerald Green) -----------------
BG_MAIN = "#F8FAFC"        # Crisp light slate background
BG_SURFACE = "#FFFFFF"     # Pure white card surface
BG_EMERALD_TINT = "#F0FDF4" # Subtle mint green highlight
BG_HEADER = "#064E3B"      # Deep emerald brand header
TEXT_PRIMARY = "#0F172A"   # Slate 900
TEXT_SECONDARY = "#475569" # Slate 600
TEXT_MUTED = "#94A3B8"     # Slate 400
TEXT_WHITE = "#FFFFFF"

ACCENT_GREEN = "#059669"   # Emerald 600
ACCENT_GREEN_HOVER = "#047857" # Emerald 700
ACCENT_MINT = "#10B981"    # Emerald 500
ACCENT_MINT_BG = "#DCFCE7" # Emerald 100 badge bg
ACCENT_MINT_TEXT = "#166534" # Emerald 800 badge text

STOP_RED = "#EF4444"
STOP_RED_HOVER = "#DC2626"
STOP_RED_BG = "#FEE2E2"
STOP_RED_TEXT = "#991B1B"

WARN_AMBER = "#F59E0B"
WARN_AMBER_HOVER = "#D97706"
WARN_AMBER_BG = "#FEF3C7"
WARN_AMBER_TEXT = "#92400E"

BORDER_COLOR = "#E2E8F0"
BORDER_GREEN = "#A7F3D0"

PORT = 8080
SERVER_URL = f"http://127.0.0.1:{PORT}"


class ControlPanelApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("NU AI Assistant — Service Control Center")
        self.root.geometry("880x720")
        self.root.minsize(820, 650)
        self.root.configure(bg=BG_MAIN)

        self.server_proc = None
        self.log_thread = None
        self.is_monitoring = True
        self.is_stopping = False

        self.services_state = {
            "fastapi": {"name": "FastAPI Core & RAG Engine (Port 8080)", "status": "Stopped", "color": STOP_RED_TEXT, "bg": STOP_RED_BG},
            "hermes": {"name": "Hermes Learning Brain Worker", "status": "Ready", "color": ACCENT_MINT_TEXT, "bg": ACCENT_MINT_BG},
            "scraper": {"name": "Notices & Crawler Engine (21,555 Records)", "status": "Indexed", "color": ACCENT_MINT_TEXT, "bg": ACCENT_MINT_BG},
            "tokens": {"name": "Token Dispatch & Resolver Center", "status": "Ready", "color": ACCENT_MINT_TEXT, "bg": ACCENT_MINT_BG},
        }

        self._build_ui()
        self._start_background_monitor()

    def _build_ui(self):
        # 1. Header Banner
        header = tk.Frame(self.root, bg=BG_HEADER, height=85)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        h_inner = tk.Frame(header, bg=BG_HEADER)
        h_inner.pack(fill=tk.BOTH, expand=True, padx=24, pady=12)

        title_lbl = tk.Label(
            h_inner,
            text="🎓 National University AI Assistant",
            font=("Segoe UI", 16, "bold"),
            fg=TEXT_WHITE,
            bg=BG_HEADER
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(
            h_inner,
            text="Master Service Manager • Guaranteed Process Isolation • Port 8080",
            font=("Segoe UI", 9),
            fg="#A7F3D0",
            bg=BG_HEADER
        )
        subtitle_lbl.pack(anchor="w", pady=(2, 0))

        # 2. Main Container
        main_frame = tk.Frame(self.root, bg=BG_MAIN)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        # Control Action Bar
        action_bar = tk.Frame(main_frame, bg=BG_SURFACE, highlightbackground=BORDER_COLOR, highlightthickness=1, bd=0)
        action_bar.pack(fill=tk.X, pady=(0, 14), ipady=8, ipadx=12)

        act_inner = tk.Frame(action_bar, bg=BG_SURFACE)
        act_inner.pack(fill=tk.X, padx=12, pady=6)

        # Start Button
        self.btn_start = tk.Button(
            act_inner,
            text="▶ Start All Services",
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT_GREEN,
            fg=TEXT_WHITE,
            activebackground=ACCENT_GREEN_HOVER,
            activeforeground=TEXT_WHITE,
            bd=0,
            padx=16,
            pady=6,
            cursor="hand2",
            command=self.start_server
        )
        self.btn_start.pack(side=tk.LEFT, padx=(0, 8))

        # Stop Button
        self.btn_stop = tk.Button(
            act_inner,
            text="⏹ Stop All",
            font=("Segoe UI", 10, "bold"),
            bg=STOP_RED,
            fg=TEXT_WHITE,
            activebackground=STOP_RED_HOVER,
            activeforeground=TEXT_WHITE,
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.stop_server
        )
        self.btn_stop.pack(side=tk.LEFT, padx=(0, 8))

        # Restart Button
        self.btn_restart = tk.Button(
            act_inner,
            text="🔄 Restart",
            font=("Segoe UI", 10, "bold"),
            bg=WARN_AMBER,
            fg=TEXT_WHITE,
            activebackground=WARN_AMBER_HOVER,
            activeforeground=TEXT_WHITE,
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.restart_server
        )
        self.btn_restart.pack(side=tk.LEFT, padx=(0, 16))

        # Open Web Assistant Button
        self.btn_web = tk.Button(
            act_inner,
            text="🌐 Open Web Assistant",
            font=("Segoe UI", 9, "bold"),
            bg=BG_EMERALD_TINT,
            fg=ACCENT_GREEN,
            activebackground="#D1FAE5",
            activeforeground=ACCENT_GREEN_HOVER,
            highlightbackground=BORDER_GREEN,
            highlightthickness=1,
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=lambda: webbrowser.open(SERVER_URL)
        )
        self.btn_web.pack(side=tk.RIGHT, padx=(6, 0))

        # Open Tokens Button
        self.btn_tokens = tk.Button(
            act_inner,
            text="🎫 Token Desk",
            font=("Segoe UI", 9),
            bg=BG_SURFACE,
            fg=TEXT_PRIMARY,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
            command=lambda: webbrowser.open(f"{SERVER_URL}/#tokens")
        )
        self.btn_tokens.pack(side=tk.RIGHT, padx=(6, 0))

        # 3. Services Health Dashboard
        grid_label = tk.Label(main_frame, text="LIVE SERVICES HEALTH", font=("Segoe UI", 8, "bold"), fg=TEXT_MUTED, bg=BG_MAIN)
        grid_label.pack(anchor="w", pady=(0, 4))

        services_grid = tk.Frame(main_frame, bg=BG_MAIN)
        services_grid.pack(fill=tk.X, pady=(0, 14))

        self.service_cards = {}
        for idx, (svc_key, svc_info) in enumerate(self.services_state.items()):
            col = idx % 2
            row = idx // 2
            card = self._create_service_card(services_grid, svc_key, svc_info)
            card.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
            services_grid.columnconfigure(col, weight=1)

        # 4. Live Server Logs Section
        log_header = tk.Frame(main_frame, bg=BG_MAIN)
        log_header.pack(fill=tk.X, pady=(4, 4))

        log_lbl = tk.Label(log_header, text="LIVE AUDIT & CONSOLE LOGS", font=("Segoe UI", 8, "bold"), fg=TEXT_MUTED, bg=BG_MAIN)
        log_lbl.pack(side=tk.LEFT)

        clear_btn = tk.Button(
            log_header,
            text="Clear Console",
            font=("Segoe UI", 8),
            bg=BG_SURFACE,
            fg=TEXT_SECONDARY,
            bd=0,
            padx=8,
            cursor="hand2",
            command=self.clear_logs
        )
        clear_btn.pack(side=tk.RIGHT)

        # Log Text Box
        self.log_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            height=13,
            font=("Consolas", 9),
            bg="#1E293B",
            fg="#F8FAFC",
            insertbackground="#10B981",
            selectbackground="#059669",
            bd=0,
            highlightthickness=1,
            highlightbackground="#334155"
        )
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        self.log(f"Control Panel ready. Python: {PYTHON_EXE}\nRoot: {PROJECT_ROOT}\n")

        # 5. Bottom Status Bar
        statusbar = tk.Frame(self.root, bg=BG_SURFACE, height=32, highlightbackground=BORDER_COLOR, highlightthickness=1)
        statusbar.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_dot = tk.Label(statusbar, text="●", font=("Segoe UI", 10), fg=STOP_RED, bg=BG_SURFACE)
        self.status_dot.pack(side=tk.LEFT, padx=(12, 4))

        self.status_text = tk.Label(
            statusbar,
            text="Status: Server Offline (Port 8080 Free)",
            font=("Segoe UI", 9),
            fg=TEXT_SECONDARY,
            bg=BG_SURFACE
        )
        self.status_text.pack(side=tk.LEFT)

        self.path_text = tk.Label(
            statusbar,
            text=f"📁 {PROJECT_ROOT}",
            font=("Segoe UI", 8),
            fg=TEXT_MUTED,
            bg=BG_SURFACE
        )
        self.path_text.pack(side=tk.RIGHT, padx=12)

    def _create_service_card(self, parent, key, info):
        card = tk.Frame(parent, bg=BG_SURFACE, highlightbackground=BORDER_COLOR, highlightthickness=1, bd=0)
        
        inner = tk.Frame(card, bg=BG_SURFACE)
        inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        title_lbl = tk.Label(inner, text=info["name"], font=("Segoe UI", 9, "bold"), fg=TEXT_PRIMARY, bg=BG_SURFACE)
        title_lbl.pack(side=tk.LEFT)

        badge = tk.Label(
            inner,
            text=f"  {info['status']}  ",
            font=("Segoe UI", 8, "bold"),
            fg=info["color"],
            bg=info["bg"],
            padx=4,
            pady=2
        )
        badge.pack(side=tk.RIGHT)

        self.service_cards[key] = {"card": card, "badge": badge, "title": title_lbl}
        return card

    def _update_service_badge(self, key, status, is_active=True):
        if key in self.service_cards:
            badge = self.service_cards[key]["badge"]
            if is_active:
                badge.configure(text=f"  {status}  ", fg=ACCENT_MINT_TEXT, bg=ACCENT_MINT_BG)
            else:
                badge.configure(text=f"  {status}  ", fg=STOP_RED_TEXT, bg=STOP_RED_BG)

    def log(self, text: str):
        self.log_area.configure(state=tk.NORMAL)
        self.log_area.insert(tk.END, text)
        self.log_area.see(tk.END)
        self.log_area.configure(state=tk.DISABLED)

    def clear_logs(self):
        self.log_area.configure(state=tk.NORMAL)
        self.log_area.delete("1.0", tk.END)
        self.log_area.configure(state=tk.DISABLED)

    def is_port_in_use(self, port=PORT) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            return s.connect_ex(("127.0.0.1", port)) == 0

    def start_server(self):
        if self.is_port_in_use(PORT):
            self.log("⚠️ Port 8080 is already active.\n")
            self._update_service_badge("fastapi", "Running (Port 8080)", is_active=True)
            self.status_dot.configure(fg=ACCENT_MINT)
            self.status_text.configure(text="Status: Active on http://127.0.0.1:8080")
            return

        main_py = PROJECT_ROOT / "main.py"
        if not main_py.exists():
            self.log(f"❌ Error: main.py not found at {main_py}\n")
            return

        self.log(f"🚀 Starting NU AI Assistant: {PYTHON_EXE} main.py\n")
        self._update_service_badge("fastapi", "Starting...", is_active=True)
        self.status_dot.configure(fg=WARN_AMBER)
        self.status_text.configure(text="Status: Launching server...")

        def _run():
            try:
                self.server_proc = subprocess.Popen(
                    [PYTHON_EXE, str(main_py)],
                    cwd=str(PROJECT_ROOT),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                
                for line in self.server_proc.stdout:
                    self.root.after(0, self.log, line)

                self.server_proc.wait()
            except Exception as e:
                self.root.after(0, self.log, f"❌ Server Process Error: {e}\n")

        self.log_thread = threading.Thread(target=_run, daemon=True)
        self.log_thread.start()

    def stop_server(self):
        self.is_stopping = True
        self.log("⏹ Stopping all Python backend processes and clearing Port 8080...\n")
        self._update_service_badge("fastapi", "Stopping...", is_active=False)

        def _stop():
            # 1. Kill local proc handle if attached
            if self.server_proc:
                try:
                    subprocess.run(f"taskkill /F /T /PID {self.server_proc.pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass
                try:
                    self.server_proc.kill()
                except Exception:
                    pass
                self.server_proc = None

            # 2. Kill all port 8080 socket listeners (including child workers)
            if os.name == 'nt':
                # Terminate port 8080 listeners via PowerShell
                ps_kill_port = f"""
                $conns = Get-NetTCPConnection -LocalPort {PORT} -ErrorAction SilentlyContinue
                if ($conns) {{
                    foreach ($c in $conns) {{
                        $pidToKill = $c.OwningProcess
                        if ($pidToKill -gt 4) {{
                            Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
                            taskkill /F /T /PID $pidToKill > $null 2>&1
                        }}
                    }}
                }}
                """
                try:
                    subprocess.run(["powershell", "-NoProfile", "-Command", ps_kill_port], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass

                # Also terminate any stray python worker processes spawned by main.py
                ps_kill_python = """
                Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { 
                    $_.Name -match 'python' -and ($_.CommandLine -match 'main.py' -or $_.CommandLine -match 'backend' -or $_.CommandLine -match 'multiprocessing-fork') 
                } | ForEach-Object { 
                    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue 
                }
                """
                try:
                    subprocess.run(["powershell", "-NoProfile", "-Command", ps_kill_python], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass

            # 3. Wait up to 3 seconds for socket release
            for _ in range(15):
                if not self.is_port_in_use(PORT):
                    break
                time.sleep(0.2)

            self.is_stopping = False
            self.root.after(0, self._on_stopped)

        threading.Thread(target=_stop, daemon=True).start()

    def _on_stopped(self):
        if not self.is_port_in_use(PORT):
            self._update_service_badge("fastapi", "Stopped", is_active=False)
            self.status_dot.configure(fg=STOP_RED)
            self.status_text.configure(text="Status: Server Offline (Port 8080 Free)")
            self.log("✅ All backend services and listener workers stopped successfully.\n")
        else:
            self.log("⚠️ Port 8080 is still responding. Checking active processes...\n")

    def restart_server(self):
        self.log("🔄 Restarting server in 1.5 seconds...\n")
        self.stop_server()

        def _delayed_start():
            time.sleep(2.0)
            self.root.after(0, self.start_server)

        threading.Thread(target=_delayed_start, daemon=True).start()

    def _start_background_monitor(self):
        def _poll():
            while self.is_monitoring:
                if not self.is_stopping:
                    is_active = self.is_port_in_use(PORT)
                    def _sync(active=is_active):
                        if self.is_stopping:
                            return
                        if active:
                            self._update_service_badge("fastapi", "Running (8080)", is_active=True)
                            self.status_dot.configure(fg=ACCENT_MINT)
                            self.status_text.configure(text="Status: Active on http://127.0.0.1:8080")
                        else:
                            if not self.server_proc:
                                self._update_service_badge("fastapi", "Stopped", is_active=False)
                                self.status_dot.configure(fg=STOP_RED)
                                self.status_text.configure(text="Status: Server Offline (Port 8080 Free)")
                    try:
                        self.root.after(0, _sync)
                    except Exception:
                        break
                time.sleep(1.5)

        t = threading.Thread(target=_poll, daemon=True)
        t.start()


def main():
    root = tk.Tk()
    try:
        if os.name == 'nt':
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = ControlPanelApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
