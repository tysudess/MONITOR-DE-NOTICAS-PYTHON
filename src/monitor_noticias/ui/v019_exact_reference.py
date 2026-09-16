from __future__ import annotations

"""v0.0.19 — Home baseada literalmente na imagem-verdade e shell global.

A camada abaixo é visual. O MainWindow, controller, banco, coletores, rotas,
callbacks e páginas funcionais existentes continuam sendo os originais. A Home
mantém a página real viva por baixo da camada visual e usa a própria referência
fornecida pelo usuário como superfície final, sem redesenhar ou reinterpretar.
"""

import sys
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget

_INSTALLED = False
_HOME_PIXMAP: QPixmap | None = None

# A referência enviada mede 1672x941. A área do conteúdo começa após a sidebar
# de 225 px e a topbar de 86 px. A Home pinta literalmente esse recorte.
REF_FULL_W = 1672.0
REF_FULL_H = 941.0
REF_SIDE_W = 225.0
REF_TOP_H = 86.0
REF_CONTENT_W = REF_FULL_W - REF_SIDE_W
REF_CONTENT_H = REF_FULL_H - REF_TOP_H

SIDEBAR_V019 = """
QFrame#sidebar {
    background:#021b2e;
    border:0;
    border-right:1px solid #07557d;
    border-radius:0;
}
QLabel#anchorMark {
    color:#ffc400;
    font-family:'Segoe UI Symbol';
    font-size:46px;
    font-weight:900;
}
QLabel#brandTitle { color:#ffffff; font-size:18px; font-weight:900; letter-spacing:.4px; }
QLabel#brandSub { color:#86abc6; font-size:11px; }
QPushButton#navButton {
    color:#eef5ff;
    background:transparent;
    border:0;
    border-radius:10px;
    padding:10px 12px;
    text-align:left;
    font-size:13px;
    font-weight:500;
}
QPushButton#navButton:hover {
    color:#ffffff;
    background:#052f4e;
}
QPushButton#navButton:checked {
    color:#ffffff;
    font-weight:800;
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #075f91,stop:.46 #063e63,stop:1 #042a48);
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
    color:#f4f7ff; border:1px solid #1688c8; border-radius:13px; padding:0 17px;
    font-size:13px; selection-background-color:#1378ad;
}
QLineEdit#globalSearch:focus { border:1px solid #7568ff; }
QFrame#topStatusGood { background:#073a38; border:1px solid #00a888; border-radius:11px; }
QLabel#topStatusText { color:#f4ffff; font-size:11px; font-weight:800; }
QLabel#topStatusDot { color:#00e3a8; font-size:18px; }
QPushButton#topBell { color:#e9f3ff; background:#071f3c; border:1px solid #164f78; border-radius:11px; font-size:20px; }
QFrame#topClock { background:#041d34; border:1px solid #0d547c; border-radius:13px; }
QLabel#topDate { color:#a8c1d5; font-size:10px; }
QLabel#topTime { color:#ffffff; font-size:17px; font-weight:900; }
QLabel#topWeatherIcon { color:#ffd329; font-size:29px; }
QLabel#topWeatherPlace { color:#a6bfd2; font-size:10px; }
QLabel#topWeatherTemp { color:#ffffff; font-size:16px; font-weight:900; }
"""


def _resource_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "resources"
    return Path(__file__).resolve().parents[3] / "resources"


def _home_pixmap() -> QPixmap:
    global _HOME_PIXMAP
    if _HOME_PIXMAP is not None and not _HOME_PIXMAP.isNull():
        return _HOME_PIXMAP
    path = _resource_root() / "ui" / "v019" / "home-full-q90.webp"
    pix = QPixmap(str(path))
    if pix.isNull():
        raise RuntimeError(f"Imagem-verdade integral v0.0.19 não pôde ser carregada: {path}")
    _HOME_PIXMAP = pix
    return pix


class HomeTruthSurface(QWidget):
    """Superfície visual literal com hotspots para os mesmos callbacks da Home."""

    CARD_RECTS = (
        (14, 166, 142, 150, "NEWS"),
        (165, 166, 137, 150, "VIDEOS"),
        (311, 166, 142, 150, "DEMANDS"),
        (463, 166, 140, 150, "SOURCES"),
        (613, 166, 140, 150, "TERMS"),
        (764, 166, 136, 150, "COVERS"),
        (910, 166, 141, 150, "PDF_EDITOR"),
        (1061, 166, 177, 150, "EXTRACTOR"),
        (1249, 166, 173, 150, "VIDEO_EDITOR"),
    )

    def __init__(self, page):
        super().__init__(page)
        self.page = page
        self.setObjectName("v019HomeTruthSurface")
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.show()
        self.raise_()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        src = QRectF(REF_SIDE_W, REF_TOP_H, REF_CONTENT_W, REF_CONTENT_H)
        p.drawPixmap(QRectF(self.rect()), _home_pixmap(), src)

    def _to_reference(self, pos):
        if self.width() <= 0 or self.height() <= 0:
            return QPointF()
        return QPointF(pos.x() * REF_CONTENT_W / self.width(), pos.y() * REF_CONTENT_H / self.height())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            p = self._to_reference(event.position())
            for x, y, w, h, route in self.CARD_RECTS:
                if QRectF(x, y, w, h).contains(p):
                    self.page.navigate.emit(route)
                    event.accept()
                    return
            # Links visuais existentes na referência: Histórico e Automação.
            if QRectF(445, 558, 125, 38).contains(p):
                self.page.navigate.emit("HISTORY")
                event.accept()
                return
            if QRectF(1000, 330, 120, 34).contains(p):
                self.page.navigate.emit("SETTINGS")
                event.accept()
                return
        super().mousePressEvent(event)


def _install_home_truth(page) -> None:
    # A página real continua instanciada e recebendo refresh do controller.
    scroll = page.findChild(QScrollArea, "referenceHomeScroll")
    if scroll is not None:
        scroll.hide()
    surface = getattr(page, "_v019_truth_surface", None)
    if surface is None:
        surface = HomeTruthSurface(page)
        page._v019_truth_surface = surface
    surface.setGeometry(page.rect())
    surface.show()
    surface.raise_()


def _sidebar_layout(window):
    sidebar = getattr(window, "sidebar", None)
    if sidebar is None:
        return None, None
    scroll = sidebar.findChild(QScrollArea, "sidebarScroll")
    content = scroll.widget() if scroll is not None else None
    layout = content.layout() if content is not None else None
    return scroll, layout if isinstance(layout, QVBoxLayout) else None


def _arrange_global_sidebar(window) -> None:
    from monitor_noticias.ui.main_window import SidebarShipArt
    from monitor_noticias.ui.sections import Section

    sidebar = getattr(window, "sidebar", None)
    if sidebar is None:
        return
    sidebar.setFixedWidth(225)
    sidebar.setStyleSheet(SIDEBAR_V019)
    scroll, layout = _sidebar_layout(window)
    if scroll is not None:
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    if layout is not None:
        layout.setContentsMargins(9, 8, 9, 6)
        layout.setSpacing(2)
        for group in sidebar.findChildren(QFrame, "sideGroupHeader"):
            group.hide()
            group.setFixedHeight(0)

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
                holder.show()
                holder.setFixedHeight(46)
                layout.insertWidget(pos, holder)
                pos += 1

        # As funções extras permanecem no mesmo menu, abaixo da área mostrada
        # pela imagem de referência, acessíveis pelo scroll da sidebar.
        spacer = getattr(window, "_v019_extra_spacer", None)
        if spacer is None:
            spacer = QWidget()
            spacer.setFixedHeight(54)
            spacer.setStyleSheet("background:transparent;")
            window._v019_extra_spacer = spacer
        if layout.indexOf(spacer) >= 0:
            layout.removeWidget(spacer)
        layout.insertWidget(pos, spacer)
        pos += 1
        for section in extra:
            holder = window.nav_holders.get(section)
            if holder is not None:
                holder.show()
                holder.setFixedHeight(46)
                layout.insertWidget(pos, holder)
                pos += 1

    for button in getattr(window, "nav_buttons", {}).values():
        button.setFixedHeight(46)
        font = button.font()
        font.setPointSizeF(11.5)
        button.setFont(font)
    badge = getattr(window, "news_badge", None)
    if badge is not None:
        badge.hide()
    card = getattr(window, "side_status_card", None)
    if card is not None:
        card.hide()
        card.setFixedHeight(0)
    for ship in sidebar.findChildren(SidebarShipArt):
        ship.hide()
        ship.setFixedHeight(0)
    for label in sidebar.findChildren(QLabel):
        if label.objectName() == "sideMotto" or label.text().strip() == "━━":
            label.hide()

    footer = getattr(window, "_home_sidebar_footer", None)
    if footer is not None:
        footer.show()
        footer.setFixedHeight(235)
        footer.setStyleSheet(
            "QFrame#homeSidebarFooter{background:#03182a;border:0;border-top:1px solid #073d5c;}"
            "QLabel{background:transparent;border:0;color:#b4c9db;font-size:11px;}"
        )


def _style_global_topbar(window) -> None:
    top = getattr(window, "reference_top_bar", None)
    if top is None:
        return
    top.setFixedHeight(86)
    top.setStyleSheet(TOPBAR_V019)
    search = getattr(top, "search", None)
    if isinstance(search, QLineEdit):
        search.setMinimumWidth(650)
        search.setMaximumWidth(720)
        search.setFixedHeight(48)
        search.setPlaceholderText("⌕   Buscar notícias, fontes, demandas... ou digite um comando (Ctrl + K)")
    bell = getattr(top, "bell", None)
    if isinstance(bell, QPushButton):
        bell.setFixedSize(48, 48)


def _apply_global_shell(window) -> None:
    _arrange_global_sidebar(window)
    _style_global_topbar(window)
    header = getattr(window, "header_widget", None)
    if header is not None:
        header.hide()
        header.setMaximumHeight(0)
    footer = getattr(window, "footer_widget", None)
    if footer is not None:
        footer.hide()
        footer.setMaximumHeight(0)


def install_v019_exact_reference() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    from monitor_noticias.ui.main_window import MainWindow
    from monitor_noticias.ui.sections import Section
    from monitor_noticias.ui.v017_home_truth import ReferenceHome

    old_build = MainWindow._build_ui
    old_nav = MainWindow.navigate
    old_resize = ReferenceHome.resizeEvent

    def home_resize(self, event):
        old_resize(self, event)
        surface = getattr(self, "_v019_truth_surface", None)
        if surface is not None:
            surface.setGeometry(self.rect())
            surface.raise_()

    def build(self):
        old_build(self)
        page = self.pages.get(Section.HOME)
        if page is not None:
            _install_home_truth(page)
        _apply_global_shell(self)

    def navigate(self, section):
        old_nav(self, section)
        page = self.pages.get(Section.HOME)
        if page is not None:
            _install_home_truth(page)
        # Qualquer overlay histórico que tente restaurar outra sidebar é
        # sobrescrito aqui. O shell v0.0.19 é único em todas as abas.
        _apply_global_shell(self)

    ReferenceHome.resizeEvent = home_resize
    MainWindow._build_ui = build
    MainWindow.navigate = navigate
