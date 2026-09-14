from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt, Signal
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
    background: #021a2f;
    color: #f4f7fb;
    font-family: 'Segoe UI';
}
QScrollArea#homeScroll, QScrollArea#homeScroll > QWidget > QWidget {
    background: transparent;
    border: none;
}
QLabel { color: #f4f7fb; }
QLabel#homeWelcome { font-size: 27px; font-weight: 800; }
QLabel#homeSubtitle { color: #b6cce2; font-size: 12px; }
QLabel#homeSlogan { color: #c9dcef; font-size: 10px; font-weight: 700; letter-spacing: 1px; }
QLabel#homeDate { color: #9ab6d0; font-size: 10px; }
QLabel#homeClock { color: #f4f7fb; font-size: 19px; font-weight: 800; }
QLabel#homeWeatherCity { color: #f4f7fb; font-size: 11px; font-weight: 700; }
QLabel#homeWeatherTemp { color: #ffc21a; font-size: 18px; font-weight: 800; }
QLineEdit#homeSearch {
    background: #021527;
    color: #eef8ff;
    border: 1px solid #00a9e8;
    border-radius: 12px;
    padding: 10px 14px;
    min-height: 22px;
    selection-background-color: #087af7;
}
QLineEdit#homeSearch:focus { border: 1px solid #00b7ff; }
QFrame#metricCard, QFrame#dashboardCard, QFrame#miniCard {
    background: #06345a;
    border: 1px solid #0b7ba8;
    border-radius: 12px;
}
QFrame#metricIcon {
    border: 1px solid rgba(255,255,255,42);
    border-radius: 10px;
}
QLabel#metricTitle { color: #b6cce2; font-size: 10px; font-weight: 600; }
QLabel#metricValue { color: #ffffff; font-size: 28px; font-weight: 800; }
QLabel#cardTitle { color: #ffffff; font-size: 15px; font-weight: 800; }
QLabel#cardSubtitle { color: #a9c4dc; font-size: 10px; }
QLabel#kicker { color: #7bd3ff; font-size: 10px; font-weight: 800; letter-spacing: 1px; }
QLabel#heroTitle { color: #ffffff; font-size: 29px; font-weight: 800; }
QLabel#heroBody { color: #bad0e4; font-size: 11px; }
QLabel#heroRail { color: #36c8ff; font-size: 11px; font-weight: 800; letter-spacing: 2px; }
QLabel#statusReady { color: #25e68f; font-size: 11px; font-weight: 700; }
QLabel#statusPct { color: #d8ecff; font-size: 10px; font-weight: 700; }
QProgressBar#homeProgress {
    background: #0b2c43;
    border: 0;
    border-radius: 3px;
    min-height: 6px;
    max-height: 6px;
    text-align: center;
}
QProgressBar#homeProgress::chunk { background: #25e68f; border-radius: 3px; }
QPushButton#quickBlue, QPushButton#quickPurple, QPushButton#quickOrange, QPushButton#quickGreen {
    color: white;
    border: 1px solid rgba(255,255,255,36);
    border-radius: 10px;
    padding: 12px 14px;
    text-align: left;
    font-size: 12px;
    font-weight: 800;
    min-height: 54px;
}
QPushButton#quickBlue { background: #087af7; }
QPushButton#quickBlue:hover { background: #1490ff; }
QPushButton#quickPurple { background: #743af3; }
QPushButton#quickPurple:hover { background: #8652ff; }
QPushButton#quickOrange { background: #ff820a; }
QPushButton#quickOrange:hover { background: #ff951f; }
QPushButton#quickGreen { background: #08a86f; }
QPushButton#quickGreen:hover { background: #11bf80; }
QFrame#scheduleBox {
    background: #052a49;
    border: 1px solid #0b628a;
    border-radius: 9px;
}
QLabel#scheduleName { color: #b9d0e5; font-size: 10px; }
QLabel#scheduleValueBlue { color: #36b7ff; font-size: 16px; font-weight: 800; }
QLabel#scheduleValueOrange { color: #ffc21a; font-size: 16px; font-weight: 800; }
QLabel#scheduleValuePurple { color: #b07cff; font-size: 13px; font-weight: 800; }
QLabel#summaryName { color: #a9c4dc; font-size: 10px; }
QLabel#summaryBlue { color: #36b7ff; font-size: 22px; font-weight: 800; }
QLabel#summaryPurple { color: #a95dff; font-size: 22px; font-weight: 800; }
QLabel#summaryOrange { color: #ffa20b; font-size: 22px; font-weight: 800; }
QLabel#smallContent { color: #b6cce2; font-size: 10px; }
QLabel#footerText { color: #8eabc5; font-size: 9px; }
QLabel#footerStatus { color: #25e68f; font-size: 9px; font-weight: 700; }
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


class MetricCard(QFrame):
    def __init__(self, title: str, icon: str, accent: str) -> None:
        super().__init__()
        self.setObjectName("metricCard")
        self.setMinimumHeight(82)
        row = QHBoxLayout(self)
        row.setContentsMargins(12, 10, 12, 10)
        row.setSpacing(10)

        icon_box = QFrame()
        icon_box.setObjectName("metricIcon")
        icon_box.setFixedSize(46, 46)
        icon_box.setStyleSheet(f"QFrame#metricIcon{{background:{accent};border:1px solid {accent};border-radius:10px;}}")
        icon_lay = QVBoxLayout(icon_box)
        icon_lay.setContentsMargins(0, 0, 0, 0)
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size:20px;font-weight:800;color:white;background:transparent;border:0;")
        icon_lay.addWidget(icon_label)
        row.addWidget(icon_box)

        text = QVBoxLayout()
        text.setSpacing(1)
        title_label = _label(title, "metricTitle")
        self.value = _label("0", "metricValue")
        text.addWidget(title_label)
        text.addWidget(self.value)
        row.addLayout(text, 1)


class QuickActionButton(QPushButton):
    def __init__(self, title: str, subtitle: str, glyph: str, object_name: str) -> None:
        super().__init__(f"{glyph}   {title}\n      {subtitle}")
        self.setObjectName(object_name)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class HomeDashboard(QWidget):
    navigate = Signal(str)

    def __init__(self, controller: MainUiController) -> None:
        super().__init__()
        self.controller = controller
        self.setObjectName("homeDashboard")
        self.setStyleSheet(HOME_STYLESHEET)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setObjectName("homeScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        body = QWidget()
        body.setObjectName("homeDashboard")
        self.body_layout = QVBoxLayout(body)
        self.body_layout.setContentsMargins(6, 4, 6, 4)
        self.body_layout.setSpacing(12)
        scroll.setWidget(body)
        root.addWidget(scroll, 1)

        self._build_header()
        self._build_metrics()
        self._build_center()
        self._build_secondary()
        self._build_bottom()
        self._build_footer()

    def _build_header(self) -> None:
        header = QHBoxLayout()
        header.setSpacing(18)

        welcome = QVBoxLayout()
        welcome.setSpacing(3)
        welcome.addWidget(_label("Olá, bem-vindo! 👋", "homeWelcome"))
        welcome.addWidget(_label("Acompanhe notícias, vídeos, demandas e fontes em tempo real.", "homeSubtitle"))
        header.addLayout(welcome, 3)

        self.search = QLineEdit()
        self.search.setObjectName("homeSearch")
        self.search.setPlaceholderText("Buscar notícias, vídeos, demandas ou fontes...")
        self.search.setMinimumWidth(300)
        header.addWidget(self.search, 2)

        right = QVBoxLayout()
        right.setSpacing(4)
        slogan = _label("━━  BRASIL SEMPRE MAIS INFORMADO", "homeSlogan")
        slogan.setAlignment(Qt.AlignmentFlag.AlignRight)
        right.addWidget(slogan)

        info = QHBoxLayout()
        info.setSpacing(12)
        bell = QLabel("◉")
        bell.setStyleSheet("color:#ffc21a;font-size:17px;font-weight:800;")
        info.addWidget(bell)
        avatar = QLabel("●")
        avatar.setStyleSheet("color:#1ea7ff;font-size:21px;")
        info.addWidget(avatar)

        clock_box = QVBoxLayout()
        clock_box.setSpacing(0)
        self.date_label = _label("", "homeDate")
        self.clock_label = _label("", "homeClock")
        clock_box.addWidget(self.date_label)
        clock_box.addWidget(self.clock_label)
        info.addLayout(clock_box)

        weather = QVBoxLayout()
        weather.setSpacing(0)
        self.weather_city = _label("Brasília - DF", "homeWeatherCity")
        self.weather_temp = _label("☀  --°", "homeWeatherTemp")
        weather.addWidget(self.weather_city)
        weather.addWidget(self.weather_temp)
        info.addLayout(weather)
        right.addLayout(info)
        header.addLayout(right, 2)
        self.body_layout.addLayout(header)

    def _build_metrics(self) -> None:
        row = QHBoxLayout()
        row.setSpacing(10)
        specs = (
            ("news", "Notícias 24h", "▤", "#087af7"),
            ("videos", "Vídeos", "▶", "#743af3"),
            ("today", "Vídeos hoje", "●", "#08a86f"),
            ("demands", "Demandas", "☑", "#ff820a"),
            ("sources", "Fontes", "▣", "#f047a8"),
        )
        self.metric_cards: dict[str, MetricCard] = {}
        for key, title, icon, accent in specs:
            item = MetricCard(title, icon, accent)
            self.metric_cards[key] = item
            row.addWidget(item, 1)
        self.body_layout.addLayout(row)

    def _build_center(self) -> None:
        row = QHBoxLayout()
        row.setSpacing(12)

        hero, hero_lay = _frame("dashboardCard", (18, 14, 18, 14), 8)
        hero.setMinimumHeight(270)
        hero_lay.addWidget(_label("━━  CENTRAL DE INTELIGÊNCIA DE MÍDIA", "kicker"))

        main = QHBoxLayout()
        left = QVBoxLayout()
        left.setSpacing(6)
        title = _label("Tudo o que importa\nem um só lugar.", "heroTitle")
        title.setWordWrap(True)
        left.addWidget(title)
        body = _label("Buscas e resultados atualizados automaticamente,\nem tempo real.", "heroBody")
        body.setWordWrap(True)
        left.addWidget(body)
        left.addStretch()
        main.addLayout(left, 4)

        monitor = QLabel("▱\n▰")
        monitor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        monitor.setStyleSheet("color:#1ea7ff;font-size:43px;font-weight:800;line-height:0.8;")
        main.addWidget(monitor, 2)

        rail = _label("VIGILÂNCIA\nMÍDIA\nANÁLISE\nRESULTADOS", "heroRail")
        rail.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        main.addWidget(rail, 2)
        hero_lay.addLayout(main, 1)

        status_row = QHBoxLayout()
        status_box = QVBoxLayout()
        top = QHBoxLayout()
        self.status_label = _label("●  Status: Pronto", "statusReady")
        self.status_pct = _label("100%", "statusPct")
        top.addWidget(self.status_label)
        top.addStretch()
        top.addWidget(self.status_pct)
        status_box.addLayout(top)
        self.progress = QProgressBar()
        self.progress.setObjectName("homeProgress")
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(False)
        self.progress.setValue(100)
        status_box.addWidget(self.progress)
        status_row.addLayout(status_box, 4)
        integrated = _label("Monitoramento integrado", "cardSubtitle")
        integrated.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_row.addWidget(integrated, 2)
        hero_lay.addLayout(status_row)
        row.addWidget(hero, 58)

        actions, actions_lay = _frame("dashboardCard", (16, 14, 16, 14), 8)
        actions.setMinimumHeight(270)
        actions_lay.addWidget(_label("⚡  Ações rápidas", "cardTitle"))
        actions_lay.addWidget(_label("Execute as principais rotinas sem sair do painel.", "cardSubtitle"))
        grid = QGridLayout()
        grid.setHorizontalSpacing(9)
        grid.setVerticalSpacing(9)
        buttons = (
            ("Buscar notícias", "Varredura manual", "▤", "quickBlue", self.controller.search_news),
            ("Buscar vídeos", "Fontes selecionadas", "▶", "quickPurple", self.controller.search_videos),
            ("Buscar demandas", "Demandas ativas", "☑", "quickOrange", self.controller.search_all_demands),
            ("Termos de busca", "Gerenciar palavras-chave", "⌕", "quickGreen", lambda: self.navigate.emit("TERMS")),
        )
        self.quick_buttons: list[QPushButton] = []
        for idx, (title, subtitle, glyph, name, callback) in enumerate(buttons):
            btn = QuickActionButton(title, subtitle, glyph, name)
            btn.clicked.connect(callback)
            self.quick_buttons.append(btn)
            grid.addWidget(btn, idx // 2, idx % 2)
        actions_lay.addLayout(grid, 1)
        row.addWidget(actions, 42)
        self.body_layout.addLayout(row)

    def _schedule_box(self, name: str, value_name: str) -> tuple[QFrame, QLabel]:
        box, lay = _frame("scheduleBox", (10, 8, 10, 8), 2)
        lay.addWidget(_label(name, "scheduleName"))
        value = _label("—", value_name)
        lay.addWidget(value)
        return box, value

    def _build_secondary(self) -> None:
        row = QHBoxLayout()
        row.setSpacing(12)

        schedule, sl = _frame("dashboardCard", (16, 13, 16, 13), 7)
        title_row = QHBoxLayout()
        title_row.addWidget(_label("◷", "scheduleValueBlue"))
        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        title_box.addWidget(_label("Agendamento automático", "cardTitle"))
        title_box.addWidget(_label("O sistema executa buscas automaticamente nos horários definidos.", "cardSubtitle"))
        title_row.addLayout(title_box, 1)
        sl.addLayout(title_row)
        schedule_grid = QHBoxLayout()
        schedule_grid.setSpacing(8)
        n_box, self.news_interval = self._schedule_box("Notícias", "scheduleValueBlue")
        d_box, self.demand_interval = self._schedule_box("Demandas", "scheduleValueOrange")
        v_box, self.video_times = self._schedule_box("Vídeos", "scheduleValuePurple")
        schedule_grid.addWidget(n_box, 1)
        schedule_grid.addWidget(d_box, 1)
        schedule_grid.addWidget(v_box, 2)
        sl.addLayout(schedule_grid)
        row.addWidget(schedule, 58)

        summary, rl = _frame("dashboardCard", (16, 13, 16, 13), 7)
        rl.addWidget(_label("▥  Resumo do dia", "cardTitle"))
        rl.addWidget(_label("Dados atuais disponíveis no aplicativo.", "cardSubtitle"))
        metrics = QHBoxLayout()
        self.summary_values: dict[str, QLabel] = {}
        for key, name, obj in (
            ("news", "Notícias", "summaryBlue"),
            ("videos", "Vídeos", "summaryPurple"),
            ("demands", "Demandas", "summaryOrange"),
        ):
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
        rl.addLayout(metrics, 1)
        row.addWidget(summary, 42)
        self.body_layout.addLayout(row)

    def _build_bottom(self) -> None:
        row = QHBoxLayout()
        row.setSpacing(12)
        specs = (
            ("Fontes em destaque", "Principais fontes monitoradas pelo sistema."),
            ("Últimas atividades", "Registro das ações mais recentes no sistema."),
            ("Dicas e operação", "Orientações para melhor uso do sistema."),
        )
        self.bottom_content: list[QLabel] = []
        for title, subtitle in specs:
            box, lay = _frame("miniCard", (14, 11, 14, 11), 5)
            lay.addWidget(_label(title, "cardTitle"))
            lay.addWidget(_label(subtitle, "cardSubtitle"))
            content = _label("", "smallContent")
            content.setWordWrap(True)
            lay.addWidget(content)
            lay.addStretch()
            self.bottom_content.append(content)
            row.addWidget(box, 1)
        self.body_layout.addLayout(row)

    def _build_footer(self) -> None:
        footer = QHBoxLayout()
        footer.addWidget(_label("Monitor de Notícias v4.0.2 | Inteligência de mídia para melhores decisões", "footerText"))
        footer.addStretch()
        self.footer_status = _label("●  Sistema operacional", "footerStatus")
        footer.addWidget(self.footer_status)
        footer.addWidget(_label("│  ━━  MAR • TERRA • AR • CIBERESPAÇO", "footerText"))
        self.body_layout.addLayout(footer)

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

        self.date_label.setText(now.strftime("%d/%m/%Y"))
        self.clock_label.setText(now.strftime("%H:%M:%S"))

        auto = self.controller.automation_settings
        self.news_interval.setText(f"{auto.news_interval_minutes} min")
        demand_minutes = auto.demand_interval_minutes
        self.demand_interval.setText(f"{demand_minutes // 60} hora" if demand_minutes == 60 else f"{demand_minutes} min")
        video_slots = sorted(auto.video_schedule_times)
        self.video_times.setText("  •  ".join(video_slots) if video_slots else "—")

        pct, status = self._progress_from_state(state)
        self.progress.setValue(pct)
        self.status_pct.setText(f"{pct}%")
        self.status_label.setText(f"●  Status: {status}")

        search_enabled = self.controller.search_available
        for button in self.quick_buttons[:3]:
            button.setEnabled(search_enabled)

        sources = [getattr(source, "name", "") or getattr(source, "label", "") for source in self.controller.news_sources[:4]]
        sources = [item for item in sources if item]
        self.bottom_content[0].setText(" • ".join(sources) if sources else "Fontes carregadas pelo aplicativo.")

        activity_parts = []
        if state.status:
            activity_parts.append(f"Notícias: {state.status}")
        if state.video_status:
            activity_parts.append(f"Vídeos: {state.video_status}")
        self.bottom_content[1].setText("\n".join(activity_parts))

        auto_status = "ativa" if auto.automatic_monitoring else "pausada"
        proxy_status = self.controller.proxy_config.status_label
        self.bottom_content[2].setText(f"Automação {auto_status}.\n{proxy_status}")

        busy = state.news_busy or state.video_busy
        self.footer_status.setText("●  Busca em andamento" if busy else "●  Sistema operacional")
