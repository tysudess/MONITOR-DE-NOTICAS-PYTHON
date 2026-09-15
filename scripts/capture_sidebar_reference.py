from __future__ import annotations

from pathlib import Path
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("MONITOR_DISABLE_WEATHER", "1")
os.environ.setdefault("MONITOR_DISABLE_EXTERNAL_INTEGRATIONS", "1")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Importar run instala os overlays na mesma ordem do executável real.
import run  # noqa: F401,E402

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QScrollArea
from monitor_noticias.ui.main_window import MainWindow
from monitor_noticias.ui.sections import SECTION_ORDER, Section


def main() -> int:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window._timer.stop()
    window.show()
    app.processEvents()

    if window.sidebar.width() != 318:
        raise RuntimeError(f"Largura inesperada da sidebar: {window.sidebar.width()}")

    scroll = window.sidebar.findChild(QScrollArea, "sidebarScroll")
    if scroll is None:
        raise RuntimeError("sidebarScroll ausente")
    if scroll.horizontalScrollBarPolicy() != Qt.ScrollBarPolicy.ScrollBarAlwaysOff:
        raise RuntimeError("Sidebar ganhou scroll horizontal")
    if scroll.verticalScrollBarPolicy() != Qt.ScrollBarPolicy.ScrollBarAsNeeded:
        raise RuntimeError("Scroll vertical não está sob demanda")

    # Valida os cabeçalhos que pertencem ao layout final. Objetos legados já
    # retirados do layout podem aguardar deleteLater e não representam duplicação visual.
    content = scroll.widget()
    side_layout = content.layout() if content is not None else None
    groups = []
    if side_layout is not None:
        for index in range(side_layout.count()):
            widget = side_layout.itemAt(index).widget()
            if widget is not None and widget.objectName() == "sideGroupHeader":
                label = widget.findChild(QLabel, "sideGroupTitle")
                if label is not None:
                    groups.append(label.text())
    if groups != ["PRINCIPAL", "GERENCIAMENTO", "FERRAMENTAS", "SISTEMA"]:
        raise RuntimeError(f"Categorias no layout divergentes: {groups}")

    if tuple(window.nav_buttons) != SECTION_ORDER:
        raise RuntimeError("Ordem dos botões divergiu de SECTION_ORDER")

    for section in SECTION_ORDER:
        window.navigate(section)
        app.processEvents()
        checked = [sec for sec, button in window.nav_buttons.items() if button.isChecked()]
        if checked != [section]:
            raise RuntimeError(f"Estado ativo inválido em {section.name}: {checked}")
        button = window.nav_buttons[section]
        if button.text() != section.value.label:
            raise RuntimeError(f"Texto visual divergente em {section.name}: {button.text()!r}")
        if button.height() != 54:
            raise RuntimeError(f"Altura divergente em {section.name}: {button.height()}")

    # Confirma que o card continua consumindo os estados reais do controller.
    window._tick()
    app.processEvents()
    cfg = window.controller.proxy_config
    auto = window.controller.automation_settings
    state = window.controller.state
    if cfg.status_label not in window.side_proxy.text():
        raise RuntimeError("Status de proxy deixou de refletir o controller")
    expected_auto = "ativa" if auto.automatic_monitoring else "pausada"
    if expected_auto not in window.side_automation.text():
        raise RuntimeError("Status de automação deixou de refletir o controller")
    expected_search = "Busca em andamento" if (state.news_busy or state.video_busy) else "Sistema operacional"
    if window.side_status_title.text() != expected_search:
        raise RuntimeError("Status de busca deixou de refletir o estado real")

    style = window.sidebar.styleSheet()
    for token in ("#FAC305", "#EDB707", "#164A6E", "#EAEDF1", "border-left:7px solid #FAC305"):
        if token not in style:
            raise RuntimeError(f"Token visual obrigatório ausente: {token}")

    out = ROOT / "artifacts" / "sidebar-reference"
    out.mkdir(parents=True, exist_ok=True)
    for width, height, name in ((1600, 1000, "sidebar-1600x1000.png"), (1366, 768, "sidebar-1366x768.png"), (1400, 1800, "sidebar-full-height.png")):
        window.resize(width, height)
        window.navigate(Section.VIDEOS)
        app.processEvents(); app.processEvents()
        path = out / name
        if not window.sidebar.grab().save(str(path), "PNG"):
            raise RuntimeError(f"Falha ao salvar {path}")
        print(f"SCREENSHOT={path}")

    window.exit_application()
    app.processEvents()
    print("SIDEBAR_REFERENCE_GATE=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
