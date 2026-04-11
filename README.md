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
Screenshots

<img width="363" height="526" alt="image" src="https://github.com/user-attachments/assets/2024400c-2af5-42d2-b052-77272cad3ff6" />
<img width="363" height="526" alt="image" src="https://github.com/user-attachments/assets/fa4643f0-b744-4be2-9d76-c8f95810f327" />
<img width="363" height="124" alt="image" src="https://github.com/user-attachments/assets/202b048a-497d-4ecb-95fa-43f8c1fe46e5" />

---

## ✨ Features

- Right-click → **“RipperFox Download”** on almost any link, image, or video.
- Automatic format conversion via `yt-dlp` and `ffmpeg`.
- Per-site output folders and custom arguments.
- Backend built in **Python + Flask**, portable and self-contained.
- Works completely offline once set up.

---

### ⚙️ Installation

=======
### 1. Install the [RipperFox Extension by clicking me](https://github.com/Yama-K/RipperFoxExtension/releases/download/Release/RipperFox-2.1.xpi)

### 2. Download the exe: [RipperFox.exe](https://github.com/Yama-K/RipperFox/releases/download/Release/RipperFox.exe)
  and run it, it'll automatically hide it in your system tray. 

### For Linux see: https://github.com/Yama-K/RipperFox-Linux
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

### 🧱 License

MIT License — do whatever you like, but don’t hold the creator liable.
Credit the projects listed below.

---

### ❤️ Credits

yt-dlp — core download engine

FFmpeg — media processing

Flask — lightweight Python backend
