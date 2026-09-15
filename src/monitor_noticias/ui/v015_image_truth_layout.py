from __future__ import annotations

"""Camada visual v0.0.15 guiada diretamente pelas imagens de referência.
Imagens = verdade visual; código existente = verdade funcional.
"""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QLabel, QPushButton

_INSTALLED = False

IMAGE_TRUTH_STYLE = r"""
QWidget#root,QWidget#mainContent{background:#031625;color:#eef7ff;font-family:'Segoe UI';}
QFrame#referenceTopBar{background:#03192b;border:0;border-bottom:1px solid #0b557a;}
QLineEdit#referenceGlobalSearch{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #06243a,stop:1 #10295a);color:#dceafb;border:1px solid #2d8fc2;border-radius:12px;padding:9px 16px;font-size:12px;min-height:26px;}
QLineEdit#referenceGlobalSearch:focus{border:1px solid #7d5cff;}
QFrame#referenceStatusOk{background:#043632;border:1px solid #0a8c77;border-radius:10px;}
QLabel#referenceStatusText{color:#fff;font-size:10px;font-weight:700;} QLabel#referenceStatusDot{color:#00e3a1;font-size:14px;font-weight:900;}
QPushButton#referenceBell{background:#061d33;color:#e7f3ff;border:1px solid #17688e;border-radius:10px;min-width:40px;max-width:40px;min-height:40px;max-height:40px;font-size:18px;}
QFrame#referenceClock{background:#061d33;border:1px solid #17688e;border-radius:10px;} QLabel#referenceDate,QLabel#referenceCity{color:#9fb9d1;font-size:9px;} QLabel#referenceTime,QLabel#referenceTemp{color:#fff;font-size:17px;font-weight:800;} QLabel#referenceSun{color:#ffd027;font-size:28px;font-weight:800;}
QFrame#sidebar{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #041426,stop:.68 #05192b,stop:1 #031525);border:0;border-right:1px solid #0b4565;border-radius:0;}
QLabel#anchorMark{color:#ffc400;background:transparent;border:0;font-size:38px;font-weight:800;} QLabel#brandTitle{color:#f7fbff;font-size:16px;font-weight:800;} QLabel#brandSub{color:#9eb6cb;font-size:9px;font-weight:500;}
QFrame#sideGroupHeader,QLabel#sideGroupDash,QLabel#sideGroupTitle{background:transparent;border:0;color:transparent;max-height:0px;min-height:0px;}
QPushButton#navButton{color:#eef6ff;background:transparent;border:1px solid transparent;border-radius:9px;padding:7px 12px;text-align:left;font-size:11px;font-weight:500;} QPushButton#navButton:hover{background:#06243d;border-color:#0d567a;} QPushButton#navButton:checked{color:#fff;background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #073a5f,stop:1 #062845);border:1px solid #00b8ff;border-left:5px solid #00e7ff;font-weight:800;}
QLabel#newsBadge{background:transparent;color:transparent;min-width:0;max-width:0;padding:0;border:0;} QScrollArea#sidebarScroll,QScrollArea#sidebarScroll>QWidget>QWidget{background:transparent;border:0;} QScrollBar:vertical{background:transparent;width:4px;margin:1px 0;border:0;} QScrollBar::handle:vertical{background:#0b5b7f;min-height:28px;border-radius:2px;}
QFrame#pageHeader{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #051d31,stop:.58 #07314d,stop:1 #04192b);border:1px solid #0d6289;border-radius:12px;} QLabel#pageKicker{color:#45c9ff;font-size:9px;font-weight:700;} QLabel#pageTitle{color:#fff;font-size:28px;font-weight:800;} QLabel#pageSubtitle{color:#c3d4e4;font-size:11px;} QLabel#pageIcon{color:#00b9ff;font-size:34px;font-weight:800;}
QFrame#card,QFrame#techCard,QFrame#resultCard,QFrame#filterCard,QFrame#settingsBlock,QGroupBox,QTableWidget,QTreeWidget,QListWidget{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #08283f,stop:.55 #07233a,stop:1 #051a2d);border:1px solid #0b6f99;border-radius:11px;} QFrame#resultCard:hover,QFrame#techCard:hover{border-color:#00bfff;}
QLineEdit,QComboBox,QSpinBox,QDateEdit,QTimeEdit,QTextEdit,QPlainTextEdit{background:#061e34;color:#f2f8ff;border:1px solid #126c95;border-radius:8px;padding:7px 9px;min-height:24px;selection-background-color:#0a8cff;} QLineEdit:focus,QComboBox:focus,QSpinBox:focus,QDateEdit:focus,QTimeEdit:focus,QTextEdit:focus{border:1px solid #00c8ff;}
QPushButton{border-radius:8px;min-height:30px;} QPushButton[secondary='true']{background:#061f35;color:#e5eef8;border:1px solid #126d97;} QPushButton[secondary='true']:hover{background:#082c49;border-color:#00b7ff;}
QHeaderView::section{background:#06243b;color:#59d4ff;border:0;border-bottom:1px solid #0a5f86;padding:7px;font-size:10px;font-weight:700;} QTableWidget,QTreeWidget{gridline-color:#0a4566;alternate-background-color:#061d31;} QTableWidget::item,QTreeWidget::item{padding:6px;}
QProgressBar{background:#061b2e;border:1px solid #0c607f;border-radius:7px;text-align:center;color:#eaf8ff;} QProgressBar::chunk{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #00deaa,stop:1 #2ecfff);border-radius:6px;} QFrame#footerFrame{background:#031525;border-top:1px solid #0a456b;}
"""


def _install_sidebar_footer(window) -> None:
    sidebar=getattr(window,'sidebar',None)
    if sidebar is None or getattr(window,'_v015_footer',None) is not None:return
    from PySide6.QtWidgets import QFrame,QVBoxLayout
    footer=QFrame(sidebar);footer.setObjectName('v015SidebarFooter');footer.setStyleSheet("QFrame#v015SidebarFooter{background:transparent;border:0;} QLabel{background:transparent;border:0;color:#9cb5ca;font-size:8px;}")
    lay=QVBoxLayout(footer);lay.setContentsMargins(18,4,12,12);lay.setSpacing(1)
    for text in ('v0.0.15','Monitor de Notícias','Inteligência de mídia','para melhores decisões'):lay.addWidget(QLabel(text))
    window._v015_footer=footer
    shell=sidebar.layout()
    if shell is not None:shell.addWidget(footer)


def _hide_non_reference_nav(window) -> None:
    from monitor_noticias.ui.sections import Section
    for section in (Section.STOP,Section.NEWS_EXTRACTOR,Section.SHEET_AUTOMATION):
        holder=getattr(window,'nav_holders',{}).get(section)
        if holder is not None:holder.hide()


def _apply_geometry(window) -> None:
    sidebar=getattr(window,'sidebar',None)
    if sidebar is not None:sidebar.setFixedWidth(218)
    top=getattr(window,'reference_top_bar',None)
    if top is not None:
        top.setFixedHeight(76);top.layout().setContentsMargins(28,10,18,10);top.layout().setSpacing(12)
        try:
            top.search.setMinimumWidth(520);top.search.setMaximumHeight(44);top.search.setPlaceholderText('Buscar notícias, fontes, demandas... ou digite um comando')
        except Exception:pass
    header=getattr(window,'header_widget',None)
    if header is not None:header.setMinimumHeight(128);header.setMaximumHeight(142)
    try:window.content_layout.setContentsMargins(0,0,0,0);window.content_layout.setSpacing(8)
    except Exception:pass


def _polish_sidebar(window) -> None:
    sidebar=getattr(window,'sidebar',None)
    if sidebar is None:return
    sidebar.setStyleSheet(sidebar.styleSheet()+'\n'+IMAGE_TRUTH_STYLE)
    for button in getattr(window,'nav_buttons',{}).values():button.setFixedHeight(44);button.setIconSize(QSize(20,20))
    badge=getattr(window,'news_badge',None)
    if badge is not None:badge.hide()
    card=getattr(window,'side_status_card',None)
    if card is not None:card.hide()
    for child in sidebar.findChildren(QLabel):
        if child.objectName() in {'sideMotto','sideGroupDash','sideGroupTitle'}:child.hide()
    _hide_non_reference_nav(window);_install_sidebar_footer(window)


def _polish_page(window) -> None:
    stack=getattr(window,'stack',None)
    if stack is None:return
    current=stack.currentWidget()
    if current is None:return
    current.setStyleSheet(current.styleSheet()+'\n'+IMAGE_TRUTH_STYLE)
    for button in current.findChildren(QPushButton):
        if button.height()<30:button.setMinimumHeight(30)


def _apply(window) -> None:
    window.setStyleSheet(window.styleSheet()+'\n'+IMAGE_TRUTH_STYLE);_apply_geometry(window);_polish_sidebar(window);_polish_page(window)


def install_v015_image_truth_layout() -> None:
    global _INSTALLED
    if _INSTALLED:return
    _INSTALLED=True
    from monitor_noticias.ui.main_window import MainWindow
    old_build,old_nav,old_tick=MainWindow._build_ui,MainWindow.navigate,MainWindow._tick
    def build(self):old_build(self);_apply(self)
    def navigate(self,section):old_nav(self,section);_apply_geometry(self);_polish_sidebar(self);_polish_page(self)
    def tick(self):old_tick(self);_apply_geometry(self)
    MainWindow._build_ui=build;MainWindow.navigate=navigate;MainWindow._tick=tick
