from pathlib import Path
import os
import sys
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("MONITOR_DISABLE_WEATHER", "1")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QScrollArea, QWidget
from monitor_noticias.ui.main_window import MainWindow
from monitor_noticias.ui.sections import SECTION_ORDER, Section


def _is_descendant(widget: QWidget, ancestor: QWidget) -> bool:
    current = widget
    while current is not None:
        if current is ancestor:
            return True
        current = current.parentWidget()
    return False


def main() -> int:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window._timer.stop()

    def wait_until(predicate, timeout: float = 25.0) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            app.processEvents()
            if predicate():
                return True
            time.sleep(0.05)
        app.processEvents()
        return bool(predicate())

    # Gates estruturais pedidos nesta revisão.
    if SECTION_ORDER[-1] is not Section.SETTINGS:
        raise RuntimeError("Configurações deixou de ser a última aba lateral.")
    sidebar_scroll = window.sidebar.findChild(QScrollArea, "sidebarScroll")
    if sidebar_scroll is None:
        raise RuntimeError("Barra lateral não possui QScrollArea.")
    if sidebar_scroll.verticalScrollBarPolicy() != Qt.ScrollBarPolicy.ScrollBarAsNeeded:
        raise RuntimeError("Scroll vertical da barra lateral não está habilitado sob demanda.")

    # Gate funcional: trocar de seção não pode derrubar o estado maximizado.
    window.showMaximized()
    app.processEvents()
    window.navigate(Section.NEWS)
    app.processEvents()
    app.processEvents()
    if not window.isMaximized():
        raise RuntimeError("Troca de aba removeu o estado maximizado da janela principal.")

    window.showNormal()
    window.resize(1721, 914)
    window.show()
    app.processEvents()

    out_dir = ROOT / "artifacts" / "refined-ui"
    out_dir.mkdir(parents=True, exist_ok=True)
    targets = [
        (Section.HOME, "inicio"),
        (Section.NEWS, "noticias"),
        (Section.VIDEOS, "videos"),
        (Section.DEMANDS, "demandas"),
        (Section.SOURCES, "fontes"),
        (Section.HISTORY, "historico"),
        (Section.TERMS, "termos"),
        (Section.PDF_EDITOR, "editor-pdf"),
        (Section.EXTRACTOR, "extrator-videos"),
        (Section.VIDEO_EDITOR, "editor-video"),
        (Section.NEWS_EXTRACTOR, "extrator-noticias"),
        (Section.SHEET_AUTOMATION, "automacao-planilhas"),
        (Section.COVERS, "capas"),
        (Section.SETTINGS, "configuracoes"),
    ]
    for section, name in targets:
        window.navigate(section)
        window.pages[section].refresh(window.controller.state)
        # Atualiza relógio, status de proxy/automação, badge e rodapé sem
        # depender do QTimer; o clima permanece desabilitado no gate visual.
        window._tick()
        app.processEvents()
        app.processEvents()

        if section == Section.VIDEO_EDITOR:
            video_page = window.pages[section]
            if video_page.editor is not None:
                if video_page.editor.isWindow():
                    raise RuntimeError("Editor de Vídeo voltou a abrir como janela top-level.")
                if not _is_descendant(video_page.editor, video_page):
                    raise RuntimeError("Editor de Vídeo não está incorporado à página rolável do Monitor.")
                scroll = video_page.findChild(QScrollArea)
                if scroll is None or scroll.verticalScrollBarPolicy() != Qt.ScrollBarPolicy.ScrollBarAsNeeded:
                    raise RuntimeError("Editor de Vídeo não possui scroll vertical sob demanda.")

        if section in (Section.NEWS_EXTRACTOR, Section.SHEET_AUTOMATION):
            page = window.pages[section]
            disabled = os.environ.get("MONITOR_DISABLE_EXTERNAL_INTEGRATIONS") == "1"
            if page.executable.is_file() and not disabled:
                if not wait_until(lambda p=page: bool(p._hwnd) and p._is_window(p._hwnd)):
                    raise RuntimeError(f"{section.value.label} não abriu/incorporou sua janela original.")

        if section == Section.COVERS:
            page = window.pages[section]
            source_exists = (ROOT / "resources" / "integrations" / "capas" / "source" / "app" / "ui.py").is_file()
            if source_exists and page.window is None:
                raise RuntimeError("Capas original não foi incorporado ao Monitor.")

        path = out_dir / f"{name}-1721x914.png"
        if not window.grab().save(str(path), "PNG"):
            raise RuntimeError(f"Falha ao salvar {path}")
        print(f"SCREENSHOT={section.name}:{path}")

    print(f"WINDOW={window.width()}x{window.height()}")
    print(f"SIDEBAR={window.sidebar.width()}")
    window.exit_application()
    app.processEvents()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
