# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PIL import Image, ImageDraw
from PyInstaller.utils.hooks import collect_all

# Ícone Windows da v0.0.9. É gerado deterministicamente no build a partir da
# mesma identidade visual do SVG usado pela janela (âncora + radar + notícia).
icon_path = Path("resources/monitor-icon.ico")
icon_path.parent.mkdir(parents=True, exist_ok=True)
if not icon_path.exists():
    size = 256
    image = Image.new("RGBA", (size, size), (3, 24, 48, 255))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((8, 8, 248, 248), radius=46, outline=(24, 191, 255, 255), width=6)
    for radius, width in ((88, 4), (66, 3), (44, 2)):
        draw.ellipse((128-radius, 124-radius, 128+radius, 124+radius), outline=(8, 121, 173, 190), width=width)
    gold = (255, 194, 26, 255)
    deep = (181, 116, 0, 255)
    draw.ellipse((110, 36, 146, 72), fill=(3, 24, 48, 255), outline=gold, width=8)
    draw.rounded_rectangle((121, 66, 135, 170), radius=7, fill=gold, outline=deep, width=2)
    draw.rounded_rectangle((92, 82, 164, 95), radius=6, fill=gold, outline=deep, width=2)
    draw.arc((61, 112, 195, 214), 10, 170, fill=gold, width=13)
    draw.polygon([(59, 153), (84, 140), (81, 170)], fill=gold)
    draw.polygon([(197, 153), (172, 140), (175, 170)], fill=gold)
    draw.rounded_rectangle((163, 160, 231, 226), radius=12, fill=(235, 247, 255, 255), outline=(16, 180, 245, 255), width=4)
    draw.rectangle((174, 173, 192, 198), fill=(30, 137, 255, 255))
    draw.line((199, 177, 220, 177), fill=(22, 72, 110, 255), width=5)
    draw.line((199, 190, 220, 190), fill=(22, 72, 110, 255), width=5)
    draw.line((174, 211, 220, 211), fill=(22, 72, 110, 255), width=5)
    image.save(icon_path, format="ICO", sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])

# PySide6 is intentionally NOT collected wholesale here. PyInstaller's Qt hooks
# follow the application's real imports and collect the Qt modules/plugins they
# require. This avoids redistributing unrelated Qt modules while preserving the
# functional dependency graph proved by the portable smoke suite.
pdfium_datas, pdfium_bins, pdfium_hidden = collect_all("pypdfium2")
fitz_datas, fitz_bins, fitz_hidden = collect_all("fitz")
trust_datas, trust_bins, trust_hidden = collect_all("truststore")

block_cipher = None

a = Analysis(
    ["run.py"],
    pathex=["src"],
    binaries=pdfium_bins + fitz_bins + trust_bins,
    datas=pdfium_datas + fitz_datas + trust_datas,
    hiddenimports=(
        pdfium_hidden
        + fitz_hidden
        + trust_hidden
        + [
            "PySide6.QtWebEngineCore",
            "PySide6.QtWebEngineWidgets",
            "PySide6.QtWebChannel",
            "PySide6.QtPrintSupport",
            "PySide6.QtMultimedia",
            "PySide6.QtMultimediaWidgets",
            "monitor_noticias.extractor_worker_process",
            "monitor_noticias.ui.v009_runtime_fixes",
        ]
    ),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=["scripts/pyi_runtime_portable_validation.py"],
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
    icon=str(icon_path),
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
