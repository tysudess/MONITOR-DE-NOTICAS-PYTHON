from __future__ import annotations

"""Limpeza final da camada literal v0.0.19.

Remove somente a pintura duplicada dos botões nativos sobre a sidebar da
imagem-verdade. Os QPushButtons continuam existentes, clicáveis e ligados às
mesmas rotas.
"""

from PySide6.QtGui import QIcon

_INSTALLED = False


def _clean(window) -> None:
    from monitor_noticias.ui.sections import Section

    primary = {
        Section.HOME, Section.NEWS, Section.VIDEOS, Section.DEMANDS,
        Section.SOURCES, Section.HISTORY, Section.TERMS, Section.COVERS,
        Section.PDF_EDITOR, Section.EXTRACTOR, Section.VIDEO_EDITOR,
    }
    for section in primary:
        button = getattr(window, "nav_buttons", {}).get(section)
        if button is None:
            continue
        button.setText("")
        button.setIcon(QIcon())
        button.setStyleSheet(
            "QPushButton{background:transparent;color:transparent;border:0;padding:0;}"
            "QPushButton:hover,QPushButton:checked,QPushButton:pressed{background:transparent;color:transparent;border:0;}"
        )


def install_v019_literal_cleanup() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True
    from monitor_noticias.ui.main_window import MainWindow
    old_build = MainWindow._build_ui
    old_nav = MainWindow.navigate

    def build(self):
        old_build(self)
        _clean(self)

    def navigate(self, section):
        old_nav(self, section)
        _clean(self)

    MainWindow._build_ui = build
    MainWindow.navigate = navigate
