from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "windows")
os.environ.setdefault("MONITOR_DISABLE_WEATHER", "1")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for entry in (ROOT, SRC):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

import run as _runtime_bootstrap  # noqa: F401,E402

from PySide6.QtCore import QPoint  # noqa: E402
from PySide6.QtGui import QFont, QPixmap  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from monitor_noticias.ui.main_window import MainWindow  # noqa: E402
from monitor_noticias.ui.sections import Section  # noqa: E402


def main() -> int:
    app = QApplication.instance() or QApplication([])
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow()
    window._timer.stop()
    window.resize(1672, 941)
    window.navigate(Section.HOME)
    window.ensurePolished()
    if window.layout() is not None:
        window.layout().activate()
    top = getattr(window, "reference_top_bar", None)
    if top is not None:
        top.sync()
    home = window.pages[Section.HOME]
    home.refresh(window.controller.state)
    app.processEvents()

    # Gate v0.0.19: shell não pode mudar ao trocar de aba.
    baseline_width = window.sidebar.width()
    baseline_style = window.sidebar.styleSheet()
    baseline_top_height = top.height() if top is not None else 0
    if baseline_width != 225:
        raise RuntimeError(f"Sidebar v0.0.19 divergente: {baseline_width}, esperado 225")
    if baseline_top_height != 86:
        raise RuntimeError(f"Topbar v0.0.19 divergente: {baseline_top_height}, esperado 86")

    for section in (Section.NEWS, Section.DEMANDS, Section.SOURCES, Section.SETTINGS):
        window.navigate(section)
        app.processEvents()
        if window.sidebar.width() != baseline_width:
            raise RuntimeError(f"Sidebar mudou de largura em {section.name}")
        if window.sidebar.styleSheet() != baseline_style:
            raise RuntimeError(f"Sidebar mudou de estilo em {section.name}")
        if top is not None and top.height() != baseline_top_height:
            raise RuntimeError(f"Topbar mudou de altura em {section.name}")

    # Todas as rotas históricas continuam presentes.
    required = {
        Section.HOME, Section.NEWS, Section.VIDEOS, Section.DEMANDS,
        Section.SOURCES, Section.HISTORY, Section.TERMS, Section.STOP,
        Section.PDF_EDITOR, Section.EXTRACTOR, Section.VIDEO_EDITOR,
        Section.NEWS_EXTRACTOR, Section.SHEET_AUTOMATION, Section.COVERS,
        Section.SETTINGS,
    }
    if not required.issubset(window.pages.keys()) or not required.issubset(window.nav_buttons.keys()):
        raise RuntimeError("v0.0.19 perdeu rota/página funcional existente")

    window.navigate(Section.HOME)
    home.refresh(window.controller.state)
    app.processEvents()

    canvas = QPixmap(1672, 941)
    canvas.fill()
    window.render(canvas, QPoint(0, 0))

    out = Path("artifacts") / "home-reference-1672x941.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    if not canvas.save(str(out), "PNG"):
        raise RuntimeError("Não foi possível salvar o screenshot da tela Início")

    print(f"HOME_SCREENSHOT={out.resolve()}")
    print("HOME_SIZE=1672x941")
    print(f"SIDEBAR_WIDTH={window.sidebar.width()}")
    print(f"TOPBAR_HEIGHT={baseline_top_height}")
    print("SIDEBAR_INVARIANT=YES")
    print(f"ROUTES_PRESERVED={len(required)}")
    print(f"HOME_CLASS={window.pages[Section.HOME].__class__.__name__}")

    window.exit_application()
    app.processEvents()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
