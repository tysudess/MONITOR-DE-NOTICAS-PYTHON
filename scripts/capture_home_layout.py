from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from PySide6.QtWidgets import QApplication

from monitor_noticias.ui.main_window import MainWindow
from monitor_noticias.ui.sections import Section


def main() -> int:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window._timer.stop()
    window.resize(1721, 914)
    window.navigate(Section.HOME)
    window.show()
    app.processEvents()
    app.processEvents()

    out = Path("artifacts") / "home-1721x914.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pixmap = window.grab()
    if not pixmap.save(str(out), "PNG"):
        raise RuntimeError("Não foi possível salvar o screenshot da tela Início")

    print(f"HOME_SCREENSHOT={out.resolve()}")
    print(f"HOME_SIZE={window.width()}x{window.height()}")
    print(f"SIDEBAR_WIDTH={window.sidebar.width()}")
    print(f"VISIBLE_HOME_NAV={sum(1 for holder in window.nav_holders.values() if holder.isVisible())}")

    window.exit_application()
    app.processEvents()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
