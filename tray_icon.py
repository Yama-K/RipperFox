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

def setup_tray_icon():
    image = create_tray_icon()
    
    menu = pystray.Menu(
        pystray.MenuItem('Show Console', show_window),
        pystray.MenuItem('Hide Console', hide_window),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Exit', exit_app)
    )
    
    icon = pystray.Icon("RipperFox", image, "RipperFox Backend", menu)
    return icon

def start_backend():
    """Start the Flask backend"""
    try:
        from yt_backend import app
        print("[SYSTEM] Starting Flask backend on port 5100...")
        # Run in a separate thread to avoid blocking
        threading.Thread(target=lambda: app.run(port=5100, debug=False, use_reloader=False), daemon=True).start()
    except Exception as e:
        print(f"[ERROR] Failed to start backend: {e}")

if __name__ == "__main__":
    # Start the backend first
    start_backend()
    
    # Then start the tray icon
    icon = setup_tray_icon()
    
    # Hide console window initially
    import ctypes
    console_window = ctypes.windll.kernel32.GetConsoleWindow()
    if console_window:
        ctypes.windll.user32.ShowWindow(console_window, 0)  # SW_HIDE
    
    print("[SYSTEM] RipperFox is running in system tray. Right-click the icon for options.")
    icon.run()