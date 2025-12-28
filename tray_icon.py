import sys
import os
import threading
from PIL import Image, ImageDraw
import pystray

def create_tray_icon():
    base_dir = os.path.dirname(__file__)
    
    # Look for icon in the root folder first, then subfolder as fallback
    icon_paths = [
        os.path.join(base_dir, "icon.ico"),               # Root folder
        os.path.join(base_dir, "RipperFox", "icon.ico"),  # Your current location
    ]
    
    for icon_path in icon_paths:
        try:
            if os.path.exists(icon_path):
                image = Image.open(icon_path)
                print(f"[SYSTEM] Loaded icon: {icon_path}")
                return image
        except Exception as e:
            print(f"[WARNING] Could not load {icon_path}: {e}")
            continue
    
    print("[INFO] Using default icon - no custom icon files found")
    return create_default_icon()

def create_default_icon():
    """Fallback to default icon if custom one fails"""
    image = Image.new('RGB', (64, 64), color='white')
    dc = ImageDraw.Draw(image)
    dc.rectangle((16, 16, 48, 48), fill='blue')
    return image

def show_window(icon, item):
    """Bring the console window to foreground"""
    import ctypes
    console_window = ctypes.windll.kernel32.GetConsoleWindow()
    if console_window:
        ctypes.windll.user32.ShowWindow(console_window, 1)  # SW_SHOWNORMAL
        ctypes.windll.user32.SetForegroundWindow(console_window)

def hide_window(icon, item):
    """Hide the console window"""
    import ctypes
    console_window = ctypes.windll.kernel32.GetConsoleWindow()
    if console_window:
        ctypes.windll.user32.ShowWindow(console_window, 0)  # SW_HIDE

def exit_app(icon, item):
    """Exit the application"""
    icon.stop()
    os._exit(0)

def update_yt_dlp(icon, item):
    """Trigger backend update and stream status to console"""
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
        pystray.MenuItem('Update yt-dlp', update_yt_dlp),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Exit', exit_app)
    )
    
    icon = pystray.Icon("RipperFox", image, "RipperFox Backend", menu)
    return icon

def start_backend():
    """Start the Flask backend"""
    try:
        # Change working directory to appdata when running as frozen so relative paths are writable
        try:
            if getattr(sys, 'frozen', False):
                import appdirs
                data_dir = appdirs.user_data_dir("RipperFox", "RipperFox")
                os.makedirs(data_dir, exist_ok=True)
                try:
                    os.chdir(data_dir)
                    print(f"[SYSTEM] Changed working dir to: {data_dir}")
                except Exception as e:
                    print(f"[WARNING] Could not change working directory to {data_dir}: {e}")
        except Exception:
            pass

        from yt_backend import app
        print("[SYSTEM] Starting Flask backend on port 5100...")
        # Run in a separate thread to avoid blocking
        threading.Thread(target=lambda: app.run(port=5100, debug=False, use_reloader=False), daemon=True).start()
    except Exception as e:
        print(f"[ERROR] Failed to start backend: {e}")

if __name__ == "__main__":
    # Hide console window as early as possible
    import ctypes
    console_window = ctypes.windll.kernel32.GetConsoleWindow()
    if console_window:
        ctypes.windll.user32.ShowWindow(console_window, 0)  # SW_HIDE

    # Start the backend first
    start_backend()
    
    # Then start the tray icon
    icon = setup_tray_icon()
    
    print("[SYSTEM] RipperFox is running in system tray. Right-click the icon for options.")
    icon.run()