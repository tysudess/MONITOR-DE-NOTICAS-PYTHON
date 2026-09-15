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

# Importar run instala, na mesma ordem do executável real, todos os overlays
# preservados e por último o shell visual v0.0.14.
import run  # noqa: F401,E402

from PySide6.QtWidgets import QApplication, QLineEdit
from monitor_noticias.ui.main_window import MainWindow
from monitor_noticias.ui.sections import Section


def main() -> int:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window._timer.stop()
    window.resize(1600, 900)
    window.show()
    app.processEvents()

    if window.sidebar.width() != 220:
        raise RuntimeError(f"Sidebar divergente da referência: {window.sidebar.width()} px")
    top = getattr(window, "reference_top_bar", None)
    if top is None or not top.isVisible():
        raise RuntimeError("Barra global v0.0.14 ausente.")
    global_search = top.findChild(QLineEdit, "referenceGlobalSearch")
    if global_search is None:
        raise RuntimeError("Busca global real não foi construída.")

    out = ROOT / "artifacts" / "v014-reference"
    out.mkdir(parents=True, exist_ok=True)
    targets = (
        (Section.HOME, "inicio"),
        (Section.NEWS, "noticias"),
        (Section.DEMANDS, "demandas"),
        (Section.SOURCES, "fontes"),
        (Section.TERMS, "termos"),
        (Section.SETTINGS, "configuracoes"),
        (Section.COVERS, "capas"),
        (Section.PDF_EDITOR, "editor-pdf"),
        (Section.EXTRACTOR, "extrator-videos"),
        (Section.VIDEO_EDITOR, "editor-video"),
    )
    for section, name in targets:
        window.navigate(section)
        window._tick()
        app.processEvents()
        path = out / f"{name}-1600x900.png"
        if not window.grab().save(str(path), "PNG"):
            raise RuntimeError(f"Falha ao salvar {path}")
        print(f"SCREENSHOT={section.name}:{path}")

    # O campo global filtra usando o query já existente; não dispara motores.
    window.navigate(Section.HOME)
    global_search.setText("teste visual")
    global_search.returnPressed.emit()
    app.processEvents()
    if window._current is not Section.NEWS:
        raise RuntimeError("Busca global não roteou para a tela Notícias.")
    news_query = getattr(window.pages[Section.NEWS], "query", None)
    if news_query is None or news_query.text() != "teste visual":
        raise RuntimeError("Busca global não reutilizou o campo real de Notícias.")

    window._allow_close = True
    window.close()
    app.processEvents()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
