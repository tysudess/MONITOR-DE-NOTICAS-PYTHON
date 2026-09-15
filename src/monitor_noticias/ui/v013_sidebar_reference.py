from __future__ import annotations

"""Ajuste exclusivamente visual da sidebar, aplicado após v0.0.12."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout

_INSTALLED = False

STYLE = r"""
QFrame#sidebar{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #02192D,stop:.48 #02243D,stop:1 #021B31);border:0;border-left:1px solid #0A4264;border-right:1px solid #0B3B5A;border-radius:0}
QLabel#anchorMark{color:#FAC305;background:rgba(8,46,78,135);border:2px solid #EDB707;border-radius:14px;font-family:'Segoe UI Symbol';font-size:43px;font-weight:800;padding:2px}
QLabel#brandTitle{color:#EAEDF1;font-family:'Segoe UI';font-size:23px;font-weight:800}
QLabel#brandSub{color:#86A7C6;font-family:'Segoe UI';font-size:13px;font-weight:500}
QFrame#sideGroupHeader{background:transparent;border:0}
QLabel#sideGroupDash{color:#FAC305;font-size:21px;font-weight:900}
QLabel#sideGroupTitle{color:#7EA6C8;font-family:'Segoe UI';font-size:12px;font-weight:700;letter-spacing:1.2px}
QPushButton#navButton{color:#EAEDF1;background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #062B49,stop:.58 #05243E,stop:1 #041F37);border:1px solid #164A6E;border-left:7px solid #FAC305;border-radius:11px;padding:9px 14px 9px 18px;text-align:left;font-family:'Segoe UI';font-size:15px;font-weight:500}
QPushButton#navButton:hover{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #083655,stop:.58 #072C49,stop:1 #05243D);border:1px solid #236B96;border-left:7px solid #FAC305}
QPushButton#navButton:pressed{background:#082E4E}
QPushButton#navButton:checked{color:#FFF;background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #303A32,stop:.55 #26372F,stop:1 #132B32);border:2px solid #EDB707;border-left:8px solid #FAC305;font-weight:700}
QLabel#newsBadge{color:#08233B;background:#FAC305;border:1px solid #EDB707;border-radius:9px;padding:1px 5px;font-size:9px;font-weight:800}
QFrame#sideStatusCard{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #062B49,stop:.55 #052640,stop:1 #041F37);border:1px solid #164A6E;border-left:7px solid #FAC305;border-radius:12px}
QLabel#statusRing{color:#FAC305;font-size:29px;font-weight:900}
QLabel#statusBars{color:#FAC305;font-family:'Segoe UI Symbol';font-size:24px;font-weight:900}
QLabel#sideStatusTitle{color:#FFF;font-family:'Segoe UI';font-size:13px;font-weight:800}
QLabel#sideStatusText{color:#89AACA;font-family:'Segoe UI';font-size:11px;font-weight:500}
QLabel#sideStatusGood{font-family:'Segoe UI';font-size:11px;font-weight:600}
QFrame#statusDivider{background:#195D8B;border:0}
QScrollArea#sidebarScroll{background:transparent;border:0}
QScrollArea#sidebarScroll>QWidget>QWidget{background:transparent}
QScrollBar:vertical{background:transparent;width:6px;margin:3px 0;border:0}
QScrollBar::handle:vertical{background:#164A6E;min-height:34px;border-radius:3px}
QScrollBar::handle:vertical:hover{background:#195D8B}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0}
QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical{background:transparent}
"""


def _without_dot(text: str) -> str:
    value = text.strip()
    return value[1:].strip() if value.startswith("●") else value


def _status_card(window) -> None:
    card = getattr(window, "side_status_card", None)
    if card is None or getattr(card, "_reference_ready", False):
        return
    card._reference_ready = True
    card.setMinimumHeight(220)
    card.setMaximumHeight(236)
    layout = card.layout()
    if not isinstance(layout, QVBoxLayout):
        return
    title, proxy, automation = window.side_status_title, window.side_proxy, window.side_automation
    local = version = None
    for label in card.findChildren(QLabel):
        text = label.text().strip()
        if text.startswith("Dados locais"):
            local = label
        elif "Windows Portable" in text:
            version = label
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
    layout.setContentsMargins(14,11,14,12)
    layout.setSpacing(7)
    top = QHBoxLayout(); top.setSpacing(8)
    ring = QLabel("◎"); ring.setObjectName("statusRing"); ring.setFixedWidth(34); ring.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setText(_without_dot(title.text()))
    bars = QLabel("▂▄▆█"); bars.setObjectName("statusBars"); bars.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
    top.addWidget(ring); top.addWidget(title,1); top.addWidget(bars); layout.addLayout(top)
    d1=QFrame(); d1.setObjectName("statusDivider"); d1.setFixedHeight(1); layout.addWidget(d1)
    if local is not None: layout.addWidget(local)
    layout.addWidget(proxy); layout.addWidget(automation)
    d2=QFrame(); d2.setObjectName("statusDivider"); d2.setFixedHeight(1); layout.addWidget(d2)
    if version is not None:
        text=version.text().strip()
        if text.startswith("▣"): text=text[1:].strip()
        version.setText(f"⊞   {text}"); layout.addWidget(version)


def _polish(window) -> None:
    sidebar=getattr(window,"sidebar",None)
    if sidebar is None: return
    sidebar.setFixedWidth(318); sidebar.setStyleSheet(STYLE)
    scroll=sidebar.findChild(QScrollArea,"sidebarScroll")
    content=scroll.widget() if scroll is not None else None
    layout=content.layout() if content is not None else None
    if isinstance(layout,QVBoxLayout): layout.setContentsMargins(18,18,18,14); layout.setSpacing(7)
    anchor=sidebar.findChild(QLabel,"anchorMark")
    if anchor is not None: anchor.setFixedSize(78,78); anchor.setAlignment(Qt.AlignmentFlag.AlignCenter)
    for section,button in window.nav_buttons.items():
        button.setText(section.value.label); button.setMinimumHeight(54); button.setMaximumHeight(54); button.setToolTip(section.value.label)
    _status_card(window)


def install_v013_sidebar_reference() -> None:
    global _INSTALLED
    if _INSTALLED: return
    _INSTALLED=True
    from monitor_noticias.ui.main_window import MainWindow
    old_build,old_nav,old_tick=MainWindow._build_ui,MainWindow.navigate,MainWindow._tick
    def build(self): old_build(self); _polish(self)
    def navigate(self,section): old_nav(self,section); _polish(self)
    def tick(self):
        old_tick(self)
        self.side_status_title.setText(_without_dot(self.side_status_title.text()))
    MainWindow._build_ui=build; MainWindow.navigate=navigate; MainWindow._tick=tick
