from __future__ import annotations

"""Ajuste exclusivamente visual da sidebar, aplicado após v0.0.12.

O overlay trabalha somente sobre widgets que já existem. Navegação, páginas,
callbacks, motores e as fontes reais de estado permanecem sob responsabilidade
do código original e dos overlays anteriores.
"""

import re

from PySide6.QtCore import QByteArray, QSize, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout

_INSTALLED = False

STYLE = r"""
QFrame#sidebar{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #02192D,stop:.48 #02243D,stop:1 #021B31);border:0;border-left:1px solid #0A4264;border-right:1px solid #0B3B5A;border-radius:0}
QLabel#anchorMark{background:rgba(8,46,78,135);border:2px solid #EDB707;border-radius:14px;padding:2px}
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


def _svg_pixmap(body: str, width: int, height: int, *, view_box: str = "0 0 24 24") -> QPixmap:
    xml = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="{view_box}">{body}</svg>'
    )
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    QSvgRenderer(QByteArray(xml.encode("utf-8"))).render(painter)
    painter.end()
    return pixmap


def _anchor_pixmap() -> QPixmap:
    # Vetor local para não depender do glifo de âncora instalado no Windows.
    body = r'''
    <g fill="none" stroke="#FAC305" stroke-width="2.7" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="4.2" r="2.2"/>
      <path d="M12 6.5v12.1M8.8 8.2h6.4"/>
      <path d="M5.2 14.4H2.8v-2.3M18.8 14.4h2.4v-2.3"/>
      <path d="M3 14.3c1.1 4.2 4.2 6.4 9 6.4s7.9-2.2 9-6.4"/>
      <path d="M12 18.7l-2.4-2.3M12 18.7l2.4-2.3"/>
    </g>'''
    return _svg_pixmap(body, 56, 56)


def _gear_icon() -> QIcon:
    # Engrenagem linear mais próxima da referência do que o antigo símbolo radial.
    body = r'''
    <g fill="none" stroke="#EEF7FF" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
      <path d="M9.6 2.8h4.8l.8 2.5c.6.2 1.2.4 1.7.7l2.3-1.2 3.4 3.4-1.2 2.3c.3.5.5 1.1.7 1.7l2.5.8v4.8l-2.5.8c-.2.6-.4 1.2-.7 1.7l1.2 2.3-3.4 3.4-2.3-1.2c-.5.3-1.1.5-1.7.7l-.8 2.5H9.6l-.8-2.5c-.6-.2-1.2-.4-1.7-.7L4.8 26l-3.4-3.4 1.2-2.3c-.3-.5-.5-1.1-.7-1.7l-2.5-.8V13l2.5-.8c.2-.6.4-1.2.7-1.7L1.4 8.2l3.4-3.4L7.1 6c.5-.3 1.1-.5 1.7-.7z" transform="translate(.6 -2.4) scale(.92)"/>
      <circle cx="12" cy="12" r="3.2"/>
    </g>'''
    return QIcon(_svg_pixmap(body, 28, 28))


def _ring_pixmap() -> QPixmap:
    body = r'''
    <circle cx="12" cy="12" r="8.2" fill="none" stroke="#FAC305" stroke-width="2" opacity=".35"/>
    <circle cx="12" cy="12" r="6.3" fill="none" stroke="#FAC305" stroke-width="2.2"/>
    <circle cx="12" cy="12" r="2.1" fill="#FAC305"/>
    '''
    return _svg_pixmap(body, 30, 30)


def _bars_pixmap() -> QPixmap:
    body = r'''
    <g fill="#FAC305">
      <rect x="2" y="16" width="3" height="6" rx=".7"/>
      <rect x="7" y="12" width="3" height="10" rx=".7"/>
      <rect x="12" y="8" width="3" height="14" rx=".7"/>
      <rect x="17" y="4" width="3" height="18" rx=".7"/>
    </g>'''
    return _svg_pixmap(body, 28, 28)


def _windows_pixmap() -> QPixmap:
    body = r'''
    <g fill="#EEF7FF">
      <path d="M2 5.2l8.2-1.1v7H2zM11.4 4l10.6-1.5v8.6H11.4zM2 12.3h8.2v7L2 18.2zM11.4 12.3H22v8.6l-10.6-1.5z"/>
    </g>'''
    return _svg_pixmap(body, 24, 24)


def _without_dot(text: str) -> str:
    value = text.strip()
    return value[1:].strip() if value.startswith("●") else value


def _color_from_style(label: QLabel, fallback: str) -> str:
    match = re.search(r"#[0-9a-fA-F]{6}", label.styleSheet())
    return match.group(0) if match else fallback


def _make_dot() -> QFrame:
    dot = QFrame()
    dot.setFixedSize(10, 10)
    return dot


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

    # Os labels originais são preservados porque MainWindow._tick continua sendo
    # a única fonte de verdade dos estados exibidos.
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

    layout.setContentsMargins(14, 11, 14, 12)
    layout.setSpacing(7)

    top = QHBoxLayout()
    top.setSpacing(8)
    ring = QLabel()
    ring.setFixedSize(32, 32)
    ring.setPixmap(_ring_pixmap())
    ring.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title.setText(_without_dot(title.text()))
    bars = QLabel()
    bars.setFixedSize(30, 30)
    bars.setPixmap(_bars_pixmap())
    bars.setAlignment(Qt.AlignmentFlag.AlignCenter)
    top.addWidget(ring)
    top.addWidget(title, 1)
    top.addWidget(bars)
    layout.addLayout(top)

    d1 = QFrame(); d1.setObjectName("statusDivider"); d1.setFixedHeight(1); layout.addWidget(d1)
    if local is not None:
        layout.addWidget(local)

    window._sidebar_proxy_dot = _make_dot()
    proxy_row = QHBoxLayout(); proxy_row.setSpacing(9)
    proxy_row.addWidget(window._sidebar_proxy_dot)
    proxy_row.addWidget(proxy, 1)
    layout.addLayout(proxy_row)

    window._sidebar_automation_dot = _make_dot()
    automation_row = QHBoxLayout(); automation_row.setSpacing(9)
    automation_row.addWidget(window._sidebar_automation_dot)
    automation_row.addWidget(automation, 1)
    layout.addLayout(automation_row)

    d2 = QFrame(); d2.setObjectName("statusDivider"); d2.setFixedHeight(1); layout.addWidget(d2)

    if version is not None:
        text = version.text().strip()
        for prefix in ("▣", "⊞"):
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        version.setText(text)
        version_row = QHBoxLayout(); version_row.setSpacing(9)
        windows = QLabel(); windows.setFixedSize(25, 25); windows.setPixmap(_windows_pixmap()); windows.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_row.addWidget(windows)
        version_row.addWidget(version, 1)
        layout.addLayout(version_row)

    _sync_status_visuals(window)


def _sync_status_visuals(window) -> None:
    # Primeiro o _tick original grava texto e cores a partir do estado real;
    # aqui apenas transformamos os marcadores textuais em formas visuais.
    for attr in ("side_status_title", "side_proxy", "side_automation"):
        label = getattr(window, attr, None)
        if isinstance(label, QLabel):
            label.setText(_without_dot(label.text()))

    proxy_dot = getattr(window, "_sidebar_proxy_dot", None)
    if proxy_dot is not None:
        color = _color_from_style(window.side_proxy, "#FAC305")
        proxy_dot.setStyleSheet(f"background:{color};border:0;border-radius:5px;")

    automation_dot = getattr(window, "_sidebar_automation_dot", None)
    if automation_dot is not None:
        color = _color_from_style(window.side_automation, "#05DBA8")
        automation_dot.setStyleSheet(f"background:{color};border:0;border-radius:5px;")


def _polish(window) -> None:
    sidebar = getattr(window, "sidebar", None)
    if sidebar is None:
        return

    sidebar.setFixedWidth(318)
    sidebar.setStyleSheet(STYLE)

    scroll = sidebar.findChild(QScrollArea, "sidebarScroll")
    content = scroll.widget() if scroll is not None else None
    layout = content.layout() if content is not None else None
    if isinstance(layout, QVBoxLayout):
        layout.setContentsMargins(18, 18, 18, 14)
        layout.setSpacing(7)

    anchor = sidebar.findChild(QLabel, "anchorMark")
    if anchor is not None:
        anchor.setText("")
        anchor.setFixedSize(78, 78)
        anchor.setPixmap(_anchor_pixmap())
        anchor.setAlignment(Qt.AlignmentFlag.AlignCenter)

    for section, button in window.nav_buttons.items():
        button.setText(section.value.label)
        button.setMinimumHeight(54)
        button.setMaximumHeight(54)
        button.setToolTip(section.value.label)

    # A v0.0.12 já fornece ícones SVG. Corrigimos apenas Configurações para uma
    # engrenagem inequívoca, sem trocar o sistema de ícones ou dependências.
    from monitor_noticias.ui.sections import Section
    settings = window.nav_buttons.get(Section.SETTINGS)
    if settings is not None:
        settings.setIcon(_gear_icon())
        settings.setIconSize(QSize(28, 28))

    _status_card(window)


def install_v013_sidebar_reference() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    from monitor_noticias.ui.main_window import MainWindow

    old_build, old_nav, old_tick = MainWindow._build_ui, MainWindow.navigate, MainWindow._tick

    def build(self):
        old_build(self)
        _polish(self)

    def navigate(self, section):
        old_nav(self, section)
        _polish(self)

    def tick(self):
        old_tick(self)
        _sync_status_visuals(self)

    MainWindow._build_ui = build
    MainWindow.navigate = navigate
    MainWindow._tick = tick
