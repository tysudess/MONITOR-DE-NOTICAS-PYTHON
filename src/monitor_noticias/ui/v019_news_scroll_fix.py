from __future__ import annotations

"""Corrige a rolagem da lista de Notícias da referência v0.0.19.

Mantém filtros, busca, cards e paginação existentes; apenas aumenta a quantidade
de resultados por página e garante uma barra vertical visível na área da lista.
"""

from PySide6.QtCore import Qt

_INSTALLED = False


def install_v019_news_scroll_fix() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    from monitor_noticias.ui.refined_search import NewsPage

    old_init = NewsPage.__init__

    def init(self, controller) -> None:
        old_init(self, controller)
        self._page_size = 25
        scroll = getattr(self, "scroll", None)
        if scroll is not None:
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll.setMinimumHeight(260)
        self._signature = None

    NewsPage.__init__ = init
