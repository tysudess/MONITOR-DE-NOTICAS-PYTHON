from __future__ import annotations

"""Overlay estritamente visual para a família de layouts v0.0.14.

Este módulo não substitui páginas, motores, callbacks nem persistência. Ele apenas
recompõe o shell já existente (barra global, sidebar e cabeçalho visual), usando
os mesmos widgets, estados e rotas do Monitor.
"""

from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

_INSTALLED = False

REFERENCE_STYLE = r"""
QWidget#mainContent {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #031525,stop:.55 #041A2B,stop:1 #061C2F);
}
QFrame#referenceTopBar {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #03192B,stop:.62 #041D31,stop:1 #031729);
    border-bottom:1px solid #0B557A;
}
QLineEdit#referenceGlobalSearch {
    background:#061D33;color:#DDEBFA;border:1px solid #177DAA;border-radius:11px;
    padding:9px 14px;font-size:11px;min-height:24px;
}
QLineEdit#referenceGlobalSearch:focus { border:1px solid #00B7FF; }
QFrame#referenceStatusOk { background:#043A3A;border:1px solid #078B70;border-radius:10px; }
QFrame#referenceClock { background:#061D33;border:1px solid #125E83;border-radius:10px; }
QLabel#referenceStatusText { color:#F1F7FC;font-size:10px;font-weight:700; }
QLabel#referenceStatusDot { color:#00E2A3;font-size:15px;font-weight:900; }
QLabel#referenceDate { color:#A9C2D8;font-size:9px; }
QLabel#referenceTime { color:#FFFFFF;font-size:16px;font-weight:800; }
QLabel#referenceCity { color:#A9C2D8;font-size:9px; }
QLabel#referenceTemp { color:#FFFFFF;font-size:16px;font-weight:800; }
QLabel#referenceSun { color:#FFC400;font-size:27px;font-weight:800; }
QPushButton#referenceBell {
    background:#061D33;color:#DDEBFA;border:1px solid #17678F;border-radius:10px;
    min-width:38px;max-width:38px;min-height:38px;max-height:38px;padding:0;font-size:18px;
}
QPushButton#referenceBell:hover { border-color:#00B7FF;background:#082945; }

QFrame#sidebar {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #031426,stop:.58 #041A2B,stop:1 #031628);
    border:0;border-right:1px solid #0B4565;border-radius:0;
}
QLabel#anchorMark { background:transparent;border:0;padding:0; }
QLabel#brandTitle { color:#F5F8FB;font-family:'Segoe UI';font-size:16px;font-weight:800; }
QLabel#brandSub { color:#8EA9C1;font-family:'Segoe UI';font-size:9px;font-weight:500; }
QFrame#sideGroupHeader { background:transparent;border:0; }
QLabel#sideGroupDash { color:#FFC400;font-size:13px;font-weight:900; }
QLabel#sideGroupTitle { color:#7198B8;font-size:9px;font-weight:700;letter-spacing:1px; }
QPushButton#navButton {
    color:#E7EEF6;background:transparent;border:1px solid transparent;border-radius:9px;
    padding:7px 10px;text-align:left;font-family:'Segoe UI';font-size:11px;font-weight:500;
}
QPushButton#navButton:hover { background:#06253F;border-color:#0D587D; }
QPushButton#navButton:pressed { background:#07304F; }
QPushButton#navButton:checked {
    color:#FFFFFF;background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #073D62,stop:1 #062C4B);
    border:1px solid #00B7FF;border-left:5px solid #00E5FF;font-weight:800;
}
QLabel#newsBadge { color:#041A2B;background:#FFC400;border:0;border-radius:8px;padding:1px 5px;font-size:8px;font-weight:800; }
QFrame#sideStatusCard { background:transparent;border:0; }
QScrollArea#sidebarScroll { background:transparent;border:0; }
QScrollArea#sidebarScroll>QWidget>QWidget { background:transparent; }
QScrollBar:vertical { background:transparent;width:5px;margin:2px 0;border:0; }
QScrollBar::handle:vertical { background:#0D587D;min-height:30px;border-radius:2px; }
QScrollBar::handle:vertical:hover { background:#00A9E8; }
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical { height:0; }
QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical { background:transparent; }

QFrame#pageHeader {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #041A2D,stop:.62 #062742,stop:1 #04182A);
    border:1px solid #0A5E86;border-radius:12px;
}
QLabel#pageKicker { color:#4FCBFF;font-size:9px;font-weight:700;letter-spacing:1.2px; }
QLabel#pageTitle { color:#FFFFFF;font-size:26px;font-weight:800; }
QLabel#pageSubtitle { color:#C3D4E4;font-size:11px; }
QLabel#pageIcon { color:#00B7FF;font-size:34px;font-weight:800; }

QFrame#card,QFrame#techCard,QFrame#resultCard,QFrame#filterCard,QFrame#settingsBlock {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #082B43,stop:.55 #07263E,stop:1 #051D32);
    border:1px solid #0B709A;border-radius:11px;
}
QFrame#resultCard:hover,QFrame#techCard:hover { border-color:#00B7FF; }
QLineEdit,QComboBox,QSpinBox,QDateEdit,QTimeEdit {
    background:#061F35;color:#EEF7FF;border:1px solid #126D97;border-radius:8px;
    padding:7px 9px;min-height:24px;selection-background-color:#078BFF;
}
QLineEdit:focus,QComboBox:focus,QSpinBox:focus,QDateEdit:focus,QTimeEdit:focus { border:1px solid #00C8FF; }
QPushButton { border-radius:8px; }
QPushButton[secondary='true'] { background:#061F35;color:#E2EDF7;border:1px solid #126D97; }
QPushButton[secondary='true']:hover { background:#082C49;border-color:#00B7FF; }
QFrame#footerFrame { background:#031525;border-top:1px solid #0A456B; }
"""


class ReferenceTopBar(QFrame):
    """Barra global visual alimentada somente por estados já existentes."""

    def __init__(self, window) -> None:
        super().__init__(window)
        self.window = window
        self.setObjectName("referenceTopBar")
        self.setFixedHeight(74)
        row = QHBoxLayout(self)
        row.setContentsMargins(18, 10, 18, 10)
        row.setSpacing(12)

        self.search = QLineEdit()
        self.search.setObjectName("referenceGlobalSearch")
        self.search.setPlaceholderText("⌕   Buscar notícias, fontes, demandas... ou digite um termo")
        self.search.returnPressed.connect(self._route_search)
        row.addWidget(self.search, 1)

        self.proxy_box, self.proxy_text = self._status_box("Proxy pronto")
        row.addWidget(self.proxy_box)
        self.auto_box, self.auto_text = self._status_box("Automação ativa")
        row.addWidget(self.auto_box)

        self.bell = QPushButton("♢")
        self.bell.setObjectName("referenceBell")
        self.bell.setToolTip("Notificações do Windows continuam sob responsabilidade do sistema existente.")
        row.addWidget(self.bell)

        time_box = QFrame(); time_box.setObjectName("referenceClock")
        tl = QHBoxLayout(time_box); tl.setContentsMargins(14, 6, 14, 6); tl.setSpacing(12)
        tc = QVBoxLayout(); tc.setSpacing(0)
        self.date = QLabel(); self.date.setObjectName("referenceDate")
        self.time = QLabel(); self.time.setObjectName("referenceTime")
        tc.addWidget(self.date); tc.addWidget(self.time); tl.addLayout(tc)
        divider = QFrame(); divider.setFixedWidth(1); divider.setStyleSheet("background:#1A5E81;border:0;"); tl.addWidget(divider)
        sun = QLabel("☀"); sun.setObjectName("referenceSun"); tl.addWidget(sun)
        wc = QVBoxLayout(); wc.setSpacing(0)
        city = QLabel("Brasília - DF"); city.setObjectName("referenceCity")
        self.temp = QLabel("--°C"); self.temp.setObjectName("referenceTemp")
        wc.addWidget(city); wc.addWidget(self.temp); tl.addLayout(wc)
        row.addWidget(time_box)

    @staticmethod
    def _status_box(text: str):
        frame = QFrame(); frame.setObjectName("referenceStatusOk")
        lay = QHBoxLayout(frame); lay.setContentsMargins(10, 7, 12, 7); lay.setSpacing(6)
        dot = QLabel("●"); dot.setObjectName("referenceStatusDot")
        label = QLabel(text); label.setObjectName("referenceStatusText")
        lay.addWidget(dot); lay.addWidget(label)
        return frame, label

    def _route_search(self) -> None:
        text = self.search.text().strip()
        if not text:
            return
        from monitor_noticias.ui.sections import Section
        pages = self.window.pages
        current = getattr(self.window, "_current", Section.HOME)
        target = current if current in {Section.NEWS, Section.VIDEOS} else Section.NEWS
        page = pages.get(target)
        query = getattr(page, "query", None)
        if isinstance(query, QLineEdit):
            query.setText(text)
        if current != target:
            self.window.navigate(target)

    def sync(self) -> None:
        now = datetime.now()
        self.date.setText(now.strftime("%d/%m/%Y"))
        self.time.setText(now.strftime("%H:%M:%S"))
        cfg = self.window.controller.proxy_config
        auto = self.window.controller.automation_settings
        label = str(getattr(cfg, "status_label", "Proxy"))
        self.proxy_text.setText(label if label else "Proxy")
        self.auto_text.setText("Automação ativa" if auto.automatic_monitoring else "Automação pausada")
        header = getattr(self.window, "header_widget", None)
        weather = getattr(header, "weather_temp", None)
        if isinstance(weather, QLabel) and weather.text().strip():
            self.temp.setText(weather.text())


def _hide_legacy_sidebar_extras(window) -> None:
    # Os widgets permanecem vivos e seus estados continuam sendo atualizados pelo
    # MainWindow original; apenas deixam de ocupar a composição visual de referência.
    card = getattr(window, "side_status_card", None)
    if card is not None:
        card.hide()
    sidebar = getattr(window, "sidebar", None)
    if sidebar is None:
        return
    for child in sidebar.findChildren(QLabel):
        if child.objectName() == "sideMotto":
            child.hide()


def _polish_sidebar(window) -> None:
    sidebar = getattr(window, "sidebar", None)
    if sidebar is None:
        return
    sidebar.setFixedWidth(220)
    for button in window.nav_buttons.values():
        button.setMinimumHeight(44)
        button.setMaximumHeight(44)
        button.setIconSize(button.iconSize())
    _hide_legacy_sidebar_extras(window)


def _polish_header(window) -> None:
    header = getattr(window, "header_widget", None)
    if header is None:
        return
    header.setMinimumHeight(116)
    header.setMaximumHeight(126)
    for attr in ("proxy_pill", "auto_pill"):
        widget = getattr(header, attr, None)
        if widget is not None:
            widget.hide()
    for attr in ("date_label", "clock_label"):
        widget = getattr(header, attr, None)
        if widget is not None:
            widget.hide()
    weather = getattr(header, "weather_temp", None)
    if weather is not None:
        parent = weather.parentWidget()
        if parent is not None:
            parent.hide()


def _ensure_top_bar(window) -> None:
    if getattr(window, "reference_top_bar", None) is not None:
        return
    top = ReferenceTopBar(window)
    window.reference_top_bar = top
    window.content_layout.insertWidget(0, top)


def _apply(window) -> None:
    window.setStyleSheet(window.styleSheet() + "\n" + REFERENCE_STYLE)
    _ensure_top_bar(window)
    _polish_sidebar(window)
    _polish_header(window)


def _post_navigation(window) -> None:
    from monitor_noticias.ui.sections import Section
    _polish_sidebar(window)
    _polish_header(window)
    top = getattr(window, "reference_top_bar", None)
    if top is not None:
        top.show()
    # Home e ferramentas de workspace mantêm os próprios heróis, mas a barra global
    # continua visível em todas as telas, como nas referências.
    if getattr(window, "_current", None) in {Section.HOME, Section.EXTRACTOR, Section.SHEET_AUTOMATION}:
        window.content_layout.setContentsMargins(0, 0, 0, 0)
        window.content_layout.setSpacing(0)
    else:
        window.content_layout.setContentsMargins(0, 0, 0, 0)
        window.content_layout.setSpacing(10)


def install_v014_full_reference_layout() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    from monitor_noticias.ui.main_window import MainWindow

    old_build = MainWindow._build_ui
    old_nav = MainWindow.navigate
    old_tick = MainWindow._tick

    def build(self):
        old_build(self)
        _apply(self)

    def navigate(self, section):
        old_nav(self, section)
        _post_navigation(self)

    def tick(self):
        old_tick(self)
        # Mantém o clima usando exatamente o mecanismo já existente no RadarHeader.
        try:
            self.header_widget.update_runtime(self.controller)
        except Exception:
            pass
        top = getattr(self, "reference_top_bar", None)
        if top is not None:
            top.sync()

    MainWindow._build_ui = build
    MainWindow.navigate = navigate
    MainWindow._tick = tick
