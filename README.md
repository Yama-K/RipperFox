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

### ⚙️ Installation (Automatic, permanent, signed)

### 1. Left click on RipperFox-1.0.xpi and install it

### 2. Download [RipperFox-Backend.zip](https://github.com/Yama-K/RipperFox/releases/download/Stable-signed/RipperFox-backend.zip)

  Unpack it somewhere, preferably into "RipperFox" folder or something similar. 

### 3. Run ```!run_backend.bat```

  This will install python and dependencies, download ffmpeg and yt-dlp. 

### 4. Once done, don't kill the install terminal, that's your backend. 

---

### ⚙️ Installation (Manual, temporary, for unsigned)

### 1. Start the backend
Run: ```run_backend.bat``` 
Leave that window open — it launches the local Flask server on port 5100.

### 2. Install as temporary add-on
Go to: ```about:debugging#/runtime/this-firefox``` and choose ```This Firefox```

<img width="226" height="127" alt="image" src="https://github.com/user-attachments/assets/cfff9939-256d-41ff-b1ee-27ec4bcc7f99" />

Click ```Load Temporary Add-On``` and navigate to ```RipperFox\RipperFox\``` and select ```manifest.json```

Done. Make sure your ```!run_backend.bat``` is running. 

---

### ⚙️ Installation (Manual, Permanent, Requires ESR, DEV or Nightly builds, for unsigned)

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
