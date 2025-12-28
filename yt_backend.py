import sys, os
# --- Local site-packages path ---
local_site = os.path.join(os.path.dirname(__file__), "python", "Lib", "site-packages")
if os.path.isdir(local_site) and local_site not in sys.path:
    sys.path.insert(0, local_site)

# --- yt-dlp_updater support ---
try:
    from ytdlp_updater import run_ytdlp_with_binary, ensure_ytdlp_binary, auto_update_check
    YTDLP_UPDATER_AVAILABLE = True
except ImportError:
    YTDLP_UPDATER_AVAILABLE = False
    print("[WARNING] ytdlp_updater not available, using Python package")

# --- Add FFmpeg to PATH for bundled executable ---
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    base_dir = sys._MEIPASS
    os.environ['PATH'] = base_dir + os.pathsep + os.environ['PATH']

# --- Check dependencies ---
required = ["flask", "flask_cors", "colorama", "yt_dlp", "ffmpeg"]
missing = []
for pkg in required:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)

if missing:
    print("=" * 60)
    print("RipperFox Backend - Missing Dependencies Detected")
    print("The following Python packages are missing:")
    print("  ", ", ".join(missing))
    print("\nPlease run 'python_install.bat' in the backend folder.")
    print("=" * 60)
    input("Press Enter to exit...")
    sys.exit(1)

# --- Force local site-packages path for portable Python ---
local_site = os.path.join(os.path.dirname(__file__), "python", "Lib", "site-packages")
if os.path.isdir(local_site) and local_site not in sys.path:
    sys.path.insert(0, local_site)
# ----------------------------------------------------------

import subprocess, threading, json, time, urllib.parse, shutil
from flask import Flask, request, jsonify
from flask_cors import CORS
from fnmatch import fnmatch

# Import the new packages
import yt_dlp
import ffmpeg

# --- Optional color support for Windows CMD ---
try:
    from colorama import init as color_init, Fore, Style
    color_init()
except ImportError:
    class Dummy:
        def __getattr__(self, _): return ""
    Fore = Style = Dummy()

# --- Handle settings file location for EXE vs Script ---
if getattr(sys, 'frozen', False):
    # Running as compiled exe - use user's appdata folder
    import appdirs
    app_name = "RipperFox"
    app_author = "RipperFox"
    data_dir = appdirs.user_data_dir(app_name, app_author)
    os.makedirs(data_dir, exist_ok=True)
    SETTINGS_FILE = os.path.join(data_dir, "settings.json")
    BASE_DIR = data_dir  # Use appdata as base directory for downloads
    
    # Copy default settings if they don't exist
    if not os.path.exists(SETTINGS_FILE):
        try:
            # Get default settings from bundled resources
            base_dir = sys._MEIPASS
            default_settings_path = os.path.join(base_dir, "settings.json")
            if os.path.exists(default_settings_path):
                with open(default_settings_path, 'r', encoding='utf-8') as f:
                    default_settings = json.load(f)
                with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(default_settings, f, indent=2)
                print(f"[SYSTEM] Created settings file: {SETTINGS_FILE}")
        except Exception as e:
            print(f"[WARNING] Could not create settings file: {e}")
else:
    # Running as script - use local folder
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

# --- Global variables ---
JOBS = {}
JOB_HISTORY_LIMIT = 10
LOCAL_PYTHON_DIR = os.path.join(BASE_DIR, "python")
# ------------------------------------------------------------------

app = Flask(__name__)
CORS(app)

# --- Disable Flask default request logging ---
import logging
log = logging.getLogger('werkzeug')
log.disabled = True
# --------------------------------------------

# --- Colorized logging ---
def log(tag, message, color=Fore.WHITE):
    print(f"{color}[{tag}]{Style.RESET_ALL} {message}")

# --- Save settings helper ---
def save_settings(data):
    # Convert absolute paths back to relative (when under BASE_DIR) before persisting
    to_save = dict(data)
    try:
        dd = to_save.get("default_dir")
        if isinstance(dd, str) and os.path.isabs(dd):
            try:
                if os.path.commonpath([os.path.abspath(dd), os.path.abspath(BASE_DIR)]) == os.path.abspath(BASE_DIR):
                    to_save["default_dir"] = os.path.relpath(dd, BASE_DIR)
            except Exception:
                pass

        # Normalize download_dirs entries
        download_dirs = to_save.get("download_dirs", {})
        for k, cfg in list(download_dirs.items()):
            dir_val = cfg.get("dir")
            if isinstance(dir_val, str) and os.path.isabs(dir_val):
                try:
                    if os.path.commonpath([os.path.abspath(dir_val), os.path.abspath(BASE_DIR)]) == os.path.abspath(BASE_DIR):
                        cfg["dir"] = os.path.relpath(dir_val, BASE_DIR)
                except Exception:
                    pass
        to_save["download_dirs"] = download_dirs

        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(to_save, f, indent=2)
    except Exception as e:
        log("settings", f"Failed to save settings.json: {e}", Fore.RED)

# --- Settings loader - simplified without yt_dlp_path ---
def load_settings():
    # Keep stored/default values relative-friendly and resolve them only for runtime
    base = {
        "default_dir": "downloads",
        "default_args": "--recode-video mp4 --embed-thumbnail --embed-metadata",
        "download_dirs": {},
        "show_toasts": True
    }

    # If no file exists, create a new one (persisting the relative defaults)
    if not os.path.exists(SETTINGS_FILE):
        log("settings", "No settings.json found. Creating default.", Fore.YELLOW)
        save_settings(base)
        # Build and return a runtime-resolved copy
        runtime = dict(base)
        runtime["default_dir"] = os.path.abspath(os.path.join(BASE_DIR, base["default_dir"]))
        runtime["download_dirs"] = {}
        return runtime

    # If file exists, try to load or recover
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                raise ValueError("Empty settings file.")
            data = json.loads(content)
            # Remove yt_dlp_path if it exists in old settings (migration from old version)
            if 'yt_dlp_path' in data:
                del data['yt_dlp_path']

            # Convert stored absolute paths back to relative when they point inside BASE_DIR
            changed = False
            dd = data.get('default_dir')
            if isinstance(dd, str) and os.path.isabs(dd):
                try:
                    if os.path.commonpath([os.path.abspath(dd), os.path.abspath(BASE_DIR)]) == os.path.abspath(BASE_DIR):
                        data['default_dir'] = os.path.relpath(dd, BASE_DIR)
                        changed = True
                except Exception:
                    pass

            ddirs = data.get('download_dirs', {})
            for k, cfg in list(ddirs.items()):
                dir_val = cfg.get('dir')
                if isinstance(dir_val, str) and os.path.isabs(dir_val):
                    try:
                        if os.path.commonpath([os.path.abspath(dir_val), os.path.abspath(BASE_DIR)]) == os.path.abspath(BASE_DIR):
                            cfg['dir'] = os.path.relpath(dir_val, BASE_DIR)
                            changed = True
                    except Exception:
                        pass
            data['download_dirs'] = ddirs

            base.update(data)

            # If we converted any absolute in-file paths to relative, persist that change to avoid committing system-local paths
            if changed:
                try:
                    save_settings(base)
                    log('settings', 'Normalized stored paths to relative locations', Fore.YELLOW)
                except Exception:
                    pass
    except Exception as e:
        log("settings", f"Failed to load settings.json ({e}). Regenerating default.", Fore.RED)
        save_settings(base)

    # ----- Build runtime-resolved copy (do not persist these changes) -----
    runtime = dict(base)

    # Resolve default_dir to absolute (if it's relative)
    if not os.path.isabs(runtime.get("default_dir", "")):
        runtime["default_dir"] = os.path.abspath(os.path.join(BASE_DIR, runtime.get("default_dir", "")))

    # Normalize per-site download dirs for runtime
    resolved_download_dirs = {}
    for key, cfg in runtime.get("download_dirs", {}).items():
        cfg_copy = dict(cfg)
        dir_val = cfg_copy.get("dir")
        if dir_val and not os.path.isabs(dir_val):
            cfg_copy["dir"] = os.path.abspath(os.path.join(BASE_DIR, dir_val))
        resolved_download_dirs[key] = cfg_copy
    runtime["download_dirs"] = resolved_download_dirs

    # Ensure default dir exists, with fallbacks if creation fails
    def _ensure_dir(path):
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            log("settings", f"Failed to create directory '{path}': {e}", Fore.RED)
            return False

    preferred = runtime["default_dir"]
    if not _ensure_dir(preferred):
        fallback1 = os.path.abspath(os.path.join(BASE_DIR, "downloads"))
        if _ensure_dir(fallback1):
            runtime["default_dir"] = fallback1
        else:
            # Try user's Downloads folder then temp dir as last resort
            user_dl = os.path.join(os.path.expanduser("~"), "Downloads")
            if _ensure_dir(user_dl):
                runtime["default_dir"] = user_dl
            else:
                import tempfile
                runtime["default_dir"] = tempfile.gettempdir()
                _ensure_dir(runtime["default_dir"])

    print("=" * 32)
    log("startup", f"Python runtime: {LOCAL_PYTHON_DIR}", Fore.CYAN)
    log("startup", f"Using Python yt-dlp package", Fore.CYAN)
    log("startup", f"Using Python ffmpeg package", Fore.CYAN)
    log("startup", f"Default download dir: {base['default_dir']}", Fore.CYAN)
    log("startup", f"Settings file: {os.path.abspath(SETTINGS_FILE)}", Fore.CYAN)
    print("=" * 32)
    return base

# --- Initialize settings once, globally ---
SETTINGS = load_settings()

# --- Site matcher with comma-separated support ---
def get_site_config(url, download_dirs):
    parsed = urllib.parse.urlparse(url)
    hostname = parsed.hostname or ""
    matched_pattern = None
    matched_cfg = None

    for pattern_group, cfg in download_dirs.items():
        # Split patterns like "*youtube*, *youtu.be*" into individual entries
        patterns = [p.strip() for p in pattern_group.split(",") if p.strip()]
        for pattern in patterns:
            # Match either full fnmatch or partial substring (for loose matching)
            if fnmatch(hostname, pattern) or pattern.strip("*") in hostname:
                matched_pattern = pattern
                matched_cfg = cfg
                break
        if matched_cfg:
            break

    if matched_cfg:
        log("yt-dlp", f"Using site settings for {matched_pattern} ({hostname})", Fore.GREEN)
        return matched_cfg
    else:
        log("yt-dlp", f"Using general settings for {hostname}", Fore.YELLOW)
        return None

# --- SETTINGS ROUTE ---
@app.route("/api/settings", methods=["GET", "POST"])
def settings():
    global SETTINGS
    if request.method == "POST":
        new_data = request.get_json()
        # Remove yt_dlp_path from the update since we don't use it anymore
        SETTINGS.update({
            "default_dir": new_data.get("default_dir", SETTINGS["default_dir"]),
            "default_args": new_data.get("default_args", SETTINGS["default_args"]),
            "download_dirs": new_data.get("download_dirs", SETTINGS.get("download_dirs", {})),
            "show_toasts": new_data.get("show_toasts", SETTINGS.get("show_toasts", True))
        })
        save_settings(SETTINGS)
        log("settings", "Updated and saved settings.json", Fore.YELLOW)
    return jsonify(SETTINGS)

# --- YT-DLP UPDATE ROUTES ---
# Tracks the last update attempt and its status
UPDATE_JOB = {"status": "idle", "message": "Idle", "started_at": None, "finished_at": None, "latest_version": None}

@app.route("/api/update-yt-dlp", methods=["POST"])
def update_yt_dlp_api():
    global UPDATE_JOB
    if not YTDLP_UPDATER_AVAILABLE:
        return jsonify({"error": "ytdlp_updater not available"}), 503

    def _do_update():
        from ytdlp_updater import download_latest_ytdlp, ensure_ytdlp_binary
        try:
            UPDATE_JOB.update({"status": "running", "message": "Starting update...", "started_at": time.time(), "finished_at": None})
            log("yt-dlp", "Starting yt-dlp update...", Fore.CYAN)
            ok = download_latest_ytdlp()
            if ok:
                path, version = ensure_ytdlp_binary()
                UPDATE_JOB.update({"status": "succeeded", "message": f"Updated to {version}", "finished_at": time.time(), "latest_version": version})
                log("yt-dlp", f"Updated yt-dlp to {version}", Fore.GREEN)
            else:
                UPDATE_JOB.update({"status": "failed", "message": "Download failed", "finished_at": time.time()})
                log("yt-dlp", "yt-dlp download failed", Fore.RED)
        except Exception as e:
            UPDATE_JOB.update({"status": "failed", "message": str(e), "finished_at": time.time()})
            log("yt-dlp", f"Update failed: {e}", Fore.RED)

    threading.Thread(target=_do_update, daemon=True).start()
    return jsonify({"status": "started"})

@app.route("/api/update-status", methods=["GET"])
def update_status():
    # Return current update job info
    return jsonify(UPDATE_JOB)

# --- Enhanced download function with better yt-dlp options ---
@app.route("/api/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    parsed = urllib.parse.urlparse(url)
    hostname = parsed.hostname or "unknown"
    site_settings = get_site_config(url, SETTINGS.get("download_dirs", {}))
    
    download_dir = (site_settings.get("dir") if site_settings else SETTINGS["default_dir"])
    custom_args = (site_settings.get("args") if site_settings else SETTINGS["default_args"])
    os.makedirs(download_dir, exist_ok=True)

    job_id = str(int(time.time() * 1000))
    JOBS[job_id] = {"url": url, "site": hostname, "status": "starting", "dir": download_dir}

    def run_job():
        JOBS[job_id]["status"] = "running"
        
        try:
            # Build yt-dlp options from settings
            ydl_opts = {
                'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
            }
            
            # Parse custom arguments from settings
            if '--embed-thumbnail' in custom_args:
                ydl_opts['embedthumbnail'] = True
            if '--embed-metadata' in custom_args:
                ydl_opts['addmetadata'] = True
            if '--recode-video mp4' in custom_args:
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }]
            
            log("yt-dlp", f"Downloading {url} to {download_dir}", Fore.GREEN)
            log("yt-dlp", f"Using options: {ydl_opts}", Fore.GREEN)

            # Try to use external binary first if available
            if YTDLP_UPDATER_AVAILABLE:
                log("yt-dlp", f"Using external yt-dlp binary for {url}", Fore.GREEN)
                try:
                    returncode, stdout, stderr = run_ytdlp_with_binary(url, download_dir, custom_args)
                    if returncode == 0:
                        JOBS[job_id]["status"] = "completed"
                        log("yt-dlp", f"Job completed using binary: {url}", Fore.CYAN)
                        return
                    else:
                        # Fallback to python package
                        JOBS[job_id]["status"] = f"error: {stderr}"
                        log("error", f"Binary download failed: {stderr}", Fore.RED)
                except Exception as be:
                    log("error", f"Binary run failed: {be}", Fore.RED)

            # Fallback to Python package if binary failed or not available
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            JOBS[job_id]["status"] = "completed"
            log("yt-dlp", f"Job completed: {url}", Fore.CYAN)
            
        except Exception as e:
            JOBS[job_id]["status"] = f"error: {e}"
            log("error", f"Download failed: {e}", Fore.RED)

        # Clean up old jobs
        if len(JOBS) > JOB_HISTORY_LIMIT:
            for old in list(JOBS.keys())[:-JOB_HISTORY_LIMIT]:
                del JOBS[old]

    threading.Thread(target=run_job, daemon=True).start()
    return jsonify({"job_id": job_id})

# --- STATUS ROUTES ---
@app.route("/api/status", methods=["GET"])
def status():
    return jsonify(dict(list(JOBS.items())[-JOB_HISTORY_LIMIT:]))

@app.route("/api/status", methods=["DELETE"])
def clear_status():
    JOBS.clear()
    log("status", "Cleared all job history", Fore.MAGENTA)
    return jsonify({"cleared": True})

if __name__ == "__main__":
    app.run(port=5100)