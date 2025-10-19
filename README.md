# RipperFox

### 🦊 RipperFox  RipperFox is a self-hosted Firefox extension and local backend combo that lets you download videos, GIFs, and images directly from websites using your own machine and **yt-dlp**.   No trackers, no third-party servers, and no dependency on any online service — everything runs locally.
<img width="512" height="512" alt="ripperfox" src="https://github.com/user-attachments/assets/fa763b46-fea6-4405-80b5-488dab362561" />

---

## ✨ Features

- Right-click → **“RipperFox Download”** on almost any link, image, or video.
- Automatic format conversion via `yt-dlp` and `ffmpeg`.
- Per-site output folders and custom arguments.
- Backend built in **Python + Flask**, portable and self-contained.
- Works completely offline once set up.

---

## ⚙️ Installation (Manual, Permanent, Requires ESR, DEV or Nightly builds)

### 1. Start the backend
Run: ```run_backend.bat``` 
Leave that window open — it launches the local Flask server on port 5100.

### 2. Package the extension

Open the RipperFox/ RipperFox folder

Select all files inside (manifest.json, popup/, background.js, etc.).

Compress them into a ZIP file.

Rename it to: ```RipperFox.xpi```

### 3. Enable unsigned installs

In Firefox Developer Edition or Nightly, open about:config and set:
```xpinstall.signatures.required → false```

### 4. Install

Go to about:addons → Install Add-on From File… → choose RipperFox.xpi.

The add-on will stay installed after restart.
To update it later, rebuild the .xpi and drag it onto about:addons.

---

### 🧠 Usage

Make sure the backend is running. It will complain in Settings tab otherwise. 

Right-click any link, image, video, or page background → “RipperFox Download.”

Files are saved in your configured download folder (or per-site rules).

---


### 🧰 Optional Configuration

Open the RipperFox popup → Settings tab.

Customize:

Default save directory

yt-dlp arguments

Per-site folders and args (*youtube.com*, *youtu.be*, etc.)

All settings persist in backend/settings.json.

---


### 🚀 Updating yt-dlp

Open terminal → drag & drop ```yt-dlp.exe``` to it, add update option ```-U```, press enter, done.

Like so: ```C:\Path\To\yt-dlp\yt-dlp.exe -U``` will get you 

```
C:\Path\To\yt-dlp\yt-dlp.exe -U
Latest version: stable@2025.10.14 from yt-dlp/yt-dlp
yt-dlp is up to date (stable@2025.10.14 from yt-dlp/yt-dlp)
```

---

### 🧱 License

MIT License — do whatever you like, but don’t hold the creator liable.
Credit the projects listed below.

---

### ❤️ Credits

yt-dlp — core download engine

FFmpeg — media processing

Flask — lightweight Python backend
