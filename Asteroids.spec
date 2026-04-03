# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all
import os

# 🔥 collect pygame
datas, binaries, hiddenimports = collect_all('pygame')

# 🔥 collect asset folder
asset_files = []
base_dir = os.getcwd()

for root, dirs, files in os.walk(os.path.join(base_dir, 'asset')):
    for f in files:
        full_path = os.path.join(root, f)
        rel_path = os.path.relpath(root, base_dir)
        asset_files.append((full_path, rel_path))

a = Analysis(
    ['ASTEROID.py'],
    pathex=[],
    binaries=binaries,
    datas=datas + asset_files,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Asteroids',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='asset/icon.icns',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='Asteroids',
)

app = BUNDLE(
    coll,
    name='Asteroids.app',
    icon='asset/icon.icns',
    bundle_identifier='com.asteroids.game',
)