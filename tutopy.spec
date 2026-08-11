# -*- mode: python ; coding: utf-8 -*-

import sys


icon_path = (
    "tutopy/ui/assets/tutopy.ico"
    if sys.platform == "win32"
    else "tutopy/ui/assets/tutopy.png"
)

a = Analysis(
    ["tutopy/main.py"],
    pathex=[],
    binaries=[],
    datas=[("tutopy/ui/assets", "tutopy/ui/assets")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "pytestqt"],
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
    name="Tutopy",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)
