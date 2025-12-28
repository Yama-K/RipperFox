import os
import sys
import requests
import threading
import time
import json
from pathlib import Path

def get_appdata_dir():
    """Get the appdata directory for RipperFox"""
    if getattr(sys, 'frozen', False):
        import appdirs
        data_dir = appdirs.user_data_dir("RipperFox", "RipperFox")
    else:
        data_dir = os.path.dirname(__file__)
    
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def get_ytdlp_binary_path():
    """Get the path to yt-dlp binary (external to exe)"""
    data_dir = get_appdata_dir()
    ytdlp_path = os.path.join(data_dir, "yt-dlp.exe")
    return ytdlp_path

def check_for_ytdlp_update(current_version=None):
    """Check if a newer yt-dlp version is available"""
    try:
        response = requests.get(
            "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest",
            timeout=10
        )
        # Treat non-200 responses as 'no update' instead of raising
        if response.status_code != 200:
            print(f"[yt-dlp] Update check skipped (status {response.status_code})")
            return False, None, []

        try:
            latest_release = response.json()
        except ValueError as e:
            # JSON decode errors (e.g., HTML error page or empty body) are benign for auto-check
            print(f"[yt-dlp] Update check skipped (invalid response): {e}")
            return False, None, []

        latest_version = latest_release.get("tag_name", "").lstrip("v")
        
        # If we have a current version to compare
        if current_version and latest_version:
            from packaging import version
            if version.parse(latest_version) > version.parse(current_version):
                return True, latest_version, latest_release.get("assets", [])
        
        return False, latest_version, latest_release.get("assets", [])
    except Exception as e:
        # Network or other errors should not alarm the user; log and continue
        print(f"[yt-dlp] Update check skipped: {e}")
        return False, None, []

def download_latest_ytdlp():
    """Download the latest yt-dlp binary"""
    try:
        ytdlp_path = get_ytdlp_binary_path()
        download_url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
        
        print(f"[yt-dlp] Downloading latest version...")
        response = requests.get(download_url, timeout=30)
        response.raise_for_status()
        
        with open(ytdlp_path, 'wb') as f:
            f.write(response.content)
        
        print(f"[yt-dlp] Updated to latest version")
        return True
    except Exception as e:
        print(f"[yt-dlp] Download failed: {e}")
        return False

def get_ytdlp_version(ytdlp_path):
    """Get version of yt-dlp binary"""
    try:
        import subprocess
        result = subprocess.run(
            [ytdlp_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip()
    except:
        return None

def ensure_ytdlp_binary():
    """Ensure we have a working yt-dlp binary"""
    ytdlp_path = get_ytdlp_binary_path()
    
    # Check if binary exists and is working
    if os.path.exists(ytdlp_path):
        version = get_ytdlp_version(ytdlp_path)
        if version:
            return ytdlp_path, version
    
    # Try to use bundled version first (in MEIPASS)
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
        bundled_path = os.path.join(base_dir, "yt-dlp.exe")
        if os.path.exists(bundled_path):
            import shutil
            shutil.copy2(bundled_path, ytdlp_path)
            version = get_ytdlp_version(ytdlp_path)
            if version:
                return ytdlp_path, version
    
    # Download fresh copy
    if download_latest_ytdlp():
        version = get_ytdlp_version(ytdlp_path)
        if version:
            return ytdlp_path, version
    
    return None, None

def run_ytdlp_with_binary(url, download_dir, custom_args=""):
    """Run yt-dlp using the external binary"""
    ytdlp_path, version = ensure_ytdlp_binary()
    
    if not ytdlp_path:
        raise Exception("Failed to get yt-dlp binary")
    
    import subprocess
    import shlex
    
    # Build command
    cmd = [ytdlp_path, "-o", os.path.join(download_dir, "%(title)s.%(ext)s")]
    
    # Add custom arguments
    if custom_args:
        cmd.extend(shlex.split(custom_args))
    
    cmd.append(url)
    
    print(f"[yt-dlp] Running: {' '.join(cmd)}")
    
    # Run the command
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=3600  # 1 hour timeout
    )
    
    return result.returncode, result.stdout, result.stderr

def auto_update_check():
    """Background thread to check for updates periodically"""
    while True:
        try:
            ytdlp_path = get_ytdlp_binary_path()
            current_version = get_ytdlp_version(ytdlp_path)
            
            needs_update, latest_version, _ = check_for_ytdlp_update(current_version)
            
            if needs_update:
                print(f"[yt-dlp] Update available: {current_version} -> {latest_version}")
                # You could prompt user here or auto-update
                # download_latest_ytdlp()
        
        except Exception as e:
            # Non-fatal errors are normal (rate limits, network issues); log at info level
            print(f"[yt-dlp] Auto-update check skipped: {e}")
        
        # Check once per day
        time.sleep(24 * 60 * 60)