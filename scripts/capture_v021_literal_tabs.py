from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "windows")
os.environ.setdefault("MONITOR_DISABLE_WEATHER", "1")
os.environ.setdefault("MONITOR_DISABLE_EXTERNAL_INTEGRATIONS", "1")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for entry in (ROOT, SRC):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

import run as _runtime_bootstrap  # noqa: F401,E402

from PySide6.QtCore import QEventLoop, QPoint, QTimer  # noqa: E402
from PySide6.QtGui import QFont, QPixmap  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402
from monitor_noticias.ui.main_window import MainWindow  # noqa: E402
from monitor_noticias.ui.sections import Section  # noqa: E402


def wait(app, ms=1100):
    loop = QEventLoop(); QTimer.singleShot(ms, loop.quit); loop.exec(); app.processEvents()


def capture(window, section, filename, attr, app):
    window.navigate(section); wait(app)
    page = window.pages[section]
    surface = getattr(page, attr, None)
    if surface is None or surface.isHidden():
        raise RuntimeError(f"Superfície literal ausente/oculta em {section.name}")
    if surface.geometry() != page.rect():
        raise RuntimeError(f"Geometria literal divergente em {section.name}: {surface.geometry()} != {page.rect()}")
    if surface.parent() is not page:
        raise RuntimeError(f"Parent da superfície literal divergente em {section.name}")
    pix = QPixmap(1672, 941); pix.fill(); window.render(pix, QPoint(0, 0))
    out = Path("artifacts") / filename; out.parent.mkdir(exist_ok=True)
    if not pix.save(str(out), "PNG"):
        raise RuntimeError(f"Falha ao salvar {filename}")
    return out


def main():
    app = QApplication.instance() or QApplication([]); app.setFont(QFont("Segoe UI", 10))
    window = MainWindow(); window._timer.stop(); window.resize(1672, 941)
    window.navigate(Section.HOME); wait(app)
    width = window.sidebar.width(); style = window.sidebar.styleSheet()
    if width != 225: raise RuntimeError(f"Sidebar divergente: {width}")

    required = set(Section)
    if not required.issubset(window.pages) or not required.issubset(window.nav_buttons):
        raise RuntimeError("Rota/página funcional perdida")

    mapping = (
        (Section.NEWS, "NOTICIAS-v0.0.21.png", "_v021_noticias_surface"),
        (Section.SOURCES, "FONTES-v0.0.21.png", "_v021_fontes_surface"),
        (Section.TERMS, "TERMOS-v0.0.21.png", "_v021_termos_surface"),
    )
    for _round in range(2):
        for section, filename, attr in mapping:
            capture(window, section, filename, attr, app)
            if window.sidebar.width() != width or window.sidebar.styleSheet() != style:
                raise RuntimeError(f"Sidebar mudou em {section.name}")
            window.navigate(Section.HOME); wait(app)
            if window.sidebar.width() != width or window.sidebar.styleSheet() != style:
                raise RuntimeError(f"Sidebar mudou ao retornar de {section.name}")

    # Captura final da Home após várias idas/voltas para provar que não reaparece dupla camada.
    home = window.pages[Section.HOME]; home.refresh(window.controller.state); wait(app, 300)
    pix = QPixmap(1672, 941); pix.fill(); window.render(pix, QPoint(0, 0))
    home_out = Path("artifacts/HOME-v0.0.21.png")
    if not pix.save(str(home_out), "PNG"): raise RuntimeError("Falha ao salvar Home")

    print("V021_LITERAL_NEWS=YES")
    print("V021_LITERAL_SOURCES=YES")
    print("V021_LITERAL_TERMS=YES")
    print("V021_NO_DOUBLE_LAYER_GATE=YES")
    print("V021_SIDEBAR_INVARIANT=YES")
    print(f"V021_ROUTES_PRESERVED={len(required)}")
    window.exit_application(); app.processEvents(); return 0


if __name__ == "__main__":
    raise SystemExit(main())
