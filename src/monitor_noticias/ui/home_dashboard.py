from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from monitor_noticias.ui.controller import MainUiController, UiState


HOME_STYLESHEET = """
QWidget#homeDashboard {
    background: #031b30;
    color: #f4f7fb;
    font-family: 'Segoe UI';
}
QWidget#homeBody {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #031b30, stop:0.55 #032743, stop:1 #02172a);
}
QScrollArea#homeScroll {
    background: #031b30;
    border: none;
}
QScrollArea#homeScroll QWidget#qt_scrollarea_viewport {
    background: #031b30;
    border: none;
}
QLabel { color: #f4f7fb; background: transparent; }
QLabel#homeWelcome { color:#ffffff; font-size: 31px; font-weight: 800; }
QLabel#homeSubtitle { color: #c5d7e8; font-size: 13px; }
QLabel#homeSlogan { color: #6ec8ff; font-size: 10px; font-weight: 800; letter-spacing: 1.5px; }
QLabel#homeDate { color: #9ab6d0; font-size: 9px; }
QLabel#homeClock { color: #f4f7fb; font-size: 17px; font-weight: 800; }
QLabel#homeWeatherCity { color: #c7d9ea; font-size: 10px; }
QLabel#homeWeatherTemp { color: #f4f7fb; font-size: 16px; font-weight: 800; }
QLineEdit#homeSearch {
    background: rgba(2,24,43,225);
    color: #eef8ff;
    border: 1px solid #0e8fcb;
    border-radius: 11px;
    padding: 10px 14px;
    min-height: 23px;
    selection-background-color: #087af7;
}
QLineEdit#homeSearch:focus { border: 1px solid #00b7ff; }
QFrame#metricCard, QFrame#dashboardCard, QFrame#miniCard {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #06375c, stop:0.50 #05304e, stop:1 #031f39);
    border: 1px solid #087eae;
    border-radius: 12px;
}
QFrame#metricCard:hover, QFrame#dashboardCard:hover { border-color: #00a9e8; }
QFrame#metricIcon { border-radius: 11px; }
QLabel#metricTitle { color: #d6e4f1; font-size: 11px; font-weight: 500; }
QLabel#metricValue { color: #ffffff; font-size: 28px; font-weight: 800; }
QLabel#cardTitle { color: #ffffff; font-size: 15px; font-weight: 800; }
QLabel#cardSubtitle { color: #b9cde0; font-size: 10px; }
QLabel#kicker { color: #7bd3ff; font-size: 10px; font-weight: 700; letter-spacing: 1.2px; }
QLabel#heroTitle { color: #ffffff; font-size: 31px; font-weight: 800; }
QLabel#heroBody { color: #c0d2e3; font-size: 11px; }
QLabel#heroRail { color: #2cc5ff; font-size: 11px; font-weight: 800; letter-spacing: 1.4px; }
QFrame#statusPanel { background: #052d42; border: 1px solid #0cb87b; border-radius: 9px; }
QLabel#statusReady { color: #25e68f; font-size: 11px; font-weight: 800; }
QLabel#statusPct { color: #ffffff; font-size: 10px; font-weight: 800; }
QProgressBar#homeProgress {
    background: #12384b;
    border: 0;
    border-radius: 3px;
    min-height: 6px;
    max-height: 6px;
    text-align: center;
}
QProgressBar#homeProgress::chunk { background: #25e68f; border-radius: 3px; }
QPushButton#quickBlue, QPushButton#quickPurple, QPushButton#quickOrange, QPushButton#quickGreen {
    color: white;
    border: 1px solid rgba(255,255,255,42);
    border-radius: 10px;
    padding: 11px 14px;
    text-align: left;
    font-size: 12px;
    font-weight: 800;
    min-height: 61px;
}
QPushButton#quickBlue { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #087af7, stop:1 #005fc9); }
QPushButton#quickBlue:hover { background: #118cff; }
QPushButton#quickPurple { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #6b2ddd, stop:1 #9a43ed); }
QPushButton#quickPurple:hover { background: #8244ed; }
QPushButton#quickOrange { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #d97900, stop:1 #ff9900); }
QPushButton#quickOrange:hover { background: #ef8b00; }
QPushButton#quickGreen { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #07865f, stop:1 #03aa72); }
QPushButton#quickGreen:hover { background: #0aa879; }
QFrame#scheduleBox {
    background: #052d4d;
    border: 1px solid #0b6e9d;
    border-radius: 8px;
}
QLabel#scheduleName { color: #f4f7fb; font-size: 10px; font-weight: 700; }
QLabel#scheduleValueBlue { color: #1ea7ff; font-size: 11px; font-weight: 800; }
QLabel#scheduleValueOrange { color: #ffc21a; font-size: 11px; font-weight: 800; }
QLabel#scheduleValuePurple { color: #bd78ff; font-size: 10px; font-weight: 700; }
QLabel#summaryName { color: #bed0e1; font-size: 10px; }
QLabel#summaryBlue { color: #168fff; font-size: 28px; font-weight: 800; }
QLabel#summaryPurple { color: #a95dff; font-size: 28px; font-weight: 800; }
QLabel#summaryOrange { color: #ff9700; font-size: 28px; font-weight: 800; }
QLabel#smallContent { color: #b6cce2; font-size: 9px; }
QLabel#footerText { color: #9bb7cf; font-size: 9px; }
QLabel#footerStatus { color: #b8cadb; font-size: 9px; }
"""


REFINED_SIDEBAR_STYLESHEET = """
QFrame#sidebar {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #052e50, stop:0.58 #042642, stop:1 #031a30);
    border: 1px solid #087eae;
    border-radius: 14px;
}
QLabel#brandTitle { color:#ffffff; font-size:17px; font-weight:800; }
QLabel#brandSub { color:#a8c3db; font-size:10px; }
QLabel#anchorMark { color:#f5aa00; font-family:'Segoe UI Symbol'; font-size:46px; font-weight:700; }
QPushButton#navButton {
    color:#eef6ff;
    background:transparent;
    border:0;
    border-radius:9px;
    padding:9px 12px;
    text-align:left;
    font-size:13px;
    font-weight:500;
}
QPushButton#navButton:hover { background:#083657; }
QPushButton#navButton:checked {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0a659d,stop:1 #06375d);
    border:1px solid #00a9e8;
    color:#ffffff;
    font-weight:800;
}
QLabel#newsBadge {
    color:#062440;
    background:#ffc21a;
    border-radius:10px;
    padding:2px 7px;
    font-size:9px;
    font-weight:800;
}
QFrame#sideStatusCard {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #052b48,stop:1 #03233c);
    border:1px solid #0a638d;
    border-radius:10px;
}
QLabel#sideStatusTitle { color:#ffffff; font-size:10px; font-weight:800; }
QLabel#sideStatusText { color:#a9c6df; font-size:9px; }
QLabel#sideStatusGood { color:#a9c6df; font-size:9px; }
QLabel#sideMotto { color:#54bff2; font-size:8px; font-weight:700; letter-spacing:1px; }
"""


def _frame(name: str, margins=(14, 12, 14, 12), spacing: int = 8) -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName(name)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    return frame, layout


def _label(text: str = "", object_name: str = "") -> QLabel:
    label = QLabel(text)
    if object_name:
        label.setObjectName(object_name)
    return label


class DashboardHeader(QWidget):
    """Paints the radar/technical background visible behind the header."""

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        center = QPointF(self.width() * 0.39, self.height() * 0.50)

        p.setPen(Qt.PenStyle.NoPen)
        for radius, alpha in ((72, 8), (56, 12), (40, 16), (24, 22), (10, 28)):
            p.setBrush(QColor(0, 168, 235, alpha))
            p.drawEllipse(center, radius, radius)

        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor(0, 150, 220, 56), 1))
        for radius in (24, 44, 64, 84, 104, 124):
            p.drawEllipse(center, radius, radius)
        p.drawLine(QPointF(center.x() - 150, center.y()), QPointF(center.x() + 150, center.y()))
        p.drawLine(QPointF(center.x(), max(0, center.y() - 108)), QPointF(center.x(), min(self.height(), center.y() + 108)))

        p.setPen(QPen(QColor(0, 190, 255, 95), 1))
        p.drawLine(QPointF(center.x(), 0), QPointF(center.x(), self.height()))
        p.setPen(QPen(QColor(0, 210, 255, 190), 2))
        p.drawEllipse(center, 4, 4)
        p.setPen(QPen(QColor(0, 136, 196, 42), 1))
        p.drawLine(QPointF(0, 14), QPointF(self.width() * 0.70, 14))


class LeafIcon(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setFixedSize(48, 48)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#19cc87"))
        p.drawEllipse(QRectF(7, 11, 34, 23))
        p.setBrush(QColor("#031f37"))
        p.drawEllipse(QRectF(1, 22, 27, 18))
        p.setPen(QPen(QColor("#042842"), 2))
        p.drawLine(QPointF(17, 34), QPointF(31, 18))


class RoundIcon(QWidget):
    def __init__(self, kind: str, size: int = 42) -> None:
        super().__init__()
        self.kind = kind
        self.setFixedSize(size, size)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        r = self.rect().adjusted(2, 2, -2, -2)
        if self.kind == "user":
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor("#0a5c92"))
            p.drawEllipse(r)
            p.setBrush(QColor("#eff8ff"))
            p.drawEllipse(QRectF(self.width() * .39, self.height() * .25, self.width() * .22, self.height() * .22))
            p.drawRoundedRect(QRectF(self.width() * .28, self.height() * .52, self.width() * .44, self.height() * .22), 7, 7)
        elif self.kind == "bell":
            p.setPen(QPen(QColor("#d9efff"), 2))
            p.setBrush(Qt.BrushStyle.NoBrush)
            w = self.width()
            h = self.height()
            p.drawArc(QRectF(w * .30, h * .24, w * .40, h * .42), 0, 180 * 16)
            p.drawLine(QPointF(w * .30, h * .46), QPointF(w * .25, h * .63))
            p.drawLine(QPointF(w * .70, h * .46), QPointF(w * .75, h * .63))
            p.drawLine(QPointF(w * .25, h * .63), QPointF(w * .75, h * .63))
            p.drawEllipse(QRectF(w * .46, h * .67, w * .08, h * .08))
        elif self.kind == "sun":
            p.setPen(QPen(QColor("#ffc21a"), 2))
            p.setBrush(QColor("#ffc21a"))
            c = QPointF(self.width() / 2, self.height() / 2)
            p.drawEllipse(c, self.width() * .16, self.height() * .16)
            p.setBrush(Qt.BrushStyle.NoBrush)
            for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0), (.7, .7), (-.7, .7), (.7, -.7), (-.7, -.7)):
                a = QPointF(c.x() + dx * self.width() * .27, c.y() + dy * self.height() * .27)
                b = QPointF(c.x() + dx * self.width() * .39, c.y() + dy * self.height() * .39)
                p.drawLine(a, b)


class MonitorArt(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumSize(190, 118)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        w, h = self.width(), self.height()
        x, y = w * .12, h * .12
        sw, sh = w * .66, h * .62
        p.setPen(QPen(QColor("#0c5f91"), 2))
        p.setBrush(QColor("#0b527e"))
        p.drawRoundedRect(QRectF(x, y, sw, sh), 9, 9)
        p.setBrush(QColor("#021c31"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRect(QRectF(x + 12, y + 10, sw - 24, sh - 22))
        p.setBrush(QColor("#0a527c"))
        p.drawRect(QRectF(x + sw * .45, y + sh, sw * .10, h * .10))
        p.drawRoundedRect(QRectF(x - 14, y + sh + h * .08, sw + 28, h * .09), 2, 2)
        p.setPen(QPen(QColor("#073b5d"), 2))
        p.drawLine(QPointF(x + sw * .42, y + sh + h * .12), QPointF(x + sw * .58, y + sh + h * .12))


class HeroCard(QFrame):
    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setPen(QPen(QColor(0, 151, 205, 25), 1))
        center = QPointF(self.width() * .92, self.height() * .52)
        for radius in (45, 75, 105, 135):
            p.drawEllipse(center, radius, radius)


class MetricCard(QFrame):
    def __init__(self, title: str, icon: str, accent: str) -> None:
        super().__init__()
        self.setObjectName("metricCard")
        self.setMinimumHeight(104)
        row = QHBoxLayout(self)
        row.setContentsMargins(18, 14, 14, 14)
        row.setSpacing(14)

        icon_box = QFrame()
        icon_box.setObjectName("metricIcon")
        icon_box.setFixedSize(60, 60)
        icon_box.setStyleSheet(
            f"QFrame#metricIcon{{background:{accent};border:1px solid rgba(255,255,255,45);border-radius:11px;}}"
        )
        icon_lay = QVBoxLayout(icon_box)
        icon_lay.setContentsMargins(0, 0, 0, 0)
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size:24px;font-weight:800;color:white;background:transparent;border:0;")
        icon_lay.addWidget(icon_label)
        row.addWidget(icon_box)

        text = QVBoxLayout()
        text.setSpacing(1)
        text.addStretch()
        title_label = _label(title, "metricTitle")
        self.value = _label("0", "metricValue")
        text.addWidget(title_label)
        text.addWidget(self.value)
        text.addStretch()
        row.addLayout(text, 1)


class QuickActionButton(QPushButton):
    def __init__(self, title: str, subtitle: str, glyph: str, object_name: str) -> None:
        super().__init__(f"{glyph}    {title}\n         {subtitle}")
        self.setObjectName(object_name)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class HomeDashboard(QWidget):
    navigate = Signal(str)

    def __init__(self, controller: MainUiController) -> None:
        super().__init__()
        self.controller = controller
        self.setObjectName("homeDashboard")
        self.setStyleSheet(HOME_STYLESHEET)
        self._sidebar_original: dict[str, object] | None = None

        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        self.scroll = QScrollArea()
        self.scroll.setObjectName("homeScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        body = QWidget()
        body.setObjectName("homeBody")
        self.body_layout = QVBoxLayout(body)
        self.body_layout.setContentsMargins(18, 8, 18, 0)
        self.body_layout.setSpacing(14)
        self.scroll.setWidget(body)
        self.root_layout.addWidget(self.scroll, 1)

        self._build_header()
        self._build_metrics()
        self._build_center()
        self._build_secondary()
        self._build_bottom()
        self._build_footer()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._apply_sidebar_refinement()

    def hideEvent(self, event) -> None:
        self._restore_sidebar_refinement()
        super().hideEvent(event)

    def _apply_sidebar_refinement(self) -> None:
        window = self.window()
        sidebar = getattr(window, "sidebar", None)
        nav_buttons = getattr(window, "nav_buttons", None)
        status_card = getattr(window, "side_status_card", None)
        if sidebar is None or not isinstance(nav_buttons, dict) or status_card is None:
            return
        if self._sidebar_original is None:
            layout = sidebar.layout()
            status_index = layout.indexOf(status_card) if layout is not None else -1
            anchor = sidebar.findChild(QLabel, "anchorMark")
            self._sidebar_original = {
                "style": sidebar.styleSheet(),
                "nav_heights": {key: button.minimumHeight() for key, button in nav_buttons.items()},
                "status_min": status_card.minimumHeight(),
                "status_index": status_index,
                "stretch": layout.stretch(status_index - 1) if layout is not None and status_index > 0 else 0,
                "anchor": anchor,
                "anchor_text": anchor.text() if anchor is not None else "",
                "anchor_style": anchor.styleSheet() if anchor is not None else "",
            }
        sidebar.setStyleSheet(REFINED_SIDEBAR_STYLESHEET)
        for button in nav_buttons.values():
            button.setMinimumHeight(44)
        status_card.setMinimumHeight(164)
        layout = sidebar.layout()
        status_index = layout.indexOf(status_card) if layout is not None else -1
        if layout is not None and status_index > 0:
            layout.setStretch(status_index - 1, 0)
        anchor = sidebar.findChild(QLabel, "anchorMark")
        if anchor is not None:
            anchor.setText("⚓︎")
            anchor.setStyleSheet("color:#f5aa00;font-family:'Segoe UI Symbol';font-size:46px;font-weight:700;background:transparent;")

    def _restore_sidebar_refinement(self) -> None:
        if self._sidebar_original is None:
            return
        window = self.window()
        sidebar = getattr(window, "sidebar", None)
        nav_buttons = getattr(window, "nav_buttons", None)
        status_card = getattr(window, "side_status_card", None)
        if sidebar is None or not isinstance(nav_buttons, dict) or status_card is None:
            return
        original = self._sidebar_original
        sidebar.setStyleSheet(str(original["style"]))
        for key, button in nav_buttons.items():
            heights = original["nav_heights"]
            if isinstance(heights, dict) and key in heights:
                button.setMinimumHeight(int(heights[key]))
        status_card.setMinimumHeight(int(original["status_min"]))
        layout = sidebar.layout()
        status_index = int(original["status_index"])
        if layout is not None and status_index > 0:
            layout.setStretch(status_index - 1, int(original["stretch"]))
        anchor = original.get("anchor")
        if isinstance(anchor, QLabel):
            anchor.setText(str(original["anchor_text"]))
            anchor.setStyleSheet(str(original["anchor_style"]))

    def _build_header(self) -> None:
        header_widget = DashboardHeader()
        header_widget.setMinimumHeight(108)
        header = QHBoxLayout(header_widget)
        header.setContentsMargins(14, 6, 0, 2)
        header.setSpacing(18)

        welcome_wrap = QHBoxLayout()
        welcome_wrap.setSpacing(10)
        welcome_wrap.addWidget(LeafIcon(), 0, Qt.AlignmentFlag.AlignVCenter)
        welcome = QVBoxLayout()
        welcome.setSpacing(3)
        welcome.addWidget(_label("Olá, bem-vindo! 👋", "homeWelcome"))
        welcome.addWidget(_label("Acompanhe notícias, vídeos, demandas e fontes em tempo real.", "homeSubtitle"))
        welcome_wrap.addLayout(welcome, 1)
        header.addLayout(welcome_wrap, 4)

        self.search = QLineEdit()
        self.search.setObjectName("homeSearch")
        self.search.setPlaceholderText("⌕   Buscar notícias, vídeos, demandas ou fontes...")
        self.search.setMinimumWidth(350)
        self.search.setMaximumWidth(430)
        header.addWidget(self.search, 3, Qt.AlignmentFlag.AlignVCenter)

        right = QVBoxLayout()
        right.setSpacing(5)
        slogan_row = QHBoxLayout()
        slogan_row.setSpacing(10)
        gold_line = _label("━━", "homeSlogan")
        gold_line.setStyleSheet("color:#ffc21a;font-size:11px;font-weight:800;")
        slogan_row.addWidget(gold_line)
        slogan_row.addStretch()
        slogan = _label("BRASIL SEMPRE MAIS INFORMADO", "homeSlogan")
        slogan.setAlignment(Qt.AlignmentFlag.AlignRight)
        slogan_row.addWidget(slogan)
        right.addLayout(slogan_row)

        info = QHBoxLayout()
        info.setSpacing(8)
        info.addWidget(RoundIcon("bell", 40))
        info.addWidget(RoundIcon("user", 45))

        divider = QFrame()
        divider.setFixedWidth(1)
        divider.setStyleSheet("background:#0d4569;border:0;")
        info.addWidget(divider)

        clock_box = QVBoxLayout()
        clock_box.setSpacing(0)
        self.date_label = _label("", "homeDate")
        self.clock_label = _label("", "homeClock")
        clock_box.addWidget(self.date_label)
        clock_box.addWidget(self.clock_label)
        info.addLayout(clock_box)

        weather_frame = QFrame()
        weather_frame.setStyleSheet("QFrame{background:#04223c;border:1px solid #0d3d60;border-radius:10px;}")
        wf = QHBoxLayout(weather_frame)
        wf.setContentsMargins(8, 3, 9, 3)
        wf.setSpacing(7)
        wf.addWidget(RoundIcon("sun", 39))
        weather = QVBoxLayout()
        weather.setSpacing(0)
        self.weather_city = _label("Brasília - DF", "homeWeatherCity")
        self.weather_temp = _label("--°C", "homeWeatherTemp")
        weather.addWidget(self.weather_city)
        weather.addWidget(self.weather_temp)
        wf.addLayout(weather)
        info.addWidget(weather_frame)
        right.addLayout(info)
        header.addLayout(right, 3)
        self.body_layout.addWidget(header_widget)

    def _build_metrics(self) -> None:
        row = QHBoxLayout()
        row.setSpacing(13)
        specs = (
            ("news", "Notícias 24h", "▤", "#075b8e"),
            ("videos", "Vídeos", "▶", "#39236f"),
            ("today", "Vídeos hoje", "■", "#075f55"),
            ("demands", "Demandas", "▣", "#604116"),
            ("sources", "Fontes", "▤", "#4e214f"),
        )
        self.metric_cards: dict[str, MetricCard] = {}
        for key, title, icon, accent in specs:
            item = MetricCard(title, icon, accent)
            self.metric_cards[key] = item
            row.addWidget(item, 1)
        self.body_layout.addLayout(row)

    def _build_center(self) -> None:
        row = QHBoxLayout()
        row.setSpacing(15)

        hero = HeroCard()
        hero.setObjectName("dashboardCard")
        hero.setMinimumHeight(282)
        hero_lay = QVBoxLayout(hero)
        hero_lay.setContentsMargins(34, 18, 34, 16)
        hero_lay.setSpacing(7)
        hero_lay.addWidget(_label("━━━   CENTRAL DE INTELIGÊNCIA DE MÍDIA", "kicker"))

        main = QHBoxLayout()
        main.setSpacing(8)
        left = QVBoxLayout()
        left.setSpacing(7)
        title = _label("Tudo o que importa\nem um só lugar.", "heroTitle")
        title.setWordWrap(True)
        left.addWidget(title)
        body = _label("Buscas e resultados atualizados automaticamente,\nem tempo real.", "heroBody")
        body.setWordWrap(True)
        left.addWidget(body)
        left.addStretch()
        main.addLayout(left, 5)

        main.addWidget(MonitorArt(), 3, Qt.AlignmentFlag.AlignCenter)

        rail = _label("VIGILÂNCIA\nMÍDIA\nANÁLISE\nRESULTADOS", "heroRail")
        rail.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        main.addWidget(rail, 2)
        hero_lay.addLayout(main, 1)

        status_row = QHBoxLayout()
        status_row.setSpacing(16)
        panel = QFrame()
        panel.setObjectName("statusPanel")
        panel_lay = QVBoxLayout(panel)
        panel_lay.setContentsMargins(12, 6, 12, 7)
        panel_lay.setSpacing(4)
        top = QHBoxLayout()
        self.status_label = _label("●  Status: Pronto", "statusReady")
        self.status_pct = _label("100%", "statusPct")
        top.addWidget(self.status_label)
        top.addStretch()
        top.addWidget(self.status_pct)
        panel_lay.addLayout(top)
        self.progress = QProgressBar()
        self.progress.setObjectName("homeProgress")
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(False)
        self.progress.setValue(100)
        panel_lay.addWidget(self.progress)
        status_row.addWidget(panel, 4)
        integrated = _label("Monitoramento integrado", "cardSubtitle")
        integrated.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_row.addWidget(integrated, 2)
        hero_lay.addLayout(status_row)
        row.addWidget(hero, 58)

        actions, actions_lay = _frame("dashboardCard", (20, 16, 20, 16), 6)
        actions.setMinimumHeight(282)
        actions_lay.addWidget(_label("⚡   Ações rápidas", "cardTitle"))
        actions_lay.addWidget(_label("Execute as principais rotinas sem sair do painel.", "cardSubtitle"))
        grid = QGridLayout()
        grid.setContentsMargins(0, 7, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
        buttons = (
            ("Buscar notícias", "Varredura manual", "⌕", "quickBlue", self.controller.search_news),
            ("Buscar vídeos", "Fontes selecionadas", "▶", "quickPurple", self.controller.search_videos),
            ("Buscar demandas", "Demandas ativas", "▣", "quickOrange", self.controller.search_all_demands),
            ("Termos de busca", "Gerenciar palavras-chave", "⌕", "quickGreen", lambda: self.navigate.emit("TERMS")),
        )
        self.quick_buttons: list[QPushButton] = []
        for idx, (title_text, subtitle, glyph, name, callback) in enumerate(buttons):
            btn = QuickActionButton(title_text, subtitle, glyph, name)
            btn.clicked.connect(callback)
            self.quick_buttons.append(btn)
            grid.addWidget(btn, idx // 2, idx % 2)
        actions_lay.addLayout(grid, 1)
        row.addWidget(actions, 42)
        self.body_layout.addLayout(row)

    def _schedule_box(self, name: str, value_name: str) -> tuple[QFrame, QLabel]:
        box, lay = _frame("scheduleBox", (12, 8, 12, 8), 2)
        lay.addWidget(_label(name, "scheduleName"))
        value = _label("—", value_name)
        lay.addWidget(value)
        return box, value

    def _build_secondary(self) -> None:
        row = QHBoxLayout()
        row.setSpacing(15)

        schedule, sl = _frame("dashboardCard", (18, 13, 18, 14), 7)
        schedule.setMinimumHeight(172)
        title_row = QHBoxLayout()
        clock_glyph = _label("◷", "scheduleValueBlue")
        clock_glyph.setStyleSheet("color:#1ea7ff;font-size:28px;font-weight:700;")
        title_row.addWidget(clock_glyph)
        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        title_box.addWidget(_label("Agendamento automático", "cardTitle"))
        title_box.addWidget(_label("O sistema executa buscas automaticamente nos horários definidos.", "cardSubtitle"))
        title_row.addLayout(title_box, 1)
        sl.addLayout(title_row)
        schedule_grid = QHBoxLayout()
        schedule_grid.setSpacing(12)
        n_box, self.news_interval = self._schedule_box("Notícias", "scheduleValueBlue")
        d_box, self.demand_interval = self._schedule_box("Demandas", "scheduleValueOrange")
        v_box, self.video_times = self._schedule_box("Vídeos", "scheduleValuePurple")
        schedule_grid.addWidget(n_box, 1)
        schedule_grid.addWidget(d_box, 1)
        schedule_grid.addWidget(v_box, 2)
        sl.addLayout(schedule_grid)
        row.addWidget(schedule, 50)

        summary, rl = _frame("dashboardCard", (20, 13, 20, 14), 7)
        summary.setMinimumHeight(172)
        rl.addWidget(_label("▥   Resumo do dia", "cardTitle"))
        rl.addWidget(_label("Dados atuais disponíveis no aplicativo.", "cardSubtitle"))
        metrics = QHBoxLayout()
        metrics.setSpacing(0)
        self.summary_values: dict[str, QLabel] = {}
        for idx, (key, name, obj) in enumerate((
            ("news", "Notícias", "summaryBlue"),
            ("videos", "Vídeos", "summaryPurple"),
            ("demands", "Demandas", "summaryOrange"),
        )):
            box = QVBoxLayout()
            box.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value = _label("0", obj)
            value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label = _label(name, "summaryName")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            box.addWidget(value)
            box.addWidget(label)
            metrics.addLayout(box, 1)
            self.summary_values[key] = value
            if idx < 2:
                divider = QFrame()
                divider.setFixedWidth(1)
                divider.setStyleSheet("background:#0b557f;border:0;")
                metrics.addWidget(divider)
        rl.addLayout(metrics, 1)
        row.addWidget(summary, 50)
        self.body_layout.addLayout(row)

    def _build_bottom(self) -> None:
        row = QHBoxLayout()
        row.setSpacing(15)
        specs = (
            ("▤", "#49c9ff", "Fontes em destaque", "Principais fontes monitoradas pelo sistema."),
            ("◷", "#a95dff", "Últimas atividades", "Registro das ações mais recentes no sistema."),
            ("●", "#ffc21a", "Dicas e operação", "Orientações para melhor uso do sistema."),
        )
        self.bottom_content: list[QLabel] = []
        for glyph, color, title, subtitle in specs:
            box, lay = _frame("miniCard", (18, 10, 18, 8), 3)
            box.setMinimumHeight(90)
            title_row = QHBoxLayout()
            icon = QLabel(glyph)
            icon.setStyleSheet(f"color:{color};font-size:22px;font-weight:800;")
            title_row.addWidget(icon)
            title_box = QVBoxLayout()
            title_box.setSpacing(0)
            title_box.addWidget(_label(title, "cardTitle"))
            title_box.addWidget(_label(subtitle, "cardSubtitle"))
            title_row.addLayout(title_box, 1)
            lay.addLayout(title_row)
            content = _label("", "smallContent")
            content.setWordWrap(True)
            lay.addWidget(content)
            self.bottom_content.append(content)
            row.addWidget(box, 1)
        self.body_layout.addLayout(row)

    def _build_footer(self) -> None:
        footer_frame = QFrame()
        footer_frame.setFixedHeight(42)
        footer_frame.setStyleSheet("QFrame{background:#031a2e;border-top:1px solid #0a456b;border-radius:0;}")
        footer = QHBoxLayout(footer_frame)
        footer.setContentsMargins(18, 8, 18, 7)
        footer.addWidget(_label("Monitor de Notícias v4.0.2   |   Inteligência de mídia para melhores decisões", "footerText"))
        footer.addStretch()
        self.footer_status = _label("●  Sistema operacional", "footerStatus")
        self.footer_status.setStyleSheet("color:#b9cad9;font-size:9px;")
        footer.addWidget(self.footer_status)
        divider = QFrame()
        divider.setFixedWidth(1)
        divider.setStyleSheet("background:#1d5575;border:0;")
        footer.addWidget(divider)
        gold = _label("━━", "footerText")
        gold.setStyleSheet("color:#ffc21a;font-size:10px;font-weight:800;")
        footer.addWidget(gold)
        footer.addWidget(_label("MAR  •  TERRA  •  AR  •  CIBERESPAÇO", "footerText"))
        self.root_layout.addWidget(footer_frame)

    @staticmethod
    def _progress_from_state(state: UiState) -> tuple[int, str]:
        if state.news_busy:
            progress = state.news_progress
            fraction = max(0.0, min(1.0, float(getattr(progress, "fraction", 0.0))))
            return round(fraction * 100), state.status
        if state.video_busy:
            progress = state.video_progress
            fraction = max(0.0, min(1.0, float(getattr(progress, "fraction", 0.0))))
            return round(fraction * 100), state.video_status
        return 100, "Pronto"

    def refresh(self, state: UiState) -> None:
        now = datetime.now()
        now_ms = int(now.timestamp() * 1000)
        day_ago = now_ms - 86_400_000

        news_count = len(state.news)
        video_count = len(state.videos)
        today_count = sum(1 for video in state.videos if video.capturedAt >= day_ago)
        demand_count = sum(1 for demand in state.demands if demand.active)
        source_count = len(self.controller.news_sources)

        values = {
            "news": news_count,
            "videos": video_count,
            "today": today_count,
            "demands": demand_count,
            "sources": source_count,
        }
        for key, value in values.items():
            self.metric_cards[key].value.setText(str(value))

        self.summary_values["news"].setText(str(news_count))
        self.summary_values["videos"].setText(str(today_count))
        self.summary_values["demands"].setText(str(demand_count))

        self.date_label.setText(now.strftime("%d %b %Y"))
        self.clock_label.setText(now.strftime("%H:%M:%S"))

        auto = self.controller.automation_settings
        self.news_interval.setText(f"{auto.news_interval_minutes} min")
        demand_minutes = auto.demand_interval_minutes
        if demand_minutes == 60:
            demand_text = "1 hora"
        elif demand_minutes % 60 == 0:
            demand_text = f"{demand_minutes // 60} horas"
        else:
            demand_text = f"{demand_minutes} min"
        self.demand_interval.setText(demand_text)
        video_slots = sorted(auto.video_schedule_times)
        self.video_times.setText(", ".join(video_slots) if video_slots else "—")

        pct, status = self._progress_from_state(state)
        self.progress.setValue(pct)
        self.status_pct.setText(f"{pct}%")
        self.status_label.setText(f"●  Status: {status}")

        for button in self.quick_buttons[:3]:
            button.setEnabled(True)

        sources = [getattr(source, "name", "") or getattr(source, "label", "") for source in self.controller.news_sources[:4]]
        sources = [item for item in sources if item]
        self.bottom_content[0].setText(" • ".join(sources) if sources else "Fontes carregadas pelo aplicativo.")

        activity_parts = []
        if state.status:
            activity_parts.append(f"Notícias: {state.status}")
        if state.video_status:
            activity_parts.append(f"Vídeos: {state.video_status}")
        self.bottom_content[1].setText("   •   ".join(activity_parts))

        auto_status = "ativa" if auto.automatic_monitoring else "pausada"
        proxy_status = self.controller.proxy_config.status_label
        self.bottom_content[2].setText(f"Automação {auto_status}.   •   {proxy_status}")

        busy = state.news_busy or state.video_busy
        self.footer_status.setText("●  Busca em andamento" if busy else "●  Sistema operacional")
