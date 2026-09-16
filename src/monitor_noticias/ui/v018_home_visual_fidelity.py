from __future__ import annotations

"""Refino visual v0.0.18 da Home.

Somente aparência: pintura, paleta, brilho, contraste e estilos locais da Home,
sidebar e topbar enquanto HOME está ativa. Não altera controller, rotas,
callbacks, persistência nem motores.
"""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen, QPolygonF, QRadialGradient
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QLabel, QLineEdit, QPushButton

_INSTALLED = False

HOME_V018_STYLE = r"""
QWidget#referenceHome { background:#01101f; color:#f7fbff; font-family:'Segoe UI'; }
QWidget#referenceHomeBody { background:#01101f; }
QScrollArea#referenceHomeScroll, QScrollArea#referenceHomeScroll QWidget#qt_scrollarea_viewport { background:#01101f; border:0; }
QLabel { background:transparent; }
QLabel#heroTitle { color:#ffffff; font-size:30px; font-weight:850; }
QLabel#heroSubtitle { color:#c9def0; font-size:11px; }
QLabel#heroRail { color:#68dcff; font-size:11px; font-weight:800; letter-spacing:2px; }
QLabel#heroQuote { color:#ffffff; font-size:11px; font-style:italic; }
QFrame#homePanel {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #063154,stop:.45 #052540,stop:1 #03182c);
    border:1px solid #0ca7da;border-radius:11px;
}
QLabel#panelTitle { color:#ffffff; font-size:11px; font-weight:850; }
QLabel#panelLink { color:#35d2ff; font-size:9px; font-weight:700; }
QLabel#smallText { color:#d0e2f0; font-size:9px; }
QLabel#tinyText { color:#a8c1d5; font-size:8px; }
QLabel#metricCaption { color:#b6ccdd; font-size:8px; }
QLabel#activePill { color:#4effc0; background:#06463d; border:1px solid #0ac38b; border-radius:9px; padding:3px 8px; font-size:8px; font-weight:850; }
QProgressBar#sourceBar { background:#062b46; border:1px solid #0b4867; border-radius:3px; min-height:6px; max-height:6px; }
QProgressBar#sourceBar::chunk { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #00f0ff,stop:.52 #00c8ff,stop:1 #1987ff); border-radius:3px; }
"""

SIDEBAR_V018_STYLE = r"""
QFrame#sidebar {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #03101f,stop:.45 #03192d,stop:1 #021426);
    border:0;border-right:1px solid #0a5f87;border-radius:0;
}
QLabel#anchorMark { background:transparent;border:0;padding:0; }
QLabel#brandTitle { color:#ffffff;font-family:'Segoe UI';font-size:16px;font-weight:850; }
QLabel#brandSub { color:#91b5cf;font-family:'Segoe UI';font-size:9px;font-weight:500; }
QPushButton#navButton {
    color:#edf7ff;background:transparent;border:1px solid transparent;border-radius:9px;
    padding:7px 10px;text-align:left;font-family:'Segoe UI';font-size:11px;font-weight:500;
}
QPushButton#navButton:hover {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #073250,stop:1 #062238);
    border-color:#117ba8;
}
QPushButton#navButton:checked {
    color:#ffffff;
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #075077,stop:.50 #073654,stop:1 #052843);
    border:1px solid #00cfff;border-left:6px solid #00f0ff;font-weight:850;
}
QLabel#newsBadge { color:#031523;background:#ffd21a;border:0;border-radius:8px;padding:1px 5px;font-size:8px;font-weight:850; }
QScrollArea#sidebarScroll { background:transparent;border:0; }
QScrollArea#sidebarScroll>QWidget>QWidget { background:transparent; }
"""

TOPBAR_V018_STYLE = r"""
QFrame#referenceTopBar {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #03172b,stop:.56 #05233d,stop:1 #03182b);
    border-bottom:1px solid #0b709b;
}
QLineEdit#referenceGlobalSearch {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #08233c,stop:1 #071a35);
    color:#e6f6ff;border:1px solid #208ec2;border-radius:12px;padding:10px 15px;font-size:11px;
}
QLineEdit#referenceGlobalSearch:focus { border:1px solid #45d9ff; }
QFrame#referenceStatusOk { background:#06443f;border:1px solid #08ae88;border-radius:10px; }
QFrame#referenceClock { background:#061f36;border:1px solid #176b94;border-radius:11px; }
QPushButton#referenceBell { background:#071f36;color:#e9f7ff;border:1px solid #19749f;border-radius:10px;font-size:18px; }
QPushButton#referenceBell:hover { border-color:#32d4ff;background:#0a2d4b; }
QLabel#referenceStatusText { color:#ffffff;font-size:10px;font-weight:750; }
QLabel#referenceStatusDot { color:#00f2ad;font-size:15px;font-weight:900; }
QLabel#referenceDate,QLabel#referenceCity { color:#b4cfe1;font-size:9px; }
QLabel#referenceTime,QLabel#referenceTemp { color:#ffffff;font-size:16px;font-weight:850; }
QLabel#referenceSun { color:#ffd11a;font-size:27px;font-weight:900; }
"""

ACCENTS = {
    "NEWS": "#00d9ff", "VIDEOS": "#a25cff", "DEMANDS": "#ffbf1a",
    "SOURCES": "#13d8ff", "TERMS": "#a55cff", "COVERS": "#21c8ff",
    "PDF_EDITOR": "#19d7ef", "EXTRACTOR": "#b05cff", "VIDEO_EDITOR": "#ff4fc7",
}


def _glow(widget, color: str, blur: float = 22.0, strength: int = 165) -> None:
    effect = QGraphicsDropShadowEffect(widget)
    c = QColor(color); c.setAlpha(strength)
    effect.setColor(c); effect.setBlurRadius(blur); effect.setOffset(0, 0)
    widget.setGraphicsEffect(effect)


def _paint_hero(self, event) -> None:
    QFrame.paintEvent(self, event)
    p = QPainter(self)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    w, h = self.width(), self.height()
    rect = QRectF(1, 1, w - 2, h - 2)

    bg = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.bottom())
    bg.setColorAt(0.00, QColor("#021a31"))
    bg.setColorAt(0.30, QColor("#052b4e"))
    bg.setColorAt(0.56, QColor("#063d68"))
    bg.setColorAt(0.78, QColor("#052947"))
    bg.setColorAt(1.00, QColor("#02182b"))
    p.setPen(QPen(QColor("#0b8db7"), 1.2))
    p.setBrush(bg)
    p.drawRoundedRect(rect, 11, 11)

    # halo azul vivo concentrado atrás do globo, mais próximo da imagem-verdade
    cx, cy, r = w * .42, h * .67, h * 1.42
    halo = QRadialGradient(QPointF(cx, cy), r * 1.18)
    halo.setColorAt(0.00, QColor(0, 170, 255, 135))
    halo.setColorAt(.34, QColor(0, 104, 235, 92))
    halo.setColorAt(.70, QColor(0, 53, 135, 25))
    halo.setColorAt(1.00, QColor(0, 20, 50, 0))
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(halo)
    p.drawEllipse(QPointF(cx, cy), r * 1.18, r * 1.18)

    # globo
    globe = QRadialGradient(QPointF(cx-r*.16, cy-r*.18), r)
    globe.setColorAt(0.00, QColor("#0a5792"))
    globe.setColorAt(.50, QColor("#05315f"))
    globe.setColorAt(1.00, QColor("#021a38"))
    p.setBrush(globe); p.setPen(QPen(QColor(30, 200, 255, 220), 1.5))
    p.drawEllipse(QPointF(cx, cy), r, r)
    p.setBrush(Qt.BrushStyle.NoBrush)

    # meridianos e paralelos
    for factor, alpha in ((.22,95),(.42,125),(.64,92),(.82,70)):
        p.setPen(QPen(QColor(20, 183, 255, alpha), 1))
        p.drawEllipse(QRectF(cx-r*.95, cy-r*factor*.42, r*1.90, r*factor*.84))
    for factor, alpha in ((.28,85),(.52,100),(.76,72)):
        p.setPen(QPen(QColor(20, 183, 255, alpha), 1))
        p.drawEllipse(QRectF(cx-r*factor*.46, cy-r*.95, r*factor*.92, r*1.90))

    # América do Sul mais luminosa
    shape = [(-.28,-.39),(-.14,-.43),(-.03,-.38),(.08,-.28),(.17,-.19),(.22,-.08),
             (.15,.02),(.17,.12),(.10,.23),(.08,.36),(.01,.50),(-.08,.62),(-.11,.45),
             (-.17,.32),(-.20,.18),(-.29,.10),(-.35,-.02),(-.32,-.15),(-.37,-.25),(-.29,-.39)]
    poly = QPolygonF([QPointF(cx+r*x, cy+r*y) for x,y in shape])
    p.setBrush(QColor(7, 110, 175, 185)); p.setPen(QPen(QColor(80, 222, 255, 235), 1.9)); p.drawPolygon(poly)

    # malha tecnológica ao fundo e rede de pontos
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QPen(QColor(0, 143, 230, 70), 1))
    for i in range(13):
        x = w * (.20 + i * .071); p.drawLine(QPointF(x, 0), QPointF(x + h*.42, h))
    for y in (h*.22, h*.48, h*.77):
        p.setPen(QPen(QColor(0, 155, 235, 42), 1)); p.drawLine(QPointF(w*.22,y), QPointF(w*.84,y))

    nodes=[(-.27,-.27),(-.15,-.34),(-.04,-.25),(.09,-.18),(-.28,-.08),(-.15,.02),(.02,-.01),(-.20,.17),(-.07,.25),(-.03,.43),(.13,.16),(-.13,.40)]
    links=((0,1),(1,2),(2,3),(0,4),(4,5),(5,6),(4,7),(7,8),(8,9),(5,8),(6,10),(8,10),(8,11))
    p.setPen(QPen(QColor(54, 220, 255, 190), 1.15))
    for a,b in links:
        ax,ay=nodes[a]; bx,by=nodes[b]
        p.drawLine(QPointF(cx+r*ax,cy+r*ay), QPointF(cx+r*bx,cy+r*by))
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor("#58e8ff"))
    for x,y in nodes: p.drawEllipse(QPointF(cx+r*x,cy+r*y),2.5,2.5)

    # pontos luminosos na área direita
    for x,y,s in ((.55,.16,2.0),(.59,.41,1.5),(.65,.25,1.8),(.70,.48,1.5),(.75,.18,2.0),(.80,.36,1.4)):
        glow = QRadialGradient(QPointF(w*x,h*y), s*4)
        glow.setColorAt(0,QColor(110,235,255,230)); glow.setColorAt(1,QColor(0,170,255,0))
        p.setBrush(glow); p.drawEllipse(QPointF(w*x,h*y),s*4,s*4)

    p.setPen(QPen(QColor("#20e6ff"), 2.2))
    p.drawLine(QPointF(w*.70,h*.82),QPointF(w*.77,h*.82))
    p.drawLine(QPointF(w*.93,h*.86),QPointF(w*.955,h*.86))


def _style_home(page) -> None:
    from monitor_noticias.ui.v017_home_truth import ModuleCard
    page.setStyleSheet(HOME_V018_STYLE)
    cards = getattr(page, "module_cards", {})
    for route, card in cards.items():
        accent = ACCENTS.get(route, "#19cfff")
        card.setStyleSheet(f"""
            QFrame{{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #0a3151,stop:.55 #082541,stop:1 #071a31);border:1px solid {accent};border-radius:11px;}}
            QLabel{{border:0;background:transparent;}}
        """)
        if route == "NEWS":
            card.setStyleSheet(f"""
                QFrame{{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #0c4770,stop:.38 #0b3157,stop:1 #071c35);border:2px solid {accent};border-radius:11px;}}
                QLabel{{border:0;background:transparent;}}
            """)
        _glow(card, accent, 24 if route == "NEWS" else 15, 130 if route == "NEWS" else 72)
    for panel in page.findChildren(QFrame, "homePanel"):
        _glow(panel, "#00cfff", 12, 45)


def _style_shell(window, active: bool) -> None:
    sidebar = getattr(window, "sidebar", None)
    top = getattr(window, "reference_top_bar", None)
    if not active:
        return
    if sidebar is not None:
        sidebar.setStyleSheet(SIDEBAR_V018_STYLE)
        sidebar.setFixedWidth(225)
        for button in getattr(window, "nav_buttons", {}).values():
            button.setMinimumHeight(44); button.setMaximumHeight(44)
        active_button = getattr(window, "nav_buttons", {}).get(getattr(window, "_current", None))
        if active_button is not None:
            _glow(active_button, "#00dfff", 20, 120)
    if top is not None:
        top.setStyleSheet(TOPBAR_V018_STYLE)
        search = getattr(top, "search", None)
        if isinstance(search, QLineEdit): _glow(search, "#4787ff", 20, 75)
        for widget in (getattr(top,"proxy_box",None), getattr(top,"auto_box",None)):
            if widget is not None: _glow(widget, "#00e6b1", 15, 55)
        bell = getattr(top, "bell", None)
        if isinstance(bell, QPushButton): _glow(bell, "#16bfff", 14, 55)


def install_v018_home_visual_fidelity() -> None:
    global _INSTALLED
    if _INSTALLED: return
    _INSTALLED = True

    from monitor_noticias.ui.main_window import MainWindow
    from monitor_noticias.ui.sections import Section
    from monitor_noticias.ui.v017_home_truth import ReferenceHero

    ReferenceHero.paintEvent = _paint_hero
    old_build = MainWindow._build_ui
    old_nav = MainWindow.navigate

    def build(self):
        old_build(self)
        page = self.pages.get(Section.HOME)
        if page is not None: _style_home(page)
        _style_shell(self, getattr(self, "_current", None) == Section.HOME)

    def navigate(self, section):
        old_nav(self, section)
        page = self.pages.get(Section.HOME)
        if page is not None: _style_home(page)
        _style_shell(self, section == Section.HOME)

    MainWindow._build_ui = build
    MainWindow.navigate = navigate
