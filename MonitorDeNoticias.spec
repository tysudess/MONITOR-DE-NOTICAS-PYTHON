# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

pyside_datas, pyside_bins, pyside_hidden = collect_all("PySide6")
pdfium_datas, pdfium_bins, pdfium_hidden = collect_all("pypdfium2")

block_cipher = None

a = Analysis(
    ["run.py"],
    pathex=["src"],
    binaries=pyside_bins + pdfium_bins,
    datas=pyside_datas + pdfium_datas,
    hiddenimports=pyside_hidden + pdfium_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="MonitorDeNoticias",
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="MonitorDeNoticias",
)
