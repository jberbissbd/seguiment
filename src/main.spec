# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[src/icones/application-exit-symbolic.svg,
    src/icones/desar.svg,src/icones/document-properties-symbolic.svg
    src/icones/desar.svg,src/icones/document-properties-symbolic.svg,
    src/icones/draw-arrow-back.svg,src/icones/edit-delete-symbolic.svg,
    src/icones/edit-symbolic.svg,src/icones/help-info-symbolic.svg,
    src/icones/image-filter-symbolic.svg,src/icones/inode-directory-symbolic.svg,
    src/icones/mail-mark-junk-symbolic.svg,src/icones/office-calendar-symbolic.svg,
    src/icones/system-shutdown-symbolic.svg,src/icones/system-switch-user-symbolic.svg,
    src/icones/value-increase-symbolic.svg,config.ini],
    datas=[],
    hiddenimports=[python-dateutil],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    warn_on_missing_hiddenimports = True,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='tutopy',
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
)
