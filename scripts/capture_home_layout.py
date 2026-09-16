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

from PySide6.QtCore import QEventLoop, QPoint, QTimer  # noqa: E402
from PySide6.QtGui import QFont, QPixmap  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from monitor_noticias.ui.main_window import MainWindow  # noqa: E402
from monitor_noticias.ui.sections import Section  # noqa: E402


def wait_ms(app: QApplication, ms: int) -> None:
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()
    app.processEvents()


def assert_shell(window, top, width, style, top_height, where: str) -> None:
    if window.sidebar.width() != width:
        raise RuntimeError(f"Sidebar mudou de largura em {where}: {window.sidebar.width()} != {width}")
    if window.sidebar.styleSheet() != style:
        raise RuntimeError(f"Sidebar mudou de estilo em {where}")
    if top is not None and top.height() != top_height:
        raise RuntimeError(f"Topbar mudou de altura em {where}: {top.height()} != {top_height}")


def assert_home_surface(home, section_name: str) -> None:
    surface = getattr(home, "_v019_truth_surface", None)
    if surface is None:
        raise RuntimeError(f"Home literal ausente após retorno de {section_name}")
    # A janela de captura não é exibida com show(); portanto isVisible() é falso
    # por herança do pai mesmo quando o widget foi explicitamente mostrado.
    # isHidden() testa o estado próprio correto neste cenário offscreen.
    if surface.isHidden():
        raise RuntimeError(f"Home literal ficou explicitamente oculta após retorno de {section_name}")
    if surface.geometry() != home.rect():
        raise RuntimeError(f"Home literal mudou de geometria após retorno de {section_name}")
    if surface.parentWidget() is not home:
        raise RuntimeError(f"Home literal perdeu o parent correto após retorno de {section_name}")


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
    wait_ms(app, 1100)

    baseline_width = window.sidebar.width()
    baseline_style = window.sidebar.styleSheet()
    baseline_top_height = top.height() if top is not None else 0
    if baseline_width != 225:
        raise RuntimeError(f"Sidebar v0.0.20 divergente: {baseline_width}, esperado 225")
    if baseline_top_height != 86:
        raise RuntimeError(f"Topbar v0.0.20 divergente: {baseline_top_height}, esperado 86")
    assert_home_surface(home, "INICIAL")

    # Gate: troca de aba + espera suficiente para callbacks tardios e retorno
    # à Home. Shell e superfície devem permanecer idênticos em todos os pontos.
    for section in (Section.NEWS, Section.DEMANDS, Section.SOURCES, Section.SETTINGS):
        window.navigate(section)
        wait_ms(app, 1100)
        assert_shell(window, top, baseline_width, baseline_style, baseline_top_height, section.name)
        window.navigate(Section.HOME)
        home.refresh(window.controller.state)
        wait_ms(app, 1100)
        assert_shell(window, top, baseline_width, baseline_style, baseline_top_height, f"RETORNO_{section.name}")
        assert_home_surface(home, section.name)

    required = {
        Section.HOME, Section.NEWS, Section.VIDEOS, Section.DEMANDS,
        Section.SOURCES, Section.HISTORY, Section.TERMS, Section.STOP,
        Section.PDF_EDITOR, Section.EXTRACTOR, Section.VIDEO_EDITOR,
        Section.NEWS_EXTRACTOR, Section.SHEET_AUTOMATION, Section.COVERS,
        Section.SETTINGS,
    }
    if not required.issubset(window.pages.keys()) or not required.issubset(window.nav_buttons.keys()):
        raise RuntimeError("v0.0.20 perdeu rota/página funcional existente")

    # Gate de dados vivos: os widgets funcionais continuam sendo atualizados e a
    # superfície visual existe para pintar esses valores sobre a referência.
    home.refresh(window.controller.state)
    wait_ms(app, 200)
    if not getattr(home, "module_cards", None) or not getattr(home, "live_values", None):
        raise RuntimeError("Widgets funcionais da Home não estão disponíveis para a camada de dados vivos")
    assert_home_surface(home, "FINAL")

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
    print("SIDEBAR_INVARIANT_AFTER_DELAY=YES")
    print("HOME_RETURN_INVARIANT=YES")
    print("HOME_LIVE_DATA_OVERLAY=YES")
    print(f"ROUTES_PRESERVED={len(required)}")
    print(f"HOME_CLASS={window.pages[Section.HOME].__class__.__name__}")

    window.exit_application()
    app.processEvents()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
