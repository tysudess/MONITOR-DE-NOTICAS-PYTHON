from __future__ import annotations

"""v0.0.19 — fidelidade literal da Home e sidebar global.

Esta camada é exclusivamente visual. Não substitui controller, banco, coletores,
rotas, callbacks, páginas de ferramentas ou motores. A imagem fornecida pelo
usuário é usada literalmente no hero; os demais widgets permanecem reais.
"""

import base64
import sys
from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget

_INSTALLED = False
_HERO_PIXMAP: QPixmap | None = None


SIDEBAR_V019 = """
QFrame#sidebar {
    background:#031a2d;
    border:0;
    border-right:1px solid #064b70;
    border-radius:0;
}
QLabel#anchorMark {
    color:#ffc400;
    font-family:'Segoe UI Symbol';
    font-size:45px;
    font-weight:800;
}
QLabel#brandTitle { color:#f5f7ff; font-size:17px; font-weight:800; letter-spacing:.5px; }
QLabel#brandSub { color:#7facc8; font-size:10px; }
QPushButton#navButton {
    color:#eef3ff;
    background:transparent;
    border:0;
    border-radius:10px;
    padding:10px 11px;
    text-align:left;
    font-size:12px;
    font-weight:500;
}
QPushButton#navButton:hover { background:#052c49; }
QPushButton#navButton:checked {
    color:#ffffff;
    font-weight:800;
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #075f91,stop:.48 #063c61,stop:1 #042a48);
    border:1px solid #00cfff;
    border-left:6px solid #00e5ff;
}
QLabel#newsBadge { background:transparent; color:transparent; border:0; min-width:0; max-width:0; }
QFrame#sideGroupHeader { background:transparent; border:0; max-height:0; min-height:0; }
QScrollArea#sidebarScroll { background:transparent; border:0; }
QScrollArea#sidebarScroll > QWidget > QWidget { background:transparent; }
QScrollBar:vertical { width:0; background:transparent; }
"""

TOPBAR_V019 = """
QFrame#referenceTopBar { background:#03182b; border:0; border-bottom:1px solid #07557d; }
QLineEdit#globalSearch {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #06233c,stop:.78 #082449,stop:1 #1b2860);
    color:#f4f7ff; border:1px solid #1688c8; border-radius:13px; padding:0 16px;
    font-size:12px; selection-background-color:#1378ad;
}
QLineEdit#globalSearch:focus { border:1px solid #7568ff; }
QFrame#topStatusGood { background:#073a38; border:1px solid #00a888; border-radius:11px; }
QLabel#topStatusText { color:#f4ffff; font-size:10px; font-weight:700; }
QLabel#topStatusDot { color:#00e3a8; font-size:17px; }
QPushButton#topBell { color:#e9f3ff; background:#071f3c; border:1px solid #164f78; border-radius:11px; font-size:20px; }
QFrame#topClock { background:#041d34; border:1px solid #0d547c; border-radius:13px; }
QLabel#topDate { color:#9fbad0; font-size:9px; }
QLabel#topTime { color:#ffffff; font-size:16px; font-weight:800; }
QLabel#topWeatherIcon { color:#ffd329; font-size:28px; }
QLabel#topWeatherPlace { color:#a6bfd2; font-size:9px; }
QLabel#topWeatherTemp { color:#ffffff; font-size:15px; font-weight:800; }
"""

HOME_FONT_PATCH = """
QWidget#referenceHome, QWidget#referenceHomeBody { background:#03172a; }
QLabel[role='heroTitle'] { font-size:30px; font-weight:800; color:#ffffff; }
QLabel[role='heroSub'] { font-size:12px; color:#c1d3e8; }
QLabel[role='cardTitle'] { font-size:12px; font-weight:800; color:#ffffff; }
QLabel[role='cardValue'] { font-size:20px; font-weight:800; color:#ffffff; }
QLabel[role='cardSub'] { font-size:10px; color:#abc1d7; }
QLabel[role='panelTitle'] { font-size:12px; font-weight:800; color:#f7fbff; }
QLabel[role='panelLink'] { font-size:9px; color:#17c9ff; }
QLabel[role='smallText'] { font-size:10px; color:#dce8f4; }
QLabel[role='tinyText'] { font-size:9px; color:#a9bfd3; }
QLabel[role='metricCaption'] { font-size:9px; color:#a9bfd3; }
QLabel[role='activePill'] { font-size:9px; font-weight:800; }
QLabel[role='footerText'], QLabel[role='footerRight'] { font-size:9px; }
"""


def _resource_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "resources"
    return Path(__file__).resolve().parents[3] / "resources"


def _hero_pixmap() -> QPixmap:
    global _HERO_PIXMAP
    if _HERO_PIXMAP is not None and not _HERO_PIXMAP.isNull():
        return _HERO_PIXMAP
    encoded = _resource_root() / "ui" / "v019" / "home-hero.webp.b64"
    raw = base64.b64decode(encoded.read_text(encoding="ascii").strip())
    pix = QPixmap()
    if not pix.loadFromData(raw, "WEBP"):
        raise RuntimeError("Imagem-verdade do hero v0.0.19 não pôde ser carregada")
    _HERO_PIXMAP = pix
    return pix


def _paint_exact_hero(self, event) -> None:
    p = QPainter(self)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    p.drawPixmap(QRectF(0, 0, self.width(), self.height()), _hero_pixmap(), QRectF(0, 0, 1447, 155))


def _style_home(page) -> None:
    from monitor_noticias.ui.v017_home_truth import ModuleCard, ReferenceHero

    page.setStyleSheet(page.styleSheet() + HOME_FONT_PATCH)
    body = getattr(page, "body", None)
    if body is not None:
        body.setContentsMargins(12, 8, 12, 4)
        body.setSpacing(10)
    hero = page.findChild(ReferenceHero)
    if hero is not None:
        hero.setFixedHeight(155)
    for card in page.findChildren(ModuleCard):
        card.setFixedHeight(150)
        card.setMinimumWidth(0)
        title = getattr(card, "title", None)
        value = getattr(card, "value", None)
        subtitle = getattr(card, "subtitle", None)
        if isinstance(title, QLabel): title.setStyleSheet("color:#fff;font-size:12px;font-weight:800;")
        if isinstance(value, QLabel): value.setStyleSheet("color:#fff;font-size:20px;font-weight:800;")
        if isinstance(subtitle, QLabel): subtitle.setStyleSheet("color:#aac0d6;font-size:10px;")
    panels = page.findChildren(QFrame, "homePanel")
    for panel in panels[:4]: panel.setFixedHeight(200)
    for panel in panels[4:6]: panel.setFixedHeight(282)
    for label in page.findChildren(QLabel):
        f = label.font()
        if f.pointSizeF() > 0 and f.pointSizeF() < 9.5:
            f.setPointSizeF(9.5)
            label.setFont(f)


def _sidebar_layout(window):
    sidebar = getattr(window, "sidebar", None)
    if sidebar is None: return None, None
    scroll = sidebar.findChild(QScrollArea, "sidebarScroll")
    content = scroll.widget() if scroll is not None else None
    layout = content.layout() if content is not None else None
    return scroll, layout if isinstance(layout, QVBoxLayout) else None


def _arrange_global_sidebar(window) -> None:
    from monitor_noticias.ui.main_window import SidebarShipArt
    from monitor_noticias.ui.sections import Section

    sidebar = getattr(window, "sidebar", None)
    if sidebar is None: return
    sidebar.setFixedWidth(225)
    sidebar.setStyleSheet(SIDEBAR_V019)
    scroll, layout = _sidebar_layout(window)
    if scroll is not None:
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    if layout is not None:
        layout.setContentsMargins(9, 10, 9, 8)
        layout.setSpacing(3)

        groups = [w for w in sidebar.findChildren(QFrame) if w.objectName() == "sideGroupHeader"]
        for group in groups:
            group.hide(); group.setFixedHeight(0)

        holders = list(getattr(window, "nav_holders", {}).values())
        current_indices = [layout.indexOf(w) for w in holders if layout.indexOf(w) >= 0]
        base = min(current_indices) if current_indices else 2
        for holder in holders:
            layout.removeWidget(holder)

        primary = (
            Section.HOME, Section.NEWS, Section.VIDEOS, Section.DEMANDS,
            Section.SOURCES, Section.HISTORY, Section.TERMS, Section.COVERS,
            Section.PDF_EDITOR, Section.EXTRACTOR, Section.VIDEO_EDITOR,
        )
        extra = (Section.NEWS_EXTRACTOR, Section.SHEET_AUTOMATION, Section.STOP, Section.SETTINGS)
        pos = base
        for section in primary:
            holder = window.nav_holders.get(section)
            if holder is not None:
                holder.show(); holder.setFixedHeight(46); layout.insertWidget(pos, holder); pos += 1
        spacer = getattr(window, "_v019_extra_spacer", None)
        if spacer is None:
            spacer = QWidget(); spacer.setFixedHeight(76); spacer.setStyleSheet("background:transparent;")
            window._v019_extra_spacer = spacer
        if layout.indexOf(spacer) >= 0: layout.removeWidget(spacer)
        layout.insertWidget(pos, spacer); pos += 1
        for section in extra:
            holder = window.nav_holders.get(section)
            if holder is not None:
                holder.show(); holder.setFixedHeight(46); layout.insertWidget(pos, holder); pos += 1

    for button in getattr(window, "nav_buttons", {}).values():
        button.setFixedHeight(46)
        font = button.font(); font.setPointSizeF(10.5); button.setFont(font)
    badge = getattr(window, "news_badge", None)
    if badge is not None: badge.hide()
    card = getattr(window, "side_status_card", None)
    if card is not None: card.hide(); card.setFixedHeight(0)
    for ship in sidebar.findChildren(SidebarShipArt): ship.hide(); ship.setFixedHeight(0)
    for label in sidebar.findChildren(QLabel):
        if label.objectName() == "sideMotto" or label.text().strip() == "━━": label.hide()

    footer = getattr(window, "_home_sidebar_footer", None)
    if footer is not None:
        footer.show(); footer.setFixedHeight(240)
        footer.setStyleSheet("QFrame#homeSidebarFooter{background:#03182a;border:0;border-top:1px solid #073d5c;} QLabel{background:transparent;border:0;color:#a9c3d8;font-size:10px;}")


def _style_global_topbar(window) -> None:
    top = getattr(window, "reference_top_bar", None)
    if top is None: return
    top.setFixedHeight(86)
    top.setStyleSheet(TOPBAR_V019)
    search = getattr(top, "search", None)
    if isinstance(search, QLineEdit):
        search.setMinimumWidth(650); search.setMaximumWidth(720); search.setFixedHeight(48)
        search.setPlaceholderText("⌕   Buscar notícias, fontes, demandas... ou digite um comando (Ctrl + K)")
    for button in (getattr(top, "bell", None),):
        if isinstance(button, QPushButton): button.setFixedSize(48, 48)


def _apply_global_shell(window) -> None:
    _arrange_global_sidebar(window)
    _style_global_topbar(window)
    header = getattr(window, "header_widget", None)
    if header is not None: header.hide(); header.setMaximumHeight(0)
    footer = getattr(window, "footer_widget", None)
    if footer is not None: footer.hide(); footer.setMaximumHeight(0)


def install_v019_exact_reference() -> None:
    global _INSTALLED
    if _INSTALLED: return
    _INSTALLED = True

    from monitor_noticias.ui.main_window import MainWindow
    from monitor_noticias.ui.sections import Section
    from monitor_noticias.ui.v017_home_truth import ReferenceHero

    # A imagem não é redesenhada: o crop da referência é pintado literalmente.
    ReferenceHero.paintEvent = _paint_exact_hero

    old_build = MainWindow._build_ui
    old_nav = MainWindow.navigate

    def build(self):
        old_build(self)
        page = self.pages.get(Section.HOME)
        if page is not None: _style_home(page)
        _apply_global_shell(self)

    def navigate(self, section):
        old_nav(self, section)
        page = self.pages.get(Section.HOME)
        if page is not None: _style_home(page)
        # Neutraliza qualquer overlay histórico que tentasse trocar a sidebar
        # ao sair da Home. O shell v0.0.19 é único e global.
        _apply_global_shell(self)

    MainWindow._build_ui = build
    MainWindow.navigate = navigate
