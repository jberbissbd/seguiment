# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
hiddenimports = []
hiddenimports += collect_submodules('dateutil')

block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=['agents','gui'],
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
    ('icones/aplicacio.icns','icones'),
    ('icones/aplicacio.ico','icones'),
    ('icones/aplicacio.svg','icones'),
    ('config.ini','.')],
    datas=[],
    hiddenimports=[],
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
    [],
    icon='icones\aplicacio.ico'
    exclude_binaries=True,
    name='tutopy',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='tutopy',
)
