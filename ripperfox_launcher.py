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


def check_updates(icon, item):
    """Check for yt-dlp updates"""
    try:
        from ytdlp_updater import check_for_ytdlp_update, download_latest_ytdlp
        import tkinter as tk
        from tkinter import messagebox
        import threading
        
        def check_and_update():
            needs_update, latest_version, _ = check_for_ytdlp_update()
            if needs_update:
                root = tk.Tk()
                root.withdraw()
                result = messagebox.askyesno(
                    "Update Available",
                    f"A new yt-dlp version ({latest_version}) is available.\nUpdate now?"
                )
                if result:
                    if download_latest_ytdlp():
                        messagebox.showinfo("Success", "yt-dlp updated successfully!")
                    else:
                        messagebox.showerror("Error", "Failed to update yt-dlp")
                root.destroy()
        
        threading.Thread(target=check_and_update, daemon=True).start()
    except Exception as e:
        print(f"[UPDATE] Error checking updates: {e}")

def setup_tray_icon():
    image = create_tray_icon()
    
    menu = pystray.Menu(
        pystray.MenuItem('Show Console', show_window),
        pystray.MenuItem('Hide Console', hide_window),
        pystray.MenuItem('Check for yt-dlp Update', check_updates),
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
        # If ytdlp_updater supports auto_update_check, start it in background
        try:
            from ytdlp_updater import auto_update_check
            threading.Thread(target=auto_update_check, daemon=True).start()
        except Exception:
            pass
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


def check_updates(icon, item):
    """Check for yt-dlp updates"""
    try:
        from ytdlp_updater import check_for_ytdlp_update, download_latest_ytdlp
        import tkinter as tk
        from tkinter import messagebox
        import threading
        
        def check_and_update():
            needs_update, latest_version, _ = check_for_ytdlp_update()
            if needs_update:
                root = tk.Tk()
                root.withdraw()
                result = messagebox.askyesno(
                    "Update Available",
                    f"A new yt-dlp version ({latest_version}) is available.\nUpdate now?"
                )
                if result:
                    if download_latest_ytdlp():
                        messagebox.showinfo("Success", "yt-dlp updated successfully!")
                    else:
                        messagebox.showerror("Error", "Failed to update yt-dlp")
                root.destroy()
        
        threading.Thread(target=check_and_update, daemon=True).start()
    except Exception as e:
        print(f"[UPDATE] Error checking updates: {e}")