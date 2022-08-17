# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('icones/application-exit-symbolic.svg','icones'),
    ('icones/desar.svg', 'icones'),
    ('icones/document-properties-symbolic.svg','icones'),
    ('icones/draw-arrow-back.svg','icones'),
    ('icones/edit-delete-symbolic.svg','icones'),
    ('icones/edit-symbolic.svg','icones'),
    ('icones/help-info-symbolic.svg','icones'),
    ('icones/inode-directory-symbolic.svg','icones'),
    ('icones/mail-mark-junk-symbolic.svg','icones'),
    ('icones/office-calendar-symbolic.svg','icones'),
    ('icones/system-shutdown-symbolic.svg','icones'),
    ('icones/system-switch-user-symbolic.svg','icones'),
    ('icones/value-increase-symbolic.svg','icones'),
    ('config.ini','.')],
    datas=[],
    hiddenimports=['python-dateutil'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
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
