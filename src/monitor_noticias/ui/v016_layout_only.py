from __future__ import annotations

"""v0.0.16 — somente layout.

Regra: imagens fornecidas = verdade visual; widgets/paginas/callbacks existentes = verdade funcional.
Esta camada não substitui paginas, não esconde secoes e não troca callbacks.
"""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QPushButton

_INSTALLED = False

REFERENCE_STYLE = r"""
QWidget#root,QWidget#mainContent{background:#031525;color:#f2f7fd;font-family:'Segoe UI';}
QFrame#sidebar{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #031426,stop:.72 #041b2e,stop:1 #031321);border:0;border-right:1px solid #0b4c6c;border-radius:0;}
QLabel#anchorMark{color:#ffc61a;font-size:38px;font-weight:800;background:transparent;border:0;}
QLabel#brandTitle{color:#fff;font-size:16px;font-weight:800;} QLabel#brandSub{color:#9eb7ce;font-size:9px;}
QPushButton#navButton{background:transparent;color:#eef6ff;border:1px solid transparent;border-radius:9px;padding:7px 11px;text-align:left;font-size:11px;font-weight:500;}
QPushButton#navButton:hover{background:#06243b;border-color:#0b587e;}
QPushButton#navButton:checked{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #073a5d,stop:1 #05263f);border:1px solid #00b8ff;border-left:5px solid #00e3ff;color:#fff;font-weight:800;}
QLabel#newsBadge{background:#0b4165;color:#cdefff;border:1px solid #0c6e9a;border-radius:8px;padding:1px 5px;font-size:8px;}
QFrame#sideStatusCard{background:#051f34;border:1px solid #0a5d84;border-radius:10px;} QLabel#sideStatusTitle{color:#fff;font-size:9px;font-weight:800;} QLabel#sideStatusText,QLabel#sideStatusGood{color:#a9c2d7;font-size:8px;} QLabel#sideMotto{color:#55caff;font-size:8px;font-weight:700;letter-spacing:1px;}
QFrame#referenceTopBar{background:#03192b;border:0;border-bottom:1px solid #0a5275;}
QLineEdit#referenceGlobalSearch{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #06243a,stop:1 #10295a);color:#e7f2ff;border:1px solid #318cb8;border-radius:12px;padding:8px 15px;font-size:11px;min-height:27px;}
QLineEdit#referenceGlobalSearch:focus{border:1px solid #815cff;}
QFrame#referenceStatusOk{background:#05352f;border:1px solid #0a8b74;border-radius:10px;} QLabel#referenceStatusText{color:#fff;font-size:9px;font-weight:700;} QLabel#referenceStatusDot{color:#00e4a0;font-size:13px;font-weight:900;}
QPushButton#referenceBell{background:#061d33;color:#eef6ff;border:1px solid #17688e;border-radius:10px;min-width:40px;max-width:40px;min-height:40px;max-height:40px;}
QFrame#referenceClock{background:#061d33;border:1px solid #17688e;border-radius:10px;} QLabel#referenceDate,QLabel#referenceCity{color:#a0b8cf;font-size:8px;} QLabel#referenceTime,QLabel#referenceTemp{color:#fff;font-size:16px;font-weight:800;} QLabel#referenceSun{color:#ffd329;font-size:27px;}
QFrame#pageHeader{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #041b2e,stop:.58 #07304c,stop:1 #041828);border:1px solid #0c6189;border-radius:12px;} QLabel#pageTitle{color:#fff;font-size:28px;font-weight:800;} QLabel#pageSubtitle{color:#c5d5e5;font-size:11px;} QLabel#pageKicker{color:#48c9ff;font-size:9px;font-weight:700;} QLabel#pageIcon{color:#00bfff;font-size:33px;font-weight:800;}
QFrame#card,QFrame#techCard,QFrame#resultCard,QFrame#filterCard,QFrame#settingsBlock,QGroupBox{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #082840,stop:.55 #07243a,stop:1 #051a2d);border:1px solid #0b719c;border-radius:11px;}
QFrame#statusCard{background:#06354b;border:1px solid #0aa67d;border-radius:11px;} QFrame#warningCard{background:#3e3313;border:1px solid #c89a00;border-radius:10px;} QFrame#dangerCard{background:#341d28;border:1px solid #b53b50;border-radius:10px;}
QLineEdit,QComboBox,QSpinBox,QDateEdit,QTimeEdit,QTextEdit,QPlainTextEdit{background:#061f34;color:#f3f8ff;border:1px solid #126c96;border-radius:8px;padding:7px 9px;min-height:24px;} QLineEdit:focus,QComboBox:focus,QSpinBox:focus,QDateEdit:focus,QTimeEdit:focus,QTextEdit:focus{border:1px solid #00c7ff;}
QPushButton{border-radius:8px;min-height:30px;font-weight:700;} QPushButton[secondary='true']{background:#061f35;color:#e8f0fa;border:1px solid #126e98;} QPushButton[secondary='true']:hover{background:#082d49;border-color:#00b8ff;} QPushButton[danger='true']{background:#3d1e29;color:#ff6678;border:1px solid #d94159;} QPushButton[purple='true']{background:#5526a7;color:#fff;border:1px solid #a45cff;} QPushButton[green='true']{background:#087f5c;color:#fff;border:1px solid #16d89b;} QPushButton[gold='true']{background:#705500;color:#ffda3e;border:1px solid #d2a700;}
QTableWidget,QTreeWidget,QListWidget{background:#061d31;color:#edf7ff;border:1px solid #0a648c;border-radius:9px;gridline-color:#0a4566;alternate-background-color:#06243b;} QHeaderView::section{background:#06243b;color:#59d4ff;border:0;border-bottom:1px solid #0a5f86;padding:7px;font-size:9px;font-weight:700;}
QProgressBar{background:#071d2f;border:1px solid #0b607f;border-radius:6px;color:#eaf8ff;} QProgressBar::chunk{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #00dca9,stop:1 #2dcbff);border-radius:5px;}
QScrollArea{background:transparent;border:0;} QScrollArea QWidget#qt_scrollarea_viewport{background:transparent;} QScrollBar:vertical{background:transparent;width:5px;margin:1px;border:0;} QScrollBar::handle:vertical{background:#0b5c80;min-height:28px;border-radius:2px;}
QFrame#footerFrame{background:#031525;border-top:1px solid #0a456b;}
"""


def _apply(window) -> None:
    window.setStyleSheet(window.styleSheet() + "\n" + REFERENCE_STYLE)
    sidebar = getattr(window, "sidebar", None)
    if sidebar is not None:
        sidebar.setFixedWidth(220)
        for holder in getattr(window, "nav_holders", {}).values():
            holder.show()
        for button in getattr(window, "nav_buttons", {}).values():
            button.setFixedHeight(44)
            button.setIconSize(QSize(20, 20))
    top = getattr(window, "reference_top_bar", None)
    if top is not None:
        top.setFixedHeight(76)
        if top.layout() is not None:
            top.layout().setContentsMargins(28, 10, 18, 10)
            top.layout().setSpacing(12)
    header = getattr(window, "header_widget", None)
    if header is not None:
        header.setMinimumHeight(128)
        header.setMaximumHeight(142)
    footer = getattr(window, "footer_widget", None)
    if footer is not None:
        footer.setFixedHeight(28)
    stack = getattr(window, "stack", None)
    if stack is not None and stack.currentWidget() is not None:
        page = stack.currentWidget()
        page.setStyleSheet(page.styleSheet() + "\n" + REFERENCE_STYLE)
        for button in page.findChildren(QPushButton):
            if button.minimumHeight() < 30:
                button.setMinimumHeight(30)


def install_v016_layout_only() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True
    from monitor_noticias.ui.main_window import MainWindow
    old_build = MainWindow._build_ui
    old_nav = MainWindow.navigate

    def build(self):
        old_build(self)
        _apply(self)

    def navigate(self, section):
        old_nav(self, section)
        _apply(self)

    MainWindow._build_ui = build
    MainWindow.navigate = navigate
