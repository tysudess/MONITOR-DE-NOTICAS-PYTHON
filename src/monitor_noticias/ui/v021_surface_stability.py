from __future__ import annotations

"""Estabilidade geométrica das superfícies literais v0.0.21.

Não altera páginas, dados ou callbacks. Apenas mantém as superfícies visuais
finais com a mesma geometria da página quando a janela é redimensionada.
"""

from PySide6.QtCore import QTimer

_INSTALLED = False


def install_v021_surface_stability() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    from monitor_noticias.ui.main_window import MainWindow
    from monitor_noticias.ui.v021_literal_tabs import _refresh_surfaces

    old_build = MainWindow._build_ui

    def build(self):
        old_build(self)
        timer = QTimer(self)
        timer.setInterval(750)
        timer.timeout.connect(lambda w=self: _refresh_surfaces(w))
        timer.start()
        self._v021_surface_timer = timer
        _refresh_surfaces(self)

    MainWindow._build_ui = build
