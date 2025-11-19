import sys
import os
import threading
from PIL import Image, ImageDraw
import pystray

def create_tray_icon():
    base_dir = os.path.dirname(__file__)
    
    # For PyInstaller, we need to handle the bundled resources
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        base_dir = sys._MEIPASS
    
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
    """Start the Flask backend with proper path handling"""
    try:
        # Add the local site-packages to path (for PyInstaller)
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            base_dir = sys._MEIPASS
        else:
            # Running as script
            base_dir = os.path.dirname(__file__)
        
        local_site = os.path.join(base_dir, "python", "Lib", "site-packages")
        if os.path.isdir(local_site) and local_site not in sys.path:
            sys.path.insert(0, local_site)
        
        from yt_backend import app
        print("[SYSTEM] Starting Flask backend on port 5100...")
        threading.Thread(target=lambda: app.run(port=5100, debug=False, use_reloader=False), daemon=True).start()
    except Exception as e:
        print(f"[ERROR] Failed to start backend: {e}")

if __name__ == "__main__":
    # Start the backend
    start_backend()
    
    # Setup and run tray icon
    icon = setup_tray_icon()
    
    # Hide console window initially
    import ctypes
    console_window = ctypes.windll.kernel32.GetConsoleWindow()
    if console_window:
        ctypes.windll.user32.ShowWindow(console_window, 0)
    
    print("[SYSTEM] RipperFox is running in system tray. Right-click the icon for options.")
    icon.run()