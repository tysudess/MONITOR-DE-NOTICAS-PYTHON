from __future__ import annotations

"""Ajustes finais de precisão da aba Início; somente geometria e pintura."""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QFrame, QLabel, QLineEdit, QScrollArea, QVBoxLayout

_INSTALLED = False


def _precision_hero_paint(self, event) -> None:
    QFrame.paintEvent(self, event)
    p = QPainter(self)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    w, h = self.width(), self.height()
    rect = QRectF(1, 1, w - 2, h - 2)

    bg = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.bottom())
    bg.setColorAt(0.00, QColor("#03172a"))
    bg.setColorAt(0.34, QColor("#05243d"))
    bg.setColorAt(0.58, QColor("#06375b"))
    bg.setColorAt(1.00, QColor("#031729"))
    p.setPen(QPen(QColor("#0a6088"), 1))
    p.setBrush(bg)
    p.drawRoundedRect(rect, 11, 11)

    p.setPen(QPen(QColor(0, 118, 190, 65), 1))
    for i in range(13):
        x = w * (.18 + i * .073)
        p.drawLine(QPointF(x, 0), QPointF(x + h * .40, h))
    for y in (h * .22, h * .50, h * .80):
        p.setPen(QPen(QColor(0, 139, 215, 35), 1))
        p.drawLine(QPointF(w * .23, y), QPointF(w * .82, y))

    # Na referência, o globo fica atrás do título e antes do slogan, com centro
    # perto de 42% da largura útil do hero e diâmetro maior que a altura do card.
    cx, cy, r = w * .42, h * .67, h * 1.38
    glow = QLinearGradient(cx - r, cy - r, cx + r, cy + r)
    glow.setColorAt(0.00, QColor(0, 36, 82, 0))
    glow.setColorAt(.38, QColor(0, 88, 205, 44))
    glow.setColorAt(.56, QColor(0, 172, 255, 128))
    glow.setColorAt(1.00, QColor(0, 36, 82, 0))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(glow)
    p.drawEllipse(QPointF(cx, cy), r * 1.10, r * 1.10)

    p.setBrush(QColor(2, 26, 57, 225))
    p.setPen(QPen(QColor(0, 173, 255, 190), 1.35))
    p.drawEllipse(QPointF(cx, cy), r, r)
    p.setBrush(Qt.BrushStyle.NoBrush)

    p.setPen(QPen(QColor(0, 180, 255, 90), 1))
    for factor in (.24, .45, .67):
        p.drawEllipse(QRectF(cx-r*.94, cy-r*factor*.43, r*1.88, r*factor*.86))
    for factor in (.30, .54, .78):
        p.drawEllipse(QRectF(cx-r*factor*.46, cy-r*.94, r*factor*.92, r*1.88))

    # América do Sul: contorno local e leve preenchimento azul, sem asset remoto.
    shape = [
        (-.28,-.39),(-.14,-.43),(-.03,-.38),(.08,-.28),(.17,-.19),(.22,-.08),
        (.15,.02),(.17,.12),(.10,.23),(.08,.36),(.01,.50),(-.08,.62),
        (-.11,.45),(-.17,.32),(-.20,.18),(-.29,.10),(-.35,-.02),(-.32,-.15),
        (-.37,-.25),(-.29,-.39)
    ]
    poly = QPolygonF([QPointF(cx+r*x, cy+r*y) for x,y in shape])
    p.setBrush(QColor(5, 90, 147, 145))
    p.setPen(QPen(QColor(54, 203, 255, 215), 1.8))
    p.drawPolygon(poly)

    nodes=[(-.27,-.27),(-.15,-.34),(-.04,-.25),(.09,-.18),(-.28,-.08),(-.15,.02),
           (.02,-.01),(-.20,.17),(-.07,.25),(-.03,.43),(.13,.16),(-.13,.40)]
    links=((0,1),(1,2),(2,3),(0,4),(4,5),(5,6),(4,7),(7,8),(8,9),(5,8),(6,10),(8,10),(8,11))
    p.setPen(QPen(QColor(25, 209, 255, 150), 1))
    for a,b in links:
        ax,ay=nodes[a]; bx,by=nodes[b]
        p.drawLine(QPointF(cx+r*ax,cy+r*ay),QPointF(cx+r*bx,cy+r*by))
    p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor("#2ad4ff"))
    for x,y in nodes:
        p.drawEllipse(QPointF(cx+r*x,cy+r*y),2.3,2.3)

    p.setBrush(QColor(79, 210, 255, 135))
    for x,y in ((.30,.18),(.34,.43),(.47,.28),(.55,.17),(.60,.42),(.65,.24),(.71,.49),(.76,.20)):
        p.drawEllipse(QPointF(w*x,h*y),1.35,1.35)

    p.setPen(QPen(QColor("#00d9ff"), 2))
    p.drawLine(QPointF(w*.70,h*.82),QPointF(w*.77,h*.82))
    p.drawLine(QPointF(w*.93,h*.86),QPointF(w*.955,h*.86))


def _precision_home(page) -> None:
    from monitor_noticias.ui.v017_home_truth import ReferenceHero

    hero = page.findChild(ReferenceHero)
    if hero is not None:
        hero.setFixedHeight(155)
        layout = hero.layout()
        if layout is not None and layout.count() >= 4:
            for index, stretch in enumerate((43, 16, 19, 22)):
                layout.setStretch(index, stretch)

    body = getattr(page, "body", None)
    if body is not None:
        # Hero ocupa toda a largura, como na imagem; as demais faixas têm 12 px.
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(10)
        for idx in (1, 2, 3):
            child = body.itemAt(idx)
            if child is not None and child.layout() is not None:
                top = 3 if idx in (2, 3) else 0
                child.layout().setContentsMargins(12, top, 12, 0)
        footer_item = body.itemAt(4)
        if footer_item is not None and footer_item.widget() is not None:
            footer_item.widget().hide()
            footer_item.widget().setMaximumHeight(0)

    panels = page.findChildren(QFrame, "homePanel")
    for panel in panels[:4]:
        panel.setFixedHeight(200)
    for panel in panels[4:6]:
        panel.setFixedHeight(286)
    if len(panels) >= 6:
        # Três resumos no rodapé do gráfico devem ter altura próxima da referência.
        for child in panels[5].findChildren(QFrame):
            if "background:#05233a" in child.styleSheet().replace(" ", ""):
                child.setMinimumHeight(64)


def _precision_topbar(window, active: bool) -> None:
    top = getattr(window, "reference_top_bar", None)
    if top is None:
        return
    if not active:
        search = getattr(top, "search", None)
        if isinstance(search, QLineEdit):
            search.setMaximumWidth(16777215)
            search.setMinimumWidth(0)
        return

    top.setFixedHeight(86)
    row = top.layout()
    if row is not None:
        row.setContentsMargins(28, 10, 18, 10)
        row.setSpacing(12)

    search = getattr(top, "search", None)
    if isinstance(search, QLineEdit):
        search.setMinimumWidth(520)
        search.setMaximumWidth(710)
        search.setFixedHeight(46)
        if row is not None:
            row.setAlignment(search, Qt.AlignmentFlag.AlignVCenter)

    for widget, width in ((getattr(top,"proxy_box",None),122),(getattr(top,"auto_box",None),142)):
        if widget is not None:
            widget.setFixedWidth(width)
            widget.setFixedHeight(46)
            if row is not None:
                row.setAlignment(widget, Qt.AlignmentFlag.AlignVCenter)

    bell = getattr(top, "bell", None)
    if bell is not None:
        bell.setFixedSize(48, 48)
        if row is not None:
            row.setAlignment(bell, Qt.AlignmentFlag.AlignVCenter)

    clock = top.findChild(QFrame, "referenceClock")
    if clock is not None:
        clock.setFixedSize(280, 62)
        if row is not None:
            row.setAlignment(clock, Qt.AlignmentFlag.AlignVCenter)


def _precision_sidebar(window, active: bool) -> None:
    sidebar = getattr(window, "sidebar", None)
    if sidebar is None:
        return

    # Esconder a decoração de grupos de forma robusta, inclusive labels antigos.
    group_names={"PRINCIPAL","GERENCIAMENTO","FERRAMENTAS","SISTEMA"}
    for frame in sidebar.findChildren(QFrame):
        if frame.objectName()=="sideGroupHeader":
            frame.setVisible(not active)
            frame.setMaximumHeight(0 if active else 16777215)
    for label in sidebar.findChildren(QLabel):
        if label.objectName() in {"sideGroupDash","sideGroupTitle"} or label.text().strip() in group_names:
            label.setVisible(not active)
            label.setMaximumHeight(0 if active else 16777215)

    anchor = sidebar.findChild(QLabel, "anchorMark")
    if anchor is not None and active:
        anchor.setStyleSheet("background:transparent;border:0;padding:0;")
        anchor.setFixedSize(68, 72)

    scroll = sidebar.findChild(QScrollArea, "sidebarScroll")
    if scroll is not None:
        content = scroll.widget()
        layout = content.layout() if content is not None else None
        if active and isinstance(layout, QVBoxLayout):
            layout.setContentsMargins(9, 12, 9, 8)
            layout.setSpacing(4)
        bar = scroll.verticalScrollBar()
        if active:
            bar.setStyleSheet("QScrollBar:vertical{width:0px;background:transparent;} QScrollBar::handle:vertical{background:transparent;}")
        else:
            bar.setStyleSheet("")

    footer = getattr(window, "_home_sidebar_footer", None)
    if footer is not None and active:
        footer.setFixedHeight(232)


def install_v017_home_truth_precision() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED=True

    from monitor_noticias.ui.main_window import MainWindow
    from monitor_noticias.ui.sections import Section
    from monitor_noticias.ui.v017_home_truth import ReferenceHero

    ReferenceHero.paintEvent = _precision_hero_paint

    old_build=MainWindow._build_ui
    old_nav=MainWindow.navigate

    def build(self):
        old_build(self)
        page=self.pages.get(Section.HOME)
        if page is not None:
            _precision_home(page)
        _precision_topbar(self, getattr(self,"_current",None)==Section.HOME)
        _precision_sidebar(self, getattr(self,"_current",None)==Section.HOME)

    def navigate(self, section):
        old_nav(self, section)
        page=self.pages.get(Section.HOME)
        if page is not None:
            _precision_home(page)
        _precision_topbar(self, section==Section.HOME)
        _precision_sidebar(self, section==Section.HOME)

    MainWindow._build_ui=build
    MainWindow.navigate=navigate
