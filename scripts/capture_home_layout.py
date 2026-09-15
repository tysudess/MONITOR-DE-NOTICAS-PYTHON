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
    app.setFont(QFont("Segoe UI", 9))
    window = MainWindow()
    window._timer.stop()
    window.navigate(Section.HOME)

    # Renderização direta do widget evita que o desktop 1366x768 do runner
    # limite a janela; a referência enviada pelo usuário mede exatamente 1672x941.
    window.resize(1672, 941)
    window.ensurePolished()
    if window.layout() is not None:
        window.layout().activate()
    top = getattr(window, "reference_top_bar", None)
    if top is not None:
        top.sync()
    home = window.pages[Section.HOME]
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
    print(f"VISIBLE_HOME_NAV={sum(1 for holder in window.nav_holders.values() if holder.isVisible())}")
    print(f"HOME_CLASS={window.pages[Section.HOME].__class__.__name__}")

    window.exit_application()
    app.processEvents()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
