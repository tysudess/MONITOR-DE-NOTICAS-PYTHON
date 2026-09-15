from __future__ import annotations

"""Refino exclusivamente visual da Home v0.0.17.

Não altera controller, callbacks, rotas ou motores. Ajusta somente dimensões e
visibilidade de decoração compartilhada enquanto a seção HOME está ativa.
"""

from PySide6.QtWidgets import QFrame

_INSTALLED = False


def _refine_home_page(page) -> None:
    from monitor_noticias.ui.v017_home_truth import ReferenceHero, ModuleCard

    hero = page.findChild(ReferenceHero)
    if hero is not None:
        hero.setMinimumHeight(155)
        hero.setMaximumHeight(155)

    for card in page.findChildren(ModuleCard):
        card.setMinimumHeight(150)
        card.setMaximumHeight(150)
        card.setMinimumWidth(0)

    panels = page.findChildren(QFrame, "homePanel")
    # Ordem de criação: quatro painéis intermediários e dois painéis inferiores.
    for panel in panels[:4]:
        panel.setMinimumHeight(200)
        panel.setMaximumHeight(200)
    for panel in panels[4:6]:
        panel.setMinimumHeight(264)
        panel.setMaximumHeight(264)

    body = getattr(page, "body", None)
    if body is not None:
        body.setContentsMargins(12, 8, 12, 4)
        body.setSpacing(10)


def _home_shell(window, active: bool) -> None:
    top = getattr(window, "reference_top_bar", None)
    sidebar = getattr(window, "sidebar", None)

    if active:
        if top is not None:
            top.setFixedHeight(86)
        if sidebar is not None:
            sidebar.setFixedWidth(225)
            # Os cabeçalhos de grupos são decoração herdada e não aparecem na
            # imagem-verdade. Os botões/rotas permanecem todos vivos e acessíveis.
            for group in sidebar.findChildren(QFrame, "sideGroupHeader"):
                group.hide()
    else:
        if top is not None:
            top.setFixedHeight(76)
        if sidebar is not None:
            sidebar.setFixedWidth(220)
            for group in sidebar.findChildren(QFrame, "sideGroupHeader"):
                group.show()


def install_v017_home_truth_refine() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    from monitor_noticias.ui.main_window import MainWindow
    from monitor_noticias.ui.sections import Section

    old_build = MainWindow._build_ui
    old_nav = MainWindow.navigate

    def build(self):
        old_build(self)
        page = self.pages.get(Section.HOME)
        if page is not None:
            _refine_home_page(page)
        _home_shell(self, getattr(self, "_current", None) == Section.HOME)

    def navigate(self, section):
        old_nav(self, section)
        page = self.pages.get(Section.HOME)
        if page is not None:
            _refine_home_page(page)
        _home_shell(self, section == Section.HOME)

    MainWindow._build_ui = build
    MainWindow.navigate = navigate
