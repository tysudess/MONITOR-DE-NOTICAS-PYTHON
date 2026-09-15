from __future__ import annotations

from pathlib import Path
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("MONITOR_DISABLE_EXTERNAL_INTEGRATIONS", "1")
os.environ.setdefault("MONITOR_DISABLE_WEATHER", "1")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import run  # noqa: F401 - instala a cadeia real de overlays.
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFrame, QLabel, QScrollArea

from monitor_noticias.app.paths import AppPaths
from monitor_noticias.ui.main_window import MainWindow
from monitor_noticias.ui.sections import SECTION_ORDER, Section


EXPECTED_HEADERS = ["PRINCIPAL", "GERENCIAMENTO", "FERRAMENTAS", "SISTEMA"]


def _layout_headers(scroll: QScrollArea) -> list[str]:
    content = scroll.widget()
    layout = content.layout() if content is not None else None
    if layout is None:
        return []
    titles: list[str] = []
    for index in range(layout.count()):
        widget = layout.itemAt(index).widget()
        if isinstance(widget, QFrame) and widget.objectName() == "sideGroupHeader":
            label = widget.findChild(QLabel, "sideGroupTitle")
            if label is not None:
                titles.append(label.text())
    return titles


def _assert_sidebar(window: MainWindow) -> None:
    scroll = window.sidebar.findChild(QScrollArea, "sidebarScroll")
    if scroll is None:
        raise RuntimeError("sidebarScroll ausente")
    if scroll.horizontalScrollBarPolicy() != Qt.ScrollBarPolicy.ScrollBarAlwaysOff:
        raise RuntimeError("sidebar ganhou scroll horizontal")
    if scroll.verticalScrollBarPolicy() != Qt.ScrollBarPolicy.ScrollBarAsNeeded:
        raise RuntimeError("scroll vertical deixou de ser sob demanda")

    titles = _layout_headers(scroll)
    if titles != EXPECTED_HEADERS:
        raise RuntimeError(f"cabeçalhos laterais divergentes: {titles}")

    if tuple(window.nav_buttons) != SECTION_ORDER:
        raise RuntimeError("ordem da navegação foi alterada")
    if any(button.icon().isNull() for button in window.nav_buttons.values()):
        raise RuntimeError("ícone lateral ausente")
    if len({button.height() for button in window.nav_buttons.values()}) != 1:
        raise RuntimeError("botões laterais com alturas diferentes")


def _capture(window: MainWindow, app: QApplication, section: Section, name: str, width: int, height: int) -> Path:
    window.showNormal()
    window.resize(width, height)
    window.show()
    window.navigate(section)
    window._tick()
    app.processEvents()
    app.processEvents()
    _assert_sidebar(window)

    active = [sec for sec, button in window.nav_buttons.items() if button.isChecked()]
    if active != [section]:
        raise RuntimeError(f"estado ativo divergente em {section.name}: {active}")
    if any("❯" in button.text() for button in window.nav_buttons.values()):
        raise RuntimeError("seta textual legada permaneceu na sidebar")

    out = ROOT / "artifacts" / "sidebar-v013"
    out.mkdir(parents=True, exist_ok=True)
    path = out / name
    if not window.sidebar.grab().save(str(path), "PNG"):
        raise RuntimeError(f"falha ao capturar {path}")
    print(f"SIDEBAR_SCREENSHOT={section.name}:{path}:{window.sidebar.width()}x{window.sidebar.height()}")
    return path


def main() -> int:
    app = QApplication.instance() or QApplication([])
    window = MainWindow(paths=AppPaths.discover())
    window._timer.stop()

    try:
        # Captura alta: permite comparar toda a hierarquia com a referência vertical.
        _capture(window, app, Section.VIDEOS, "sidebar-reference-videos-318x1900.png", 1400, 1900)

        # Captura compacta: valida que a sidebar continua utilizável com scroll interno.
        _capture(window, app, Section.HOME, "sidebar-compact-home-318x768.png", 1366, 768)
        scroll = window.sidebar.findChild(QScrollArea, "sidebarScroll")
        if scroll is None or scroll.verticalScrollBar().maximum() <= 0:
            raise RuntimeError("sidebar compacta não ativou scroll vertical")

        # Confere dinamicamente todas as páginas sem trocar callbacks nem rotas.
        for section in SECTION_ORDER:
            window.navigate(section)
            app.processEvents()
            checked = [sec for sec, button in window.nav_buttons.items() if button.isChecked()]
            if checked != [section]:
                raise RuntimeError(f"item ativo incorreto em {section.name}: {checked}")
            if window.stack.currentIndex() != SECTION_ORDER.index(section):
                raise RuntimeError(f"stack incorreto em {section.name}")

        print("V013_SIDEBAR_VISUAL_GATE_OK=YES")
        return 0
    finally:
        window._allow_close = True
        window.close()
        app.processEvents()


if __name__ == "__main__":
    raise SystemExit(main())
