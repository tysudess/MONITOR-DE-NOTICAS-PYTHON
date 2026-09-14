from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from monitor_noticias.ui.controller import MainUiController, UiState


HOME_QSS = """
QWidget#homeDashboard {
    background: #021a2f;
    color: #f4f7fb;
    font-family: 'Segoe UI';
}
QScrollArea#homeScroll { border: 0; background: transparent; }
QScrollArea#homeScroll > QWidget > QWidget { background: transparent; }
QFrame#homeCard, QFrame#metricCard, QFrame#heroCard, QFrame#quickCard,
QFrame#scheduleCard, QFrame#summaryCard, QFrame#bottomCard {
    background: #052b4a;
    border: 1px solid #087fb6;
    border-radius: 12px;
}
QFrame#metricCard { min-height: 82px; }
QLabel#homeWelcome { color: #f4f7fb; font-size: 26px; font-weight: 800; }
QLabel#homeSubtitle { color: #b6cce2; font-size: 12px; }
QLabel#metricTitle { color: #d7e7f5; font-size: 12px; }
QLabel#metricValue { color: white; font-size: 27px; font-weight: 800; }
QLabel#eyebrow { color: #66cfff; font-size: 11px; font-weight: 600; letter-spacing: 1px; }
QLabel#heroTitle { color: white; font-size: 31px; font-weight: 800; }
QLabel#heroText { color: #c3d7e9; font-size: 12px; }
QLabel#verticalAccent { color: #1eb8ff; font-size: 12px; font-weight: 700; line-height: 1.5; }
QLabel#cardTitle { color: #f4f7fb; font-size: 16px; font-weight: 750; }
QLabel#cardSubtitle { color: #b6cce2; font-size: 11px; }
QLabel#scheduleTitle { color: #f4f7fb; font-size: 12px; font-weight: 700; }
QLabel#scheduleBlue { color: #20a8ff; font-size: 12px; font-weight: 700; }
QLabel#scheduleOrange { color: #ff9d0b; font-size: 12px; font-weight: 700; }
QLabel#schedulePurple { color: #bb6cff; font-size: 12px; font-weight: 700; }
QLabel#summaryBlue { color: #169eff; font-size: 28px; font-weight: 800; }
QLabel#summaryPurple { color: #a85cff; font-size: 28px; font-weight: 800; }
QLabel#summaryOrange { color: #ff9700; font-size: 28px; font-weight: 800; }
QLabel#summaryLabel { color: #b6cce2; font-size: 11px; }
QLabel#statusReady { color: #25e68f; font-size: 12px; font-weight: 700; }
QProgressBar#homeProgress {
    border: 0;
    background: #0b3654;
    border-radius: 4px;
    min-height: 7px;
    max-height: 7px;
    text-align: center;
}
QProgressBar#homeProgress::chunk { background: #25e68f; border-radius: 4px; }
QPushButton#quickNews, QPushButton#quickVideo, QPushButton#quickDemand, QPushButton#quickTerms {
    color: white;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.22);
    padding: 12px 14px;
    font-size: 13px;
    font-weight: 700;
    text-align: left;
    min-height: 58px;
}
QPushButton#quickNews { background: #087af7; }
QPushButton#quickVideo { background: #743af3; }
QPushButton#quickDemand { background: #d87900; }
QPushButton#quickTerms { background: #07895d; }
QPushButton#quickNews:hover { background: #1593ff; }
QPushButton#quickVideo:hover { background: #8e55ff; }
QPushButton#quickDemand:hover { background: #f28a00; }
QPushButton#quickTerms:hover { background: #0aa66f; }
QFrame#scheduleTile { background: #063457; border: 1px solid #0b75a9; border-radius: 9px; }
QFrame#statusPanel { background: #06384a; border: 1px solid #08a86f; border-radius: 9px; }
QFrame#metricIconBlue { background: #0a568a; border: 1px solid #087ac0; border-radius: 10px; }
QFrame#metricIconPurple { background: #38216d; border: 1px solid #6741b9; border-radius: 10px; }
QFrame#metricIconGreen { background: #075a50; border: 1px solid #0a8575; border-radius: 10px; }
QFrame#metricIconOrange { background: #5f4319; border: 1px solid #a66d18; border-radius: 10px; }
QFrame#metricIconPink { background: #5a2453; border: 1px solid #8d3b83; border-radius: 10px; }
QLabel#metricIconText { color: white; font-size: 21px; font-weight: 800; }
"""


class HomePage(QWidget):
    navigate = Signal(str)

    def __init__(self, controller: MainUiController) -> None:
        super().__init__()
        self.controller = controller
        self.setObjectName("homeDashboard")
        self.setStyleSheet(HOME_QSS)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setObjectName("homeScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        body = QWidget()
        body.setObjectName("homeDashboard")
        scroll.setWidget(body)
        self.root = QVBoxLayout(body)
        self.root.setContentsMargins(6, 6, 6, 10)
        self.root.setSpacing(14)

        self._build_header()
        self._build_metrics()
        self._build_center()
        self._build_secondary()
        self._build_bottom()
        self.root.addStretch(1)

    def _build_header(self) -> None:
        row = QHBoxLayout()
        row.setSpacing(14)

        icon = QFrame(); icon.setFixedSize(52, 52); icon.setStyleSheet("background:#064b55;border:1px solid #07926f;border-radius:26px;")
        il = QVBoxLayout(icon); il.setContentsMargins(0,0,0,0)
        leaf = QLabel("◒"); leaf.setAlignment(Qt.AlignmentFlag.AlignCenter); leaf.setStyleSheet("color:#25e68f;font-size:30px;font-weight:800;")
        il.addWidget(leaf)
        row.addWidget(icon, 0, Qt.AlignmentFlag.AlignVCenter)

        text = QVBoxLayout(); text.setSpacing(2)
        welcome = QLabel("Olá, bem-vindo! 👋"); welcome.setObjectName("homeWelcome")
        sub = QLabel("Acompanhe notícias, vídeos, demandas e fontes em tempo real."); sub.setObjectName("homeSubtitle")
        text.addWidget(welcome); text.addWidget(sub)
        row.addLayout(text)
        row.addStretch(1)

        self.header_status = QLabel("●  SISTEMA OPERACIONAL")
        self.header_status.setStyleSheet("color:#58dcaa;font-size:10px;font-weight:700;")
        row.addWidget(self.header_status, 0, Qt.AlignmentFlag.AlignTop)
        self.root.addLayout(row)

    def _metric_card(self, title: str, icon_text: str, icon_object: str) -> tuple[QFrame, QLabel]:
        frame = QFrame(); frame.setObjectName("metricCard")
        layout = QHBoxLayout(frame); layout.setContentsMargins(14, 12, 14, 12); layout.setSpacing(13)
        icon = QFrame(); icon.setObjectName(icon_object); icon.setFixedSize(50, 50)
        il = QVBoxLayout(icon); il.setContentsMargins(0,0,0,0)
        glyph = QLabel(icon_text); glyph.setObjectName("metricIconText"); glyph.setAlignment(Qt.AlignmentFlag.AlignCenter); il.addWidget(glyph)
        layout.addWidget(icon)
        labels = QVBoxLayout(); labels.setSpacing(1)
        t = QLabel(title); t.setObjectName("metricTitle")
        v = QLabel("0"); v.setObjectName("metricValue")
        labels.addWidget(t); labels.addWidget(v); layout.addLayout(labels); layout.addStretch(1)
        return frame, v

    def _build_metrics(self) -> None:
        row = QHBoxLayout(); row.setSpacing(12)
        self.metric_labels: dict[str, QLabel] = {}
        specs = (
            ("news", "Notícias 24h", "▤", "metricIconBlue"),
            ("videos", "Vídeos", "▶", "metricIconPurple"),
            ("today", "Vídeos hoje", "■", "metricIconGreen"),
            ("demands", "Demandas", "▣", "metricIconOrange"),
            ("sources", "Fontes", "☷", "metricIconPink"),
        )
        for key, title, glyph, obj in specs:
            frame, value = self._metric_card(title, glyph, obj)
            row.addWidget(frame, 1)
            self.metric_labels[key] = value
        self.root.addLayout(row)

    def _build_center(self) -> None:
        row = QHBoxLayout(); row.setSpacing(14)

        hero = QFrame(); hero.setObjectName("heroCard"); hero.setMinimumHeight(255)
        hl = QVBoxLayout(hero); hl.setContentsMargins(26, 20, 24, 16); hl.setSpacing(8)
        eye = QLabel("━   CENTRAL DE INTELIGÊNCIA DE MÍDIA"); eye.setObjectName("eyebrow"); hl.addWidget(eye)
        main = QHBoxLayout(); main.setSpacing(24)
        copy = QVBoxLayout(); copy.setSpacing(6)
        title = QLabel("Tudo o que importa\nem um só lugar."); title.setObjectName("heroTitle")
        text = QLabel("Buscas e resultados atualizados automaticamente,\nem tempo real."); text.setObjectName("heroText")
        copy.addWidget(title); copy.addWidget(text); copy.addStretch(1)
        main.addLayout(copy, 5)
        monitor = QLabel("▰"); monitor.setAlignment(Qt.AlignmentFlag.AlignCenter); monitor.setStyleSheet("color:#116b9f;font-size:100px;font-weight:300;")
        main.addWidget(monitor, 3)
        accent = QLabel("VIGILÂNCIA\nMÍDIA\nANÁLISE\nRESULTADOS"); accent.setObjectName("verticalAccent"); accent.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        main.addWidget(accent, 2)
        hl.addLayout(main, 1)

        status = QFrame(); status.setObjectName("statusPanel")
        sl = QVBoxLayout(status); sl.setContentsMargins(12, 8, 12, 8); sl.setSpacing(5)
        sr = QHBoxLayout(); self.ready_label = QLabel("●  Status: Pronto"); self.ready_label.setObjectName("statusReady"); self.progress_pct = QLabel("100%"); self.progress_pct.setObjectName("statusReady")
        sr.addWidget(self.ready_label); sr.addStretch(); sr.addWidget(self.progress_pct); sl.addLayout(sr)
        self.progress = QProgressBar(); self.progress.setObjectName("homeProgress"); self.progress.setTextVisible(False); self.progress.setRange(0,100); self.progress.setValue(100); sl.addWidget(self.progress)
        status_row = QHBoxLayout(); status_row.addWidget(status, 4); integrated = QLabel("Monitoramento integrado"); integrated.setObjectName("cardSubtitle"); integrated.setAlignment(Qt.AlignmentFlag.AlignCenter); status_row.addWidget(integrated, 1)
        hl.addLayout(status_row)
        row.addWidget(hero, 58)

        quick = QFrame(); quick.setObjectName("quickCard"); quick.setMinimumHeight(255)
        ql = QVBoxLayout(quick); ql.setContentsMargins(18, 16, 18, 16); ql.setSpacing(9)
        qtitle = QLabel("⚡  Ações rápidas"); qtitle.setObjectName("cardTitle"); ql.addWidget(qtitle)
        qsub = QLabel("Execute as principais rotinas sem sair do painel."); qsub.setObjectName("cardSubtitle"); ql.addWidget(qsub)
        grid = QGridLayout(); grid.setSpacing(10)
        buttons = (
            ("quickNews", "⌕   Buscar notícias\n      Varredura manual", self.controller.search_news, 0, 0),
            ("quickVideo", "▶   Buscar vídeos\n      Fontes selecionadas", self.controller.search_videos, 0, 1),
            ("quickDemand", "▣   Buscar demandas\n      Demandas ativas", self.controller.search_all_demands, 1, 0),
            ("quickTerms", "⌕   Termos de busca\n      Gerenciar palavras-chave", lambda: self.navigate.emit("TERMS"), 1, 1),
        )
        for obj, label, callback, r, c in buttons:
            b = QPushButton(label); b.setObjectName(obj); b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding); b.clicked.connect(callback); grid.addWidget(b, r, c)
        ql.addLayout(grid, 1)
        row.addWidget(quick, 42)
        self.root.addLayout(row)

    def _schedule_tile(self, title: str, value_object: str) -> tuple[QFrame, QLabel]:
        tile = QFrame(); tile.setObjectName("scheduleTile")
        lay = QVBoxLayout(tile); lay.setContentsMargins(12, 8, 12, 8); lay.setSpacing(4)
        t = QLabel(title); t.setObjectName("scheduleTitle")
        value = QLabel("—"); value.setObjectName(value_object); value.setWordWrap(True)
        lay.addWidget(t); lay.addWidget(value); lay.addStretch(1)
        return tile, value

    def _build_secondary(self) -> None:
        row = QHBoxLayout(); row.setSpacing(14)
        schedule = QFrame(); schedule.setObjectName("scheduleCard"); schedule.setMinimumHeight(142)
        sl = QVBoxLayout(schedule); sl.setContentsMargins(18, 14, 18, 14); sl.setSpacing(7)
        title = QLabel("◷  Agendamento automático"); title.setObjectName("cardTitle"); sl.addWidget(title)
        sub = QLabel("O sistema executa buscas automaticamente nos horários definidos."); sub.setObjectName("cardSubtitle"); sl.addWidget(sub)
        tiles = QHBoxLayout(); tiles.setSpacing(10)
        a, self.news_schedule = self._schedule_tile("Notícias", "scheduleBlue")
        b, self.demand_schedule = self._schedule_tile("Demandas", "scheduleOrange")
        c, self.video_schedule = self._schedule_tile("Vídeos", "schedulePurple")
        tiles.addWidget(a, 1); tiles.addWidget(b, 1); tiles.addWidget(c, 2); sl.addLayout(tiles)
        row.addWidget(schedule, 1)

        summary = QFrame(); summary.setObjectName("summaryCard"); summary.setMinimumHeight(142)
        su = QVBoxLayout(summary); su.setContentsMargins(18, 14, 18, 14); su.setSpacing(7)
        st = QLabel("▥  Resumo do dia"); st.setObjectName("cardTitle"); su.addWidget(st)
        ss = QLabel("Dados atuais disponíveis no aplicativo."); ss.setObjectName("cardSubtitle"); su.addWidget(ss)
        vals = QHBoxLayout(); vals.setSpacing(16)
        self.summary_news = QLabel("0"); self.summary_news.setObjectName("summaryBlue")
        self.summary_videos = QLabel("0"); self.summary_videos.setObjectName("summaryPurple")
        self.summary_demands = QLabel("0"); self.summary_demands.setObjectName("summaryOrange")
        for value, label in ((self.summary_news,"Notícias"),(self.summary_videos,"Vídeos"),(self.summary_demands,"Demandas")):
            box = QVBoxLayout(); value.setAlignment(Qt.AlignmentFlag.AlignCenter); lab = QLabel(label); lab.setObjectName("summaryLabel"); lab.setAlignment(Qt.AlignmentFlag.AlignCenter); box.addWidget(value); box.addWidget(lab); vals.addLayout(box, 1)
        su.addLayout(vals, 1)
        row.addWidget(summary, 1)
        self.root.addLayout(row)

    def _bottom_card(self, title: str, subtitle: str, icon: str) -> QFrame:
        frame = QFrame(); frame.setObjectName("bottomCard"); frame.setMinimumHeight(94)
        lay = QVBoxLayout(frame); lay.setContentsMargins(16, 12, 16, 12); lay.setSpacing(4)
        t = QLabel(f"{icon}  {title}"); t.setObjectName("cardTitle"); s = QLabel(subtitle); s.setObjectName("cardSubtitle"); s.setWordWrap(True)
        lay.addWidget(t); lay.addWidget(s); lay.addStretch(1)
        return frame

    def _build_bottom(self) -> None:
        row = QHBoxLayout(); row.setSpacing(14)
        row.addWidget(self._bottom_card("Fontes em destaque", "Principais fontes monitoradas pelo sistema.", "☷"), 1)
        row.addWidget(self._bottom_card("Últimas atividades", "Registro das ações mais recentes no sistema.", "◴"), 1)
        row.addWidget(self._bottom_card("Dicas e operação", "Orientações para melhor uso do sistema.", "●"), 1)
        self.root.addLayout(row)

    def refresh(self, state: UiState) -> None:
        now_ms = int(datetime.now().timestamp() * 1000)
        day_ago = now_ms - 86_400_000
        news_count = len(state.news)
        video_count = len(state.videos)
        video_today = sum(1 for v in state.videos if v.capturedAt >= day_ago)
        demand_count = sum(1 for d in state.demands if d.active)
        source_count = len(self.controller.news_sources)

        self.metric_labels["news"].setText(str(news_count))
        self.metric_labels["videos"].setText(str(video_count))
        self.metric_labels["today"].setText(str(video_today))
        self.metric_labels["demands"].setText(str(demand_count))
        self.metric_labels["sources"].setText(str(source_count))
        self.summary_news.setText(str(news_count))
        self.summary_videos.setText(str(video_count))
        self.summary_demands.setText(str(demand_count))

        auto = self.controller.automation_settings
        self.news_schedule.setText(f"{auto.news_interval_minutes} min" if auto.news_automatic else "Desativado")
        dm = auto.demand_interval_minutes
        self.demand_schedule.setText((f"{dm // 60} hora" if dm == 60 else f"{dm} min") if auto.demand_automatic else "Desativado")
        times = sorted(auto.video_schedule_times)
        self.video_schedule.setText(", ".join(times) if auto.video_automatic and times else "Desativado")

        busy = bool(state.news_busy or state.video_busy)
        if busy:
            fractions = []
            if state.news_busy: fractions.append(float(getattr(state.news_progress, "fraction", 0.0)))
            if state.video_busy: fractions.append(float(getattr(state.video_progress, "fraction", 0.0)))
            pct = round((sum(fractions) / max(1, len(fractions))) * 100)
            self.ready_label.setText("●  Status: Em execução")
        else:
            pct = 100
            self.ready_label.setText("●  Status: Pronto")
        self.progress.setValue(max(0, min(100, pct)))
        self.progress_pct.setText(f"{max(0, min(100, pct))}%")
