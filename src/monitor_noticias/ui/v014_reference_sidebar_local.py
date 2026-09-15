from __future__ import annotations

"""Precedência local da sidebar v0.0.14 sobre o stylesheet local da v0.0.13."""

_INSTALLED = False

SIDEBAR_STYLE = r"""
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
"""


def _apply(window) -> None:
    sidebar = getattr(window, "sidebar", None)
    if sidebar is None:
        return
    sidebar.setFixedWidth(220)
    sidebar.setStyleSheet(SIDEBAR_STYLE)


def install_v014_reference_sidebar_local() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True
    from monitor_noticias.ui.main_window import MainWindow
    old_build, old_nav = MainWindow._build_ui, MainWindow.navigate

    def build(self):
        old_build(self)
        _apply(self)

    def navigate(self, section):
        old_nav(self, section)
        _apply(self)

    MainWindow._build_ui = build
    MainWindow.navigate = navigate
