from __future__ import annotations

"""Ajuste visual v0.0.13 da barra lateral, fiel à referência fornecida.

Este overlay atua somente sobre widgets já criados pela interface. Navegação,
páginas, callbacks, workers, controladores e estados continuam sendo os mesmos
da aplicação v0.0.12.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
)

_INSTALLED = False

SIDEBAR_V013_STYLE = """
QFrame#sidebar {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #02192D, stop:0.16 #021E35, stop:0.82 #03243E, stop:1 #021A2F);
    border: 1px solid #0A3C5D;
    border-radius: 0px;
}
QLabel#anchorMark {
    color:#FAC305;
    background:#06283F;
    border:2px solid #EDB707;
    border-radius:12px;
    font-family:'Segoe UI Symbol';
    font-size:34px;
    font-weight:800;
    padding:0px;
}
QLabel#brandTitle {
    color:#EAEDF1;
    font-size:17px;
    font-weight:900;
    letter-spacing:.25px;
}
QLabel#brandSub {
    color:#87A8C7;
    font-size:11px;
    font-weight:500;
}
QFrame#sideGroupHeader {
    background:transparent;
    border:0;
}
QLabel#sideGroupDash {
    color:#FAC305;
    font-size:19px;
    font-weight:900;
}
QLabel#sideGroupTitle {
    color:#79A6CF;
    font-size:11px;
    font-weight:800;
    letter-spacing:1px;
}
QPushButton#navButton {
    color:#EAEDF1;
    background:#03223A;
    border:1px solid #164A6E;
    border-left:6px solid #FAC305;
    border-radius:10px;
    padding:9px 14px 9px 18px;
    text-align:left;
    font-size:14px;
    font-weight:500;
}
QPushButton#navButton:hover {
    color:#F5F8FB;
    background:#082E4E;
    border:1px solid #24709A;
    border-left:6px solid #FAC305;
}
QPushButton#navButton:pressed {
    background:#0A3658;
    border:1px solid #2B7CA5;
    border-left:6px solid #FAC305;
}
QPushButton#navButton:checked {
    color:#FFFFFF;
    background:#252F2D;
    border:2px solid #EDB707;
    border-left:7px solid #FAC305;
    font-weight:800;
}
QPushButton#navButton:checked:hover {
    background:#2B3531;
    border:2px solid #FAC305;
    border-left:7px solid #FAC305;
}
QLabel#newsBadge {
    color:#071F33;
    background:#FAC305;
    border:0;
    border-radius:9px;
    padding:1px 5px;
    font-size:9px;
    font-weight:900;
}
QFrame#sideStatusCard {
    background:#03223A;
    border:1px solid #164A6E;
    border-left:6px solid #FAC305;
    border-radius:11px;
}
QFrame#sideStatusHeader, QFrame#sideStatusFooter {
    background:transparent;
    border:0;
}
QLabel#sideStatusRing {
    color:#FAC305;
    background:transparent;
    border:0;
    font-family:'Segoe UI Symbol';
    font-size:25px;
    font-weight:900;
}
QLabel#sideStatusBars {
    color:#FAC305;
    background:transparent;
    border:0;
    font-family:'Segoe UI Symbol';
    font-size:20px;
    font-weight:900;
    letter-spacing:1px;
}
QLabel#sideStatusTitle {
    color:#FFFFFF;
    font-size:13px;
    font-weight:800;
}
QLabel#sideStatusText {
    color:#8FB1D0;
    font-size:11px;
}
QLabel#sideStatusGood {
    font-size:11px;
    font-weight:600;
}
QLabel#sideWindowsIcon {
    color:#EAEDF1;
    background:transparent;
    border:0;
    font-family:'Segoe UI Symbol';
    font-size:20px;
    font-weight:800;
}
QFrame#sideStatusDividerTop {
    background:#164A6E;
    border:0;
}
QScrollArea#sidebarScroll {
    background:transparent;
    border:0;
}
QScrollArea#sidebarScroll > QWidget > QWidget {
    background:transparent;
}
QScrollBar:vertical {
    background:#021E35;
    width:6px;
    margin:3px 0px;
    border:0;
}
QScrollBar::handle:vertical {
    background:#164A6E;
    min-height:34px;
    border-radius:3px;
}
QScrollBar::handle:vertical:hover {
    background:#195D8B;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height:0;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background:transparent;
}
"""


def _strip_status_bullet(text: str) -> str:
    for prefix in ("●   ", "●  ", "● "):
        if text.startswith(prefix):
            return text[len(prefix):]
    return text


def _strip_version_icon(text: str) -> str:
    marker = "Windows Portable"
    index = text.find(marker)
    return text[index:] if index >= 0 else text


def _ensure_status_structure(window) -> None:
    card = getattr(window, "side_status_card", None)
    title = getattr(window, "side_status_title", None)
    if card is None or title is None:
        return
    layout = card.layout()
    if not isinstance(layout, QVBoxLayout):
        return

    header = card.findChild(QFrame, "sideStatusHeader")
    if header is None:
        title_index = layout.indexOf(title)
        if title_index < 0:
            title_index = 0
        layout.removeWidget(title)

        header = QFrame(card)
        header.setObjectName("sideStatusHeader")
        row = QHBoxLayout(header)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        ring = QLabel("◎", header)
        ring.setObjectName("sideStatusRing")
        ring.setFixedWidth(27)
        ring.setAlignment(Qt.AlignmentFlag.AlignCenter)
        glow = QGraphicsDropShadowEffect(ring)
        glow.setBlurRadius(10.0)
        glow.setOffset(0.0, 0.0)
        glow.setColor(QColor(250, 195, 5, 105))
        ring.setGraphicsEffect(glow)

        title.setParent(header)
        row.addWidget(ring, 0, Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(title, 1, Qt.AlignmentFlag.AlignVCenter)

        bars = QLabel("▂▄▆█", header)
        bars.setObjectName("sideStatusBars")
        bars.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(bars, 0, Qt.AlignmentFlag.AlignVCenter)

        layout.insertWidget(title_index, header)

        divider = QFrame(card)
        divider.setObjectName("sideStatusDividerTop")
        divider.setFixedHeight(1)
        layout.insertWidget(title_index + 1, divider)

    version = None
    for label in card.findChildren(QLabel):
        if "Windows Portable" in label.text():
            version = label
            break
    footer = card.findChild(QFrame, "sideStatusFooter")
    if version is not None and footer is None:
        version_index = layout.indexOf(version)
        if version_index < 0:
            version_index = layout.count()
        layout.removeWidget(version)
        version.setText(_strip_version_icon(version.text()))

        footer = QFrame(card)
        footer.setObjectName("sideStatusFooter")
        row = QHBoxLayout(footer)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(9)

        win = QLabel("⊞", footer)
        win.setObjectName("sideWindowsIcon")
        win.setFixedWidth(22)
        win.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setParent(footer)
        row.addWidget(win, 0, Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(version, 1, Qt.AlignmentFlag.AlignVCenter)
        layout.insertWidget(version_index, footer)

    for child in card.findChildren(QFrame, "", Qt.FindChildOption.FindDirectChildrenOnly):
        if child is header or child is footer:
            continue
        if child.height() == 1 or child.maximumHeight() == 1:
            child.setStyleSheet("background:#164A6E;border:0;")

    title.setText(_strip_status_bullet(title.text()))


def _apply_sidebar_reference(window) -> None:
    from monitor_noticias.ui.sections import Section

    sidebar = getattr(window, "sidebar", None)
    if sidebar is None:
        return

    sidebar.setFixedWidth(318)
    sidebar.setStyleSheet(SIDEBAR_V013_STYLE)

    scroll = sidebar.findChild(QScrollArea, "sidebarScroll")
    content = scroll.widget() if scroll is not None else None
    layout = content.layout() if content is not None else None
    if isinstance(layout, QVBoxLayout):
        layout.setContentsMargins(18, 13, 18, 14)
        layout.setSpacing(7)

    anchor = sidebar.findChild(QLabel, "anchorMark")
    if anchor is not None:
        anchor.setFixedSize(58, 58)
        anchor.setAlignment(Qt.AlignmentFlag.AlignCenter)

    for holder in getattr(window, "nav_holders", {}).values():
        holder.setFixedHeight(58)

    current = getattr(window, "_current", Section.HOME)
    for section, button in getattr(window, "nav_buttons", {}).items():
        button.setMinimumHeight(54)
        button.setMaximumHeight(54)
        # v0.0.12 acrescentava uma seta textual ao ativo. A referência usa
        # somente borda/faixa dourada; o estado checked original é preservado.
        button.setText(section.value.label)
        button.setChecked(section == current)

    badge = getattr(window, "news_badge", None)
    news_button = getattr(window, "nav_buttons", {}).get(Section.NEWS)
    if badge is not None and news_button is not None and badge.parent() is news_button:
        badge.setFixedWidth(29)
        badge.move(max(0, news_button.width() - 36), 18)

    card = getattr(window, "side_status_card", None)
    if card is not None:
        card.setMinimumHeight(205)
        card_layout = card.layout()
        if isinstance(card_layout, QVBoxLayout):
            card_layout.setContentsMargins(14, 11, 14, 11)
            card_layout.setSpacing(7)

    _ensure_status_structure(window)


def install_v013_sidebar_reference() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    from monitor_noticias.ui.main_window import MainWindow

    if getattr(MainWindow, "_v013_sidebar_reference", False):
        return
    MainWindow._v013_sidebar_reference = True

    previous_build = MainWindow._build_ui
    previous_navigate = MainWindow.navigate
    previous_tick = MainWindow._tick

    def build(self) -> None:
        previous_build(self)
        _apply_sidebar_reference(self)

    def navigate(self, section) -> None:
        previous_navigate(self, section)
        _apply_sidebar_reference(self)

    def tick(self) -> None:
        previous_tick(self)
        # O texto continua vindo do estado real calculado pelo _tick original;
        # apenas o marcador visual é separado para reproduzir o anel da referência.
        title = getattr(self, "side_status_title", None)
        if title is not None:
            title.setText(_strip_status_bullet(title.text()))

    MainWindow._build_ui = build
    MainWindow.navigate = navigate
    MainWindow._tick = tick
