# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ripperfox_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[('icon.ico', '.'), ('settings.json', '.'), ('yt_backend.py', '.'), ('ffmpeg.exe', '.'), ('ffprobe.exe', '.')],
    hiddenimports=['flask', 'flask_cors', 'colorama', 'yt_dlp', 'ffmpeg', 'pystray', 'PIL', 'PIL._imaging', 'PIL._imagingft', 'yt_dlp.extractor', 'yt_dlp.postprocessor', 'appdirs'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='RipperFox',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
