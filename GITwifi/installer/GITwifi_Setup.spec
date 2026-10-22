# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['installer/installer_runner.py'],
    pathex=[],
    binaries=[],
    datas=[('dist/GITwifi.exe', '.'), ('app_icon.ico', '.'), ('installer/setup.bat', '.')],
    hiddenimports=[],
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
    name='GITwifi_Setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='installer/version_setup_info.txt',
    icon=['app_icon.ico'],
)
