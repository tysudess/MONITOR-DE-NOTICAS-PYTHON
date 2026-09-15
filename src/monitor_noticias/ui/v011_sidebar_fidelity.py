from __future__ import annotations

"""Barra lateral v0.0.11 fiel à referência visual enviada pelo usuário."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout

_INSTALLED = False

SIDEBAR_V011_STYLE = """
QFrame#sidebar {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #03192c, stop:0.42 #042e4d, stop:0.78 #03213a, stop:1 #021527);
    border: 1px solid #055f8d;
    border-radius: 0px;
}
QLabel#anchorMark {
    color:#ffc400;
    background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #0a3348,stop:1 #071c2b);
    border:2px solid #ffc400;
    border-radius:14px;
    font-family:'Segoe UI Symbol'; font-size:42px; font-weight:800;
    padding:3px;
}
QLabel#brandTitle { color:#f7fbff; font-size:23px; font-weight:900; letter-spacing:.4px; }
QLabel#brandSub { color:#7aa7cf; font-size:13px; font-weight:500; }
QFrame#sideGroupHeader { background:transparent; border:0; }
QLabel#sideGroupDash { color:#ffc400; font-size:20px; font-weight:900; }
QLabel#sideGroupTitle { color:#78a8d0; font-size:12px; font-weight:800; letter-spacing:1px; }
QPushButton#navButton {
    color:#f4f7fb;
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #07314d,stop:1 #05243d);
    border:1px solid #0c77aa;
    border-left:6px solid #ffc400;
    border-radius:11px;
    padding:10px 14px 10px 18px;
    text-align:left;
    font-size:15px;
    font-weight:600;
}
QPushButton#navButton:hover {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0a4264,stop:1 #07304b);
    border:1px solid #27aee4;
    border-left:6px solid #ffc400;
}
QPushButton#navButton:checked {
    color:#ffffff;
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #273d38,stop:1 #122b32);
    border:2px solid #ffc400;
    border-left:8px solid #ffc400;
    font-weight:900;
}
QLabel#newsBadge {
    color:#072139; background:#ffc400; border-radius:10px;
    padding:2px 7px; font-size:9px; font-weight:900;
}
QFrame#sideStatusCard {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #07304b,stop:1 #04243e);
    border:1px solid #0c78aa;
    border-left:6px solid #ffc400;
    border-radius:12px;
}
QLabel#sideStatusTitle { color:#ffffff; font-size:13px; font-weight:900; }
QLabel#sideStatusText { color:#79a9d2; font-size:11px; }
QLabel#sideStatusGood { color:#05dba8; font-size:11px; font-weight:600; }
QLabel#sideMotto { color:transparent; font-size:1px; }
QScrollArea#sidebarScroll { background:transparent; border:0; }
QScrollArea#sidebarScroll > QWidget > QWidget { background:transparent; }
QScrollBar:vertical { background:#021527; width:8px; margin:3px 1px; border:0; }
QScrollBar::handle:vertical { background:#0b77a8; min-height:34px; border-radius:4px; }
QScrollBar::handle:vertical:hover { background:#14aee6; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background:transparent; }
"""


def _group_header(text: str) -> QFrame:
    frame = QFrame()
    frame.setObjectName("sideGroupHeader")
    layout = QHBoxLayout(frame)
    layout.setContentsMargins(2, 8, 0, 5)
    layout.setSpacing(8)
    dash = QLabel("━")
    dash.setObjectName("sideGroupDash")
    dash.setFixedWidth(28)
    title = QLabel(text)
    title.setObjectName("sideGroupTitle")
    layout.addWidget(dash)
    layout.addWidget(title, 1)
    return frame


def install_v011_sidebar_fidelity() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    from monitor_noticias.ui.main_window import MainWindow, SidebarShipArt
    from monitor_noticias.ui.sections import Section

    original_build = MainWindow._build_ui

    def build(self) -> None:
        original_build(self)
        self.sidebar.setFixedWidth(318)
        self.sidebar.setStyleSheet(SIDEBAR_V011_STYLE)

        scroll = self.sidebar.findChild(QScrollArea, "sidebarScroll")
        content = scroll.widget() if scroll is not None else None
        layout = content.layout() if content is not None else None
        if not isinstance(layout, QVBoxLayout):
            return
        layout.setContentsMargins(18, 18, 18, 14)
        layout.setSpacing(7)

        anchor = self.sidebar.findChild(QLabel, "anchorMark")
        if anchor is not None:
            anchor.setFixedSize(78, 78)
            anchor.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Rótulos e símbolos seguem a referência visual; a navegação e os
        # Section originais permanecem inalterados.
        icons = {
            Section.HOME: "⌂",
            Section.NEWS: "▤",
            Section.VIDEOS: "▷",
            Section.DEMANDS: "✉",
            Section.SOURCES: "◉",
            Section.HISTORY: "◷",
            Section.TERMS: "⌕",
            Section.STOP: "■",
            Section.PDF_EDITOR: "▧",
            Section.EXTRACTOR: "▦",
            Section.VIDEO_EDITOR: "▰",
            Section.NEWS_EXTRACTOR: "✧",
            Section.SHEET_AUTOMATION: "▦",
            Section.COVERS: "▧",
            Section.SETTINGS: "⚙",
        }
        for section, button in self.nav_buttons.items():
            button.setText(f"{icons.get(section, section.value.icon)}      {section.value.label}")
            button.setMinimumHeight(54)

        groups = (
            ("PRINCIPAL", Section.HOME),
            ("GERENCIAMENTO", Section.DEMANDS),
            ("FERRAMENTAS", Section.PDF_EDITOR),
            ("SISTEMA", Section.SETTINGS),
        )
        for title, first in groups:
            holder = self.nav_holders[first]
            idx = layout.indexOf(holder)
            if idx >= 0:
                layout.insertWidget(idx, _group_header(title))

        # O modelo de referência termina no card de estado: remove a arte naval
        # e o antigo lema para não criar elementos que não existem na figura.
        for ship in self.sidebar.findChildren(SidebarShipArt):
            ship.hide()
            ship.setMaximumHeight(0)
        for label in self.sidebar.findChildren(QLabel):
            if label.objectName() == "sideMotto" or label.text().strip() == "━━":
                label.hide()

        self.side_status_card.setMinimumHeight(210)
        self.side_status_title.setText("◉   Busca em andamento")
        # A versão exibida na figura de referência é deliberadamente mantida.
        for label in self.side_status_card.findChildren(QLabel):
            if label.text().startswith("Windows Portable"):
                label.setText("▣   Windows Portable v4.0.2")

    MainWindow._build_ui = build
