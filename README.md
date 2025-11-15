# RipperFox

### 🦊 RipperFox is a self-hosted Firefox extension and local backend combo that lets you download videos, GIFs, and images directly from websites using your own machine and **yt-dlp**.   No trackers, no third-party servers, and no dependency on any online service — everything runs locally.
<img width="512" height="512" alt="ripperfox" src="https://github.com/user-attachments/assets/fa763b46-fea6-4405-80b5-488dab362561" />

---

⚠️ Important

RipperFox consists of two parts:

The Firefox extension, which adds right-click download options.

The local backend, which must be downloaded and running on your machine for the extension to work.

The extension cannot function without the backend.
You can get the latest backend release and setup instructions right here in this repository.

---

## ✨ Features

- Right-click → **“RipperFox Download”** on almost any link, image, or video.
- Automatic format conversion via `yt-dlp` and `ffmpeg`.
- Per-site output folders and custom arguments.
- Backend built in **Python + Flask**, portable and self-contained.
- Works completely offline once set up.

---

### ⚙️ Installation

### 1. Install [RipperFox Firefox Add-on](https://github.com/Yama-K/RipperFox/releases/download/Stable-1.1/RipperFox-1.0.xpi) (Just left click it, it should just install.)

### 2. Clone this repo: ```git clone https://github.com/Yama-K/RipperFox```
  Unpack it and run !run_backend.bat 

### 3. Once done, don't kill the install terminal, that's your backend. 

---

### Uninstall

### 1. Stop the backend

### 2. Uninstall the add-on the same way you uninstall any other extension. 

### 3. It's gone. 

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
