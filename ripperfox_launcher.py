import sys
import os
import threading
import json
import appdirs
from PIL import Image, ImageDraw
import pystray

def create_tray_icon():
    base_dir = os.path.dirname(__file__)
    
    # For PyInstaller, we need to handle the bundled resources
    if getattr(sys, 'frozen', False):
        # Running as compiled exe - use the MEIPASS location if available
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
    
    icon_path = os.path.join(base_dir, "icon.ico")
    
    try:
        if os.path.exists(icon_path):
            image = Image.open(icon_path)
            print(f"[SYSTEM] Loaded icon: {icon_path}")
            return image
    except Exception as e:
        print(f"[WARNING] Could not load icon: {e}")
    
    # Fallback icon
    image = Image.new('RGB', (64, 64), color='white')
    dc = ImageDraw.Draw(image)
    dc.rectangle((16, 16, 48, 48), fill='blue')
    return image

def show_window(icon, item):
    import ctypes
    console_window = ctypes.windll.kernel32.GetConsoleWindow()
    if console_window:
        ctypes.windll.user32.ShowWindow(console_window, 1)
        ctypes.windll.user32.SetForegroundWindow(console_window)

def hide_window(icon, item):
    import ctypes
    console_window = ctypes.windll.kernel32.GetConsoleWindow()
    if console_window:
        ctypes.windll.user32.ShowWindow(console_window, 0)

def exit_app(icon, item):
    icon.stop()
    os._exit(0)


def update_yt_dlp(icon, item):
    """Request the backend to update yt-dlp and poll for status"""
    try:
        import requests
    except Exception as e:
        print(f"[UPDATE] Requests not available: {e}. Falling back to local updater.")
        try:
            from ytdlp_updater import download_latest_ytdlp
            if download_latest_ytdlp():
                print("[UPDATE] yt-dlp updated successfully (local)")
            else:
                print("[UPDATE] Local update failed")
        except Exception as ee:
            print(f"[UPDATE] Local update failed: {ee}")
        return

    def _worker():
        try:
            resp = requests.post("http://127.0.0.1:5100/api/update-yt-dlp", timeout=5)
            if resp.ok:
                print("[UPDATE] Update requested")
                # Poll status
                import time
                while True:
                    time.sleep(1)
                    s = requests.get("http://127.0.0.1:5100/api/update-status", timeout=5).json()
                    status = s.get("status")
                    msg = s.get("message")
                    print(f"[UPDATE] {status}: {msg}")
                    if status in ("succeeded", "failed", "idle"):
                        break
            else:
                print(f"[UPDATE] Update request failed: {resp.status_code} {resp.text}")
        except Exception as e:
            print(f"[UPDATE] Could not contact backend: {e}. Falling back to local updater.")
            try:
                from ytdlp_updater import download_latest_ytdlp
                if download_latest_ytdlp():
                    print("[UPDATE] yt-dlp updated successfully (local)")
                else:
                    print("[UPDATE] Local update failed")
            except Exception as ee:
                print(f"[UPDATE] Local update failed: {ee}")

    import threading
    threading.Thread(target=_worker, daemon=True).start()

def setup_tray_icon():
    image = create_tray_icon()
    
    menu = pystray.Menu(
        pystray.MenuItem('Show Console', show_window),
        pystray.MenuItem('Hide Console', hide_window),
        pystray.MenuItem('Autostart', toggle_autostart, checked=lambda item: is_autostart_enabled()),
        pystray.MenuItem('Update yt-dlp', update_yt_dlp),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Exit', exit_app)
    )
    
    icon = pystray.Icon("RipperFox", image, "RipperFox Backend", menu)
    return icon

def start_backend():
    """Start the Flask backend with proper path handling"""
    try:
        # Add the local site-packages to path (for PyInstaller)
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
        else:
            # Running as script
            base_dir = os.path.dirname(__file__)
        
        local_site = os.path.join(base_dir, "python", "Lib", "site-packages")
        if os.path.isdir(local_site) and local_site not in sys.path:
            sys.path.insert(0, local_site)

        # Ensure working directory is the appdata dir so any relative paths resolve to a writable location
        data_dir = get_appdata_dir()
        try:
            os.chdir(data_dir)
            print(f"[SYSTEM] Changed working dir to: {data_dir}")
        except Exception as e:
            print(f"[WARNING] Could not change working directory to {data_dir}: {e}")
        
        from yt_backend import app
        print("[SYSTEM] Starting Flask backend on port 5100...")
        threading.Thread(target=lambda: app.run(port=5100, debug=False, use_reloader=False), daemon=True).start()
        # If ytdlp_updater supports auto_update_check, start it in background
        try:
            from ytdlp_updater import auto_update_check
            threading.Thread(target=auto_update_check, daemon=True).start()
        except Exception:
            pass
    except Exception as e:
        print(f"[ERROR] Failed to start backend: {e}")


def get_appdata_dir():
    """Return the application data directory for RipperFox.
    When running as an executable, use appdirs.user_data_dir to match the backend.
    Otherwise return the project directory.
    """
    if getattr(sys, 'frozen', False):
        data_dir = appdirs.user_data_dir("RipperFox", "RipperFox")
    else:
        data_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_settings_path():
    return os.path.join(get_appdata_dir(), "settings.json")


def load_settings():
    path = get_settings_path()
    default = {"autostart": False}
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                default.update(data)
        else:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(default, f, indent=2)
    except Exception as e:
        print(f"[WARNING] Failed to read settings.json: {e}")
    return default


def save_settings(data):
    path = get_settings_path()
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[WARNING] Failed to save settings.json: {e}")


def startup_entry_path():
    """Return the path for the startup VBS file in the user's Startup folder."""
    startup_folder = os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    os.makedirs(startup_folder, exist_ok=True)
    entry_name = "RipperFox Startup.vbs"
    return os.path.join(startup_folder, entry_name)


def is_autostart_enabled():
    settings = load_settings()
    # Also check for presence of the startup file
    entry = startup_entry_path()
    if settings.get("autostart", False) and os.path.exists(entry):
        return True
    return False


def set_autostart(enabled: bool):
    settings = load_settings()
    settings["autostart"] = bool(enabled)
    save_settings(settings)
    return settings


def create_startup_entry():
    entry = startup_entry_path()
    # Build the command to execute at startup (VBS that runs hidden)
    if getattr(sys, 'frozen', False):
        target = f'{sys.executable}'
    else:
        # When running as script, call the Python interpreter with the script
        target = f'{sys.executable} "{os.path.abspath(__file__)}"'

    # Escape internal quotes for VB string literal
    safe_target = target.replace('"', '""')
    vbs_content = (
        'Set WshShell = CreateObject("WScript.Shell")\n'
        f'WshShell.Run "{safe_target}", 0, False\n'
    )

    try:
        # Remove any old .cmd entry if present (cleanup)
        cmd_entry = os.path.join(os.path.dirname(entry), "RipperFox Startup.cmd")
        if os.path.exists(cmd_entry):
            try:
                os.remove(cmd_entry)
            except Exception:
                pass

        with open(entry, 'w', encoding='utf-8') as f:
            f.write(vbs_content)
        # Persist autostart setting for consistency
        set_autostart(True)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create startup entry: {e}")
        return False


def remove_startup_entry():
    entry = startup_entry_path()
    try:
        # Remove VBS entry if present
        if os.path.exists(entry):
            os.remove(entry)
        # Also try removing legacy .cmd entry
        cmd_entry = os.path.join(os.path.dirname(entry), "RipperFox Startup.cmd")
        if os.path.exists(cmd_entry):
            try:
                os.remove(cmd_entry)
            except Exception:
                pass
        # Persist autostart setting for consistency
        set_autostart(False)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to remove startup entry: {e}")
        return False


def toggle_autostart(icon, item):
    current = is_autostart_enabled()
    if current:
        if remove_startup_entry():
            set_autostart(False)
            print("[SYSTEM] Autostart disabled")
            try:
                icon.update_menu()
            except Exception:
                pass
    else:
        if create_startup_entry():
            set_autostart(True)
            print("[SYSTEM] Autostart enabled")
            try:
                icon.update_menu()
            except Exception:
                pass

if __name__ == "__main__":
    # Hide console window as early as possible to avoid visible popup on autostart
    import ctypes
    console_window = ctypes.windll.kernel32.GetConsoleWindow()
    if console_window:
        ctypes.windll.user32.ShowWindow(console_window, 0)

    # Start the backend
    start_backend()
    
    # Setup and run tray icon
    icon = setup_tray_icon()
    
    print("[SYSTEM] RipperFox is running in system tray. Right-click the icon for options.")
    icon.run()