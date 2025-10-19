import sys, os
# --- Local site-packages path ---
local_site = os.path.join(os.path.dirname(__file__), "python", "Lib", "site-packages")
if os.path.isdir(local_site) and local_site not in sys.path:
    sys.path.insert(0, local_site)

# --- Check dependencies ---
required = ["flask", "flask_cors", "colorama"]
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

# --- Optional color support for Windows CMD ---
try:
    from colorama import init as color_init, Fore, Style
    color_init()
except ImportError:
    class Dummy:
        def __getattr__(self, _): return ""
    Fore = Style = Dummy()

app = Flask(__name__)
CORS(app)

SETTINGS_FILE = "settings.json"
JOBS = {}
JOB_HISTORY_LIMIT = 10

# --- Base project directory ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Tool paths ---
LOCAL_PYTHON_DIR = os.path.join(BASE_DIR, "python")
LOCAL_YTDLP_PATH = os.path.join(BASE_DIR, "yt-dlp", "yt-dlp.exe")
LOCAL_FFMPEG_DIR = os.path.join(BASE_DIR, "ffmpeg")

# --- Add ffmpeg folder to PATH ---
os.environ["PATH"] = LOCAL_FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")

# --- Prefer local yt-dlp ---
if os.path.isfile(LOCAL_YTDLP_PATH):
    DEFAULT_YTDLP = LOCAL_YTDLP_PATH
elif shutil.which("yt-dlp"):
    DEFAULT_YTDLP = shutil.which("yt-dlp")
else:
    DEFAULT_YTDLP = "yt-dlp"


# --- Colorized logging ---
def log(tag, message, color=Fore.WHITE):
    print(f"{color}[{tag}]{Style.RESET_ALL} {message}")

# --- Save settings helper ---
def save_settings(data):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log("settings", f"Failed to save settings.json: {e}", Fore.RED)

# --- Settings loader ---
def load_settings():
    base = {
        "yt_dlp_path": DEFAULT_YTDLP,
        "default_dir": os.path.join(BASE_DIR, "downloads"),
        "default_args": "--recode-video mp4",
        "download_dirs": {},
        "show_toasts": True
    }

    # If no file exists, create a new one
    if not os.path.exists(SETTINGS_FILE):
        log("settings", "No settings.json found. Creating default.", Fore.YELLOW)
        save_settings(base)
        return base

    # If file exists, try to load or recover
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                raise ValueError("Empty settings file.")
            data = json.loads(content)
            base.update(data)
    except Exception as e:
        log("settings", f"Failed to load settings.json ({e}). Regenerating default.", Fore.RED)
        save_settings(base)

    os.makedirs(base["default_dir"], exist_ok=True)

    print("=" * 32)
    log("startup", f"Python runtime: {LOCAL_PYTHON_DIR}", Fore.CYAN)
    log("startup", f"Using yt-dlp from: {base['yt_dlp_path']}", Fore.CYAN)
    log("startup", f"ffmpeg path added: {LOCAL_FFMPEG_DIR}", Fore.CYAN)
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
        SETTINGS.update({
            "yt_dlp_path": new_data.get("yt_dlp_path", SETTINGS["yt_dlp_path"]),
            "default_dir": new_data.get("default_dir", SETTINGS["default_dir"]),
            "default_args": new_data.get("default_args", SETTINGS["default_args"]),
            "download_dirs": new_data.get("download_dirs", SETTINGS.get("download_dirs", {})),
            "show_toasts": new_data.get("show_toasts", SETTINGS.get("show_toasts", True))
        })
        save_settings(SETTINGS)
        log("settings", "Updated and saved settings.json", Fore.YELLOW)
    return jsonify(SETTINGS)


# --- DOWNLOAD ROUTE ---
@app.route("/api/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    parsed = urllib.parse.urlparse(url)
    hostname = parsed.hostname or "unknown"
    site_settings = get_site_config(url, SETTINGS.get("download_dirs", {}))
    yt_dlp_path = SETTINGS.get("yt_dlp_path", DEFAULT_YTDLP)

    download_dir = (site_settings.get("dir") if site_settings else SETTINGS["default_dir"])
    args = (site_settings.get("args") if site_settings else SETTINGS["default_args"])
    os.makedirs(download_dir, exist_ok=True)

    if url.lower().endswith(".gif"):
        args = " ".join(a for a in args.split() if "recode-video" not in a)
        log("yt-dlp", "Detected GIF — skipping recode flag", Fore.MAGENTA)

    job_id = str(int(time.time() * 1000))
    # include hostname so UI can display it
    JOBS[job_id] = {"url": url, "site": hostname, "status": "starting", "dir": download_dir}

    def run_job():
        JOBS[job_id]["status"] = "running"
        cmd = f'"{yt_dlp_path}" {args} -P "{download_dir}" "{url}"'
        log("yt-dlp", f"Running command:\n{cmd}", Fore.GREEN)
        try:
            subprocess.run(cmd, shell=True)
            JOBS[job_id]["status"] = "completed"
            log("yt-dlp", f"Job completed: {url}", Fore.CYAN)
        except Exception as e:
            JOBS[job_id]["status"] = f"error: {e}"
            log("error", f"Download failed: {e}", Fore.RED)

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
