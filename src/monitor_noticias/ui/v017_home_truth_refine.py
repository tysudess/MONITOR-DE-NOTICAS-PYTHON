from __future__ import annotations

"""Refino exclusivamente visual da Home v0.0.17.

Não altera controller, callbacks, rotas ou motores. Ajusta somente dimensões,
ordem visual da navegação enquanto HOME está ativa e decoração local.
"""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

_INSTALLED = False


class _SidebarWave(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setFixedHeight(82)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        w, h = self.width(), self.height()
        for offset, alpha in ((0, 120), (13, 78), (26, 48)):
            path = QPainterPath(QPointF(-12, h * .72 + offset * .12))
            path.cubicTo(
                QPointF(w * .20, h * .08 + offset),
                QPointF(w * .43, h * 1.08 - offset * .30),
                QPointF(w * .62, h * .47 + offset * .08),
            )
            path.cubicTo(
                QPointF(w * .76, h * .13 + offset * .20),
                QPointF(w * .90, h * .68 - offset * .16),
                QPointF(w + 12, h * .30 + offset * .10),
            )
            p.setPen(QPen(QColor(0, 111, 192, alpha), 1.15))
            p.drawPath(path)


class _SidebarReferenceFooter(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("homeSidebarFooter")
        self.setFixedHeight(178)
        self.setStyleSheet("QFrame#homeSidebarFooter{background:#03182a;border:0;border-top:1px solid #083e5f;} QLabel{background:transparent;border:0;}")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 0, 12, 12)
        lay.setSpacing(1)
        lay.addWidget(_SidebarWave())
        version = QLabel("v4.0.2")
        version.setStyleSheet("color:#9fb7cc;font-size:9px;")
        lay.addWidget(version)
        brand = QLabel("Monitor de Notícias\nInteligência de mídia\npara melhores decisões")
        brand.setStyleSheet("color:#a7bfd3;font-size:9px;line-height:1.25;")
        lay.addWidget(brand)


def _paint_reference_hero(self, event) -> None:
    """Planeta grande, recortado pelo hero, como na imagem-verdade."""
    QFrame.paintEvent(self, event)
    p = QPainter(self)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    w, h = self.width(), self.height()

    rect = QRectF(1, 1, w - 2, h - 2)
    bg = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.bottom())
    bg.setColorAt(0.00, QColor("#03172a"))
    bg.setColorAt(0.38, QColor("#052642"))
    bg.setColorAt(0.67, QColor("#06375b"))
    bg.setColorAt(1.00, QColor("#031729"))
    p.setPen(QPen(QColor("#0a6088"), 1))
    p.setBrush(bg)
    p.drawRoundedRect(rect, 11, 11)

    # Malha técnica no fundo.
    p.setPen(QPen(QColor(0, 113, 185, 70), 1))
    for i in range(12):
        x = w * (.22 + i * .072)
        p.drawLine(QPointF(x, 0), QPointF(x + h * .36, h))
    p.setPen(QPen(QColor(0, 141, 220, 43), 1))
    for y in (h * .22, h * .52, h * .82):
        p.drawLine(QPointF(w * .25, y), QPointF(w * .80, y))

    # Globo deliberadamente maior que a altura do banner, portanto recortado.
    cx, cy, r = w * .49, h * .69, h * 1.30
    glow = QLinearGradient(cx - r, cy - r, cx + r, cy + r)
    glow.setColorAt(0, QColor(0, 64, 130, 0))
    glow.setColorAt(.42, QColor(0, 108, 225, 55))
    glow.setColorAt(.60, QColor(0, 177, 255, 115))
    glow.setColorAt(1, QColor(0, 64, 130, 0))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(glow)
    p.drawEllipse(QPointF(cx, cy), r * 1.08, r * 1.08)

    p.setBrush(QColor(2, 28, 60, 225))
    p.setPen(QPen(QColor(0, 174, 255, 170), 1.3))
    p.drawEllipse(QPointF(cx, cy), r, r)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # Latitudes e longitudes.
    for sy, alpha in ((.25, 75), (.48, 95), (.72, 70)):
        p.setPen(QPen(QColor(0, 174, 255, alpha), 1))
        p.drawEllipse(QRectF(cx - r * .92, cy - r * sy * .42, r * 1.84, r * sy * .84))
    p.setPen(QPen(QColor(0, 174, 255, 80), 1))
    for sx in (.28, .52, .76):
        p.drawEllipse(QRectF(cx - r * sx * .46, cy - r * .92, r * sx * .92, r * 1.84))

    # Silhueta vetorial aproximada da América do Sul, usada apenas como decoração.
    pts = [
        (-.23, -.34), (-.08, -.38), (.04, -.31), (.14, -.23), (.20, -.11),
        (.14, -.02), (.16, .09), (.09, .20), (.07, .34), (.01, .47),
        (-.07, .58), (-.10, .42), (-.16, .28), (-.20, .14), (-.30, .05),
        (-.34, -.08), (-.29, -.20), (-.31, -.28), (-.23, -.34),
    ]
    poly = QPolygonF([QPointF(cx + r * x, cy + r * y) for x, y in pts])
    p.setBrush(QColor(7, 83, 135, 150))
    p.setPen(QPen(QColor(43, 196, 255, 205), 1.7))
    p.drawPolygon(poly)

    # Rede e nós sobre o continente e oceano.
    nodes = [(-.26, -.21), (-.14, -.29), (-.02, -.18), (.11, -.11), (-.21, .00),
             (-.08, .08), (.08, .03), (-.16, .20), (-.02, .26), (.02, .43), (.18, .18)]
    links = ((0,1),(1,2),(2,3),(0,4),(4,5),(5,6),(4,7),(7,8),(8,9),(5,8),(6,10),(8,10))
    p.setPen(QPen(QColor(30, 202, 255, 145), 1))
    for a, b in links:
        ax, ay = nodes[a]; bx, by = nodes[b]
        p.drawLine(QPointF(cx+r*ax,cy+r*ay), QPointF(cx+r*bx,cy+r*by))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#22ccff"))
    for x, y in nodes:
        p.drawEllipse(QPointF(cx + r*x, cy + r*y), 2.4, 2.4)

    # Pequenas partículas, sem animação/peso de CPU.
    p.setBrush(QColor(75, 207, 255, 120))
    for x, y in ((.32,.22),(.37,.44),(.43,.29),(.56,.18),(.60,.40),(.65,.27),(.70,.50),(.75,.21)):
        p.drawEllipse(QPointF(w*x,h*y),1.4,1.4)

    p.setPen(QPen(QColor("#00d9ff"), 2))
    p.drawLine(QPointF(w*.70,h*.82), QPointF(w*.77,h*.82))
    p.drawLine(QPointF(w*.93,h*.86), QPointF(w*.955,h*.86))


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


def _ensure_sidebar_footer(window):
    footer = getattr(window, "_home_sidebar_footer", None)
    if footer is not None:
        return footer
    sidebar = getattr(window, "sidebar", None)
    if sidebar is None or not isinstance(sidebar.layout(), QVBoxLayout):
        return None
    footer = _SidebarReferenceFooter()
    sidebar.layout().addWidget(footer)
    window._home_sidebar_footer = footer
    return footer


def _ensure_sidebar_state(window):
    if hasattr(window, "_home_sidebar_visual_state"):
        return window._home_sidebar_visual_state
    sidebar = getattr(window, "sidebar", None)
    if sidebar is None:
        return None
    scroll = sidebar.findChild(QScrollArea, "sidebarScroll")
    content = scroll.widget() if scroll is not None else None
    layout = content.layout() if content is not None else None
    if not isinstance(layout, QVBoxLayout):
        return None

    groups = [w for w in sidebar.findChildren(QFrame) if w.objectName() == "sideGroupHeader"]
    tracked = groups + list(window.nav_holders.values())
    original = sorted(
        ((layout.indexOf(w), w) for w in tracked if layout.indexOf(w) >= 0),
        key=lambda item: item[0],
    )
    base = min((idx for idx, _ in original), default=1)
    state = {"layout": layout, "groups": groups, "original": original, "base": base}
    window._home_sidebar_visual_state = state
    return state


def _arrange_sidebar(window, active: bool) -> None:
    from monitor_noticias.ui.sections import SECTION_ORDER, Section

    state = _ensure_sidebar_state(window)
    if state is None:
        return
    layout, groups, original, base = state["layout"], state["groups"], state["original"], state["base"]

    tracked_widgets = [w for _, w in original]
    for widget in tracked_widgets:
        layout.removeWidget(widget)

    if active:
        for group in groups:
            group.hide()
            group.setMaximumHeight(0)
        desired = (
            Section.HOME, Section.NEWS, Section.VIDEOS, Section.DEMANDS,
            Section.SOURCES, Section.HISTORY, Section.TERMS, Section.COVERS,
            Section.PDF_EDITOR, Section.EXTRACTOR, Section.VIDEO_EDITOR,
            Section.NEWS_EXTRACTOR, Section.SHEET_AUTOMATION, Section.STOP,
            Section.SETTINGS,
        )
        for offset, section in enumerate(desired):
            holder = window.nav_holders.get(section)
            if holder is not None:
                layout.insertWidget(base + offset, holder)
    else:
        for group in groups:
            group.show()
            group.setMaximumHeight(16777215)
        # Restaura a ordem visual original capturada antes do modo HOME.
        for offset, (_, widget) in enumerate(original):
            layout.insertWidget(base + offset, widget)


def _home_shell(window, active: bool) -> None:
    top = getattr(window, "reference_top_bar", None)
    sidebar = getattr(window, "sidebar", None)
    footer = _ensure_sidebar_footer(window)

    if active:
        if top is not None:
            top.setFixedHeight(86)
        if sidebar is not None:
            sidebar.setFixedWidth(225)
        _arrange_sidebar(window, True)
        if footer is not None:
            footer.show()
    else:
        if top is not None:
            top.setFixedHeight(76)
        if sidebar is not None:
            sidebar.setFixedWidth(220)
        _arrange_sidebar(window, False)
        if footer is not None:
            footer.hide()


def install_v017_home_truth_refine() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    from monitor_noticias.ui.main_window import MainWindow
    from monitor_noticias.ui.sections import Section
    from monitor_noticias.ui.v017_home_truth import ReferenceHero

    # A troca abaixo é estritamente do paintEvent do banner decorativo.
    ReferenceHero.paintEvent = _paint_reference_hero

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
