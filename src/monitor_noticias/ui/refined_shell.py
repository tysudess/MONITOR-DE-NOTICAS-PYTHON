from __future__ import annotations

from datetime import datetime
from os import environ
from time import monotonic

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from monitor_noticias.ui.home_runtime_features import WEATHER_REFRESH_SECONDS, WeatherThread


SECTION_ACCENTS = {
    "Início": ("⌂", "#49c9ff"),
    "Notícias": ("▤", "#49c9ff"),
    "Vídeos": ("▶", "#b45cff"),
    "Demandas": ("▣", "#37c8ff"),
    "Fontes": ("▤", "#49c9ff"),
    "Histórico": ("↺", "#49c9ff"),
    "Termos": ("⌕", "#49c9ff"),
    "Parar buscas": ("■", "#ff5d68"),
    "Configurações": ("⚙", "#ffffff"),
    "Editor de PDF": ("▣", "#49c9ff"),
    "Extrator de Vídeos": ("⇩", "#ffc21a"),
    "Editor de Vídeo": ("▰", "#b45cff"),
}


class RadarHeader(QFrame):
    """Cabeçalho visual compartilhado; recebe somente dados reais do controller."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("pageHeader")
        self.setMinimumHeight(108)
        self._weather_thread: WeatherThread | None = None
        self._weather_last_started = 0.0
        self._weather_value: float | None = None

        root = QHBoxLayout(self)
        root.setContentsMargins(14, 8, 2, 7)
        root.setSpacing(14)

        self.icon = QLabel("▤")
        self.icon.setObjectName("pageIcon")
        self.icon.setFixedWidth(58)
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.icon)

        text = QVBoxLayout()
        text.setSpacing(2)
        kicker_row = QHBoxLayout()
        gold = QLabel("━━")
        gold.setStyleSheet("color:#ffc21a;font-size:13px;font-weight:900;")
        kicker_row.addWidget(gold)
        self.kicker = QLabel("CENTRAL DE INTELIGÊNCIA DE MÍDIA")
        self.kicker.setObjectName("pageKicker")
        kicker_row.addWidget(self.kicker)
        kicker_row.addStretch()
        text.addLayout(kicker_row)
        self.title = QLabel()
        self.title.setObjectName("pageTitle")
        text.addWidget(self.title)
        self.subtitle = QLabel()
        self.subtitle.setObjectName("pageSubtitle")
        text.addWidget(self.subtitle)
        root.addLayout(text, 5)

        root.addStretch(1)

        self.proxy_pill, self.proxy_label = self._pill("pillGold", "⬡", "Proxy", "#ffc21a")
        root.addWidget(self.proxy_pill, 0, Qt.AlignmentFlag.AlignVCenter)
        self.auto_pill, self.auto_label = self._pill("pillGreen", "◷", "Automação", "#18e398")
        root.addWidget(self.auto_pill, 0, Qt.AlignmentFlag.AlignVCenter)

        divider = QFrame()
        divider.setFixedWidth(1)
        divider.setMinimumHeight(64)
        divider.setStyleSheet("background:#0a5c83;border:0;")
        root.addWidget(divider, 0, Qt.AlignmentFlag.AlignVCenter)

        clock_box = QVBoxLayout()
        clock_box.setSpacing(0)
        self.date_label = QLabel()
        self.date_label.setObjectName("smallText")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet("color:#ffffff;font-size:18px;font-weight:800;")
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        clock_box.addWidget(self.date_label)
        clock_box.addWidget(self.clock_label)
        root.addLayout(clock_box)

        weather = QFrame()
        weather.setObjectName("pillBlue")
        wl = QHBoxLayout(weather)
        wl.setContentsMargins(8, 5, 10, 5)
        wl.setSpacing(7)
        sun = QLabel("☀")
        sun.setStyleSheet("color:#ffc21a;font-size:30px;font-weight:800;")
        wl.addWidget(sun)
        wt = QVBoxLayout()
        wt.setSpacing(0)
        city = QLabel("Brasília - DF")
        city.setObjectName("smallText")
        self.weather_temp = QLabel("--°C")
        self.weather_temp.setStyleSheet("color:#ffffff;font-size:15px;font-weight:800;")
        wt.addWidget(city)
        wt.addWidget(self.weather_temp)
        wl.addLayout(wt)
        root.addWidget(weather, 0, Qt.AlignmentFlag.AlignVCenter)

    @staticmethod
    def _pill(name: str, glyph: str, text: str, color: str):
        frame = QFrame()
        frame.setObjectName(name)
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(10, 7, 10, 7)
        lay.setSpacing(6)
        icon = QLabel(glyph)
        icon.setStyleSheet(f"color:{color};font-size:16px;font-weight:800;")
        label = QLabel(text)
        label.setStyleSheet("color:#ffffff;font-weight:800;")
        lay.addWidget(icon)
        lay.addWidget(label)
        return frame, label

    def set_section(self, title: str, subtitle: str) -> None:
        self.title.setText(title)
        self.subtitle.setText(subtitle)
        glyph, color = SECTION_ACCENTS.get(title, ("▤", "#49c9ff"))
        self.icon.setText(glyph)
        self.icon.setStyleSheet(f"color:{color};font-size:37px;font-weight:800;background:transparent;")

    def update_runtime(self, controller) -> None:
        now = datetime.now()
        self.date_label.setText(now.strftime("%d/%m/%Y"))
        self.clock_label.setText(now.strftime("%H:%M:%S"))
        cfg = controller.proxy_config
        auto = controller.automation_settings
        self.proxy_label.setText(cfg.status_label)
        self.auto_label.setText(f"Automação {'ativa' if auto.automatic_monitoring else 'pausada'}")
        self._maybe_weather()

    def _maybe_weather(self) -> None:
        if self._weather_value is not None:
            self.weather_temp.setText(f"{round(self._weather_value)}°C")
        if environ.get("QT_QPA_PLATFORM", "").strip().lower() == "offscreen":
            return
        if environ.get("MONITOR_DISABLE_WEATHER", "").strip().lower() in {"1", "true", "yes"}:
            return
        if self._weather_thread is not None and self._weather_thread.isRunning():
            return
        now = monotonic()
        if self._weather_last_started and now - self._weather_last_started < WEATHER_REFRESH_SECONDS:
            return
        self._weather_last_started = now
        worker = WeatherThread(self)
        self._weather_thread = worker
        worker.succeeded.connect(self._weather_ok)
        worker.failed.connect(lambda detail: self.weather_temp.setToolTip(f"Temperatura indisponível: {detail}"))
        worker.finished.connect(lambda: setattr(self, "_weather_thread", None))
        worker.start()

    def _weather_ok(self, value: float) -> None:
        self._weather_value = float(value)
        self.weather_temp.setText(f"{round(value)}°C")
        self.weather_temp.setToolTip("Temperatura atual de Brasília - DF")

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        center = QPointF(self.width() * .40, self.height() * .50)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor(0, 153, 216, 52), 1))
        for radius in (26, 47, 68, 89, 110, 131):
            p.drawEllipse(center, radius, radius)
        p.drawLine(QPointF(center.x()-150, center.y()), QPointF(center.x()+150, center.y()))
        p.drawLine(QPointF(center.x(), 0), QPointF(center.x(), self.height()))
        p.setPen(QPen(QColor(0, 207, 255, 170), 2))
        p.drawEllipse(center, 3, 3)
        p.setPen(QPen(QColor(0, 120, 180, 48), 1))
        p.drawLine(QPointF(0, 10), QPointF(self.width()*.72, 10))


class TechFooter(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("footerFrame")
        self.setFixedHeight(44)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 6, 0, 5)
        row.setSpacing(12)
        self.left = QLabel("Monitor de Notícias v4.0.2   |   Inteligência de mídia para melhores decisões")
        self.left.setObjectName("smallText")
        row.addWidget(self.left)
        row.addStretch()
        self.status = QLabel("●  Sistema operacional")
        self.status.setStyleSheet("color:#d2e5f4;font-size:9px;")
        row.addWidget(self.status)
        sep = QFrame(); sep.setFixedWidth(1); sep.setStyleSheet("background:#1b5e82;border:0;")
        row.addWidget(sep)
        gold = QLabel("━━")
        gold.setStyleSheet("color:#ffc21a;font-size:10px;font-weight:800;")
        row.addWidget(gold)
        text = QLabel("MAR  •  TERRA  •  AR  •  CIBERESPAÇO")
        text.setStyleSheet("color:#58c9f4;font-size:9px;font-weight:700;letter-spacing:1px;")
        row.addWidget(text)

    def set_busy(self, busy: bool) -> None:
        self.status.setText("●  Busca em andamento" if busy else "●  Sistema operacional")
        self.status.setStyleSheet(
            "color:#ffc21a;font-size:9px;" if busy else "color:#d2e5f4;font-size:9px;"
        )
