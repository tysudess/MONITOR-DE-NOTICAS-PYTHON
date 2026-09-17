from __future__ import annotations

from collections import Counter
from datetime import datetime

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QProgressBar, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)

_INSTALLED = False

STYLE = r"""
QWidget#lightHome { background:#f4f8fc; color:#0b1b57; font-family:'Segoe UI'; }
QScrollArea#lightHomeScroll { background:#f4f8fc; border:0; }
QScrollArea#lightHomeScroll > QWidget > QWidget { background:#f4f8fc; }
QFrame#whiteCard { background:white; border:1px solid #d9e6f3; border-radius:14px; }
QLabel#eyebrow { color:#61749c; font-size:11px; font-weight:700; }
QLabel#homeTitle { color:#0c1958; font-size:28px; font-weight:900; }
QLabel#homeSub { color:#61749c; font-size:12px; }
QLabel#cardTitle { color:#0c1958; font-size:12px; font-weight:800; }
QLabel#cardValue { color:#081347; font-size:26px; font-weight:900; }
QLabel#muted { color:#68799d; font-size:10px; }
QLabel#panelTitle { color:#0c1958; font-size:16px; font-weight:900; }
QLabel#panelText { color:#61749c; font-size:11px; }
QLabel#statusGood { color:#087b4d; font-size:13px; font-weight:800; }
QPushButton#quickPrimary { background:#0b79f7; color:white; border:0; border-radius:11px; padding:13px 16px; font-size:12px; font-weight:800; text-align:left; }
QPushButton#quickPrimary:hover { background:#096cdf; }
QPushButton#quickSecondary { background:#edf5ff; color:#0c4fa7; border:1px solid #c9dff6; border-radius:11px; padding:12px 16px; font-size:12px; font-weight:800; text-align:left; }
QProgressBar#miniBar { background:#eef3f8; border:0; border-radius:4px; max-height:8px; }
QProgressBar#miniBar::chunk { background:#147df5; border-radius:4px; }
QFrame#activityRow { background:#ffffff; border:0; border-top:1px solid #edf2f7; }
QLabel#rank { color:#446690; background:#eaf2fb; border-radius:9px; padding:2px 6px; font-size:9px; }
"""


def _label(text: str = "", name: str = "") -> QLabel:
    w = QLabel(text)
    if name:
        w.setObjectName(name)
    return w


class MiniTrend(QWidget):
    def __init__(self, accent: str) -> None:
        super().__init__()
        self.accent = QColor(accent)
        self.values = [0, 0, 0, 0, 0]
        self.setFixedHeight(28)

    def set_values(self, values) -> None:
        vals = list(values)[-5:]
        self.values = ([0] * (5 - len(vals)) + vals)[:5]
        self.update()

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        r = self.rect().adjusted(3, 3, -3, -3)
        maxv = max([1] + self.values)
        pts = []
        for i, val in enumerate(self.values):
            x = r.left() + r.width() * i / 4
            y = r.bottom() - r.height() * val / maxv
            pts.append(QPointF(x, y))
        p.setPen(QPen(self.accent, 2))
        for i in range(len(pts) - 1):
            p.drawLine(pts[i], pts[i + 1])


class DayChart(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.news = [0] * 24
        self.videos = [0] * 24
        self.demands = [0] * 24
        self.setMinimumHeight(118)

    def set_values(self, news, videos, demands) -> None:
        self.news = list(news)[:24] + [0] * max(0, 24 - len(news))
        self.videos = list(videos)[:24] + [0] * max(0, 24 - len(videos))
        self.demands = list(demands)[:24] + [0] * max(0, 24 - len(demands))
        self.update()

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        r = self.rect().adjusted(34, 8, -10, -22)
        p.setPen(QPen(QColor("#d9e6f2"), 1))
        for i in range(5):
            y = r.bottom() - r.height() * i / 4
            p.drawLine(QPointF(r.left(), y), QPointF(r.right(), y))
        maxv = max([1] + self.news + self.videos + self.demands)
        colors = (QColor("#147df5"), QColor("#7d36ef"), QColor("#f6a000"))
        datasets = (self.news, self.videos, self.demands)
        group = r.width() / 24.0
        bw = max(2.0, group * .17)
        for hour in range(24):
            x0 = r.left() + hour * group + group * .22
            for j, data in enumerate(datasets):
                h = r.height() * data[hour] / maxv
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(colors[j])
                p.drawRoundedRect(QRectF(x0 + j * bw * 1.25, r.bottom() - h, bw, h), 1.5, 1.5)
        p.setPen(QPen(QColor("#5f7395"), 1))
        for hour in range(0, 24, 3):
            x = r.left() + hour * group
            p.drawText(QRectF(x - 12, r.bottom() + 4, 30, 14), Qt.AlignmentFlag.AlignCenter, f"{hour:02d}h")


class StatCard(QFrame):
    def __init__(self, title: str, accent: str, glyph: str, subtitle: str) -> None:
        super().__init__()
        self.setObjectName("whiteCard")
        self.setMinimumHeight(102)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 12, 12, 10)
        icon = QLabel(glyph)
        icon.setFixedSize(46, 46)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(f"background:{accent}22;color:{accent};border-radius:14px;font-size:22px;font-weight:900;")
        lay.addWidget(icon)
        right = QVBoxLayout(); right.setSpacing(1)
        right.addWidget(_label(title, "cardTitle"))
        self.value = _label("0", "cardValue")
        right.addWidget(self.value)
        self.sub = _label(subtitle, "muted")
        right.addWidget(self.sub)
        self.trend = MiniTrend(accent)
        right.addWidget(self.trend)
        lay.addLayout(right, 1)


class LightHome(QWidget):
    def __init__(self, controller, navigate_signal) -> None:
        super().__init__()
        self.controller = controller
        self.navigate = navigate_signal
        self.setObjectName("lightHome")
        self.setStyleSheet(STYLE)
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea(); scroll.setObjectName("lightHomeScroll"); scroll.setWidgetResizable(True); scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        body = QWidget(); self.body = QVBoxLayout(body); self.body.setContentsMargins(20, 18, 20, 18); self.body.setSpacing(12)
        scroll.setWidget(body); root.addWidget(scroll)
        self._build_header(); self._build_stats(); self._build_center(); self._build_mid(); self._build_bottom()

    def _card(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        f = QFrame(); f.setObjectName("whiteCard")
        l = QVBoxLayout(f); l.setContentsMargins(16, 14, 16, 14); l.setSpacing(8)
        l.addWidget(_label(title, "panelTitle"))
        return f, l

    def _build_header(self) -> None:
        row = QHBoxLayout(); row.setSpacing(16)
        left = QVBoxLayout(); left.setSpacing(2)
        left.addWidget(_label("CENTRAL DE INTELIGÊNCIA DE MÍDIA", "eyebrow"))
        left.addWidget(_label("Monitor de Notícias", "homeTitle"))
        left.addWidget(_label("Acompanhe notícias, vídeos, demandas e fontes em tempo real.", "homeSub"))
        row.addLayout(left, 1)
        self.search = QLineEdit(); self.search.setPlaceholderText("⌕   Buscar notícias, vídeos, demandas ou fontes...")
        self.search.setStyleSheet("background:white;color:#25365e;border:1px solid #d5e2f0;border-radius:12px;padding:0 16px;min-height:44px;")
        row.addWidget(self.search, 1)
        self.body.addLayout(row)

    def _build_stats(self) -> None:
        row = QHBoxLayout(); row.setSpacing(10)
        self.cards = {
            "news24": StatCard("Notícias 24h", "#147df5", "▤", "na janela atual"),
            "videos": StatCard("Vídeos armazenados", "#7d36ef", "▶", "relevantes na base"),
            "videos_today": StatCard("Vídeos hoje", "#008c61", "◉", "capturados hoje"),
            "demands": StatCard("Demandas", "#f6a000", "▣", "ativas"),
            "sources": StatCard("Fontes", "#c00059", "◍", "monitoradas"),
        }
        for card in self.cards.values(): row.addWidget(card, 1)
        self.body.addLayout(row)

    def _build_center(self) -> None:
        row = QHBoxLayout(); row.setSpacing(12)
        hero, hl = self._card("")
        title = _label("Central pronta para monitorar", "panelTitle"); title.setStyleSheet("font-size:20px;font-weight:900;color:#0c1958;")
        hl.addWidget(title)
        hl.addWidget(_label("As buscas e os resultados são atualizados nesta tela em tempo real.", "panelText"))
        self.status_box = QFrame(); self.status_box.setStyleSheet("background:#e9f8f2;border:0;border-radius:10px;")
        sl = QVBoxLayout(self.status_box); sl.setContentsMargins(14, 12, 14, 12)
        self.status_title = _label("●  Status: Pronto", "statusGood"); sl.addWidget(self.status_title)
        self.status_detail = _label("Monitoramento ativo e funcionando normalmente.", "panelText"); sl.addWidget(self.status_detail)
        hl.addWidget(self.status_box)
        hl.addStretch()
        row.addWidget(hero, 2)

        quick, ql = self._card("⚡  Ações rápidas")
        for text, handler, primary in (
            ("⌕   Buscar notícias", lambda: self.controller.search_news(*self.controller.period_last_hours(24)), True),
            ("▶   Buscar vídeos", lambda: self.controller.search_videos(*self.controller.period_last_hours(24)), False),
            ("▣   Buscar demandas", self.controller.search_all_demands, False),
        ):
            b = QPushButton(text); b.setObjectName("quickPrimary" if primary else "quickSecondary"); b.clicked.connect(handler); ql.addWidget(b)
        ql.addStretch(); row.addWidget(quick, 1)
        self.body.addLayout(row)

    def _build_mid(self) -> None:
        row = QHBoxLayout(); row.setSpacing(12)
        sched, sl = self._card("◷  Agendamento automático")
        self.schedule_news = _label("Notícias  •  a cada 30 min", "panelText")
        self.schedule_demands = _label("Demandas  •  a cada 60 min", "panelText")
        self.schedule_videos = _label("Vídeos  •  horários definidos", "panelText")
        for w in (self.schedule_news, self.schedule_demands, self.schedule_videos): sl.addWidget(w)
        row.addWidget(sched, 1)

        chart_card, cl = self._card("▥  Resumo do dia")
        self.chart = DayChart(); cl.addWidget(self.chart)
        row.addWidget(chart_card, 2)
        self.body.addLayout(row)

    def _build_bottom(self) -> None:
        row = QHBoxLayout(); row.setSpacing(12)
        sources, sl = self._card("◉  Fontes mais relevantes")
        self.source_rows = []
        for i in range(5):
            rr = QHBoxLayout(); rank = _label(str(i + 1), "rank"); rank.setFixedWidth(24); name = _label("—", "panelText"); count = _label("0", "muted")
            rr.addWidget(rank); rr.addWidget(name, 1); rr.addWidget(count); sl.addLayout(rr); self.source_rows.append((name, count))
        row.addWidget(sources, 1)

        acts, al = self._card("◷  Últimas atividades")
        self.activity_rows = []
        for _ in range(3):
            title = _label("Sistema pronto", "cardTitle"); detail = _label("—", "muted"); al.addWidget(title); al.addWidget(detail); self.activity_rows.append((title, detail))
        row.addWidget(acts, 1)

        tips, tl = self._card("💡  Dicas")
        tl.addWidget(_label("Use termos de busca específicos", "cardTitle"))
        tip = _label("Quanto mais específicos os termos, mais relevantes serão os resultados.", "panelText"); tip.setWordWrap(True); tl.addWidget(tip); tl.addStretch()
        row.addWidget(tips, 1)
        self.body.addLayout(row)

    def refresh(self, state) -> None:
        now = datetime.now()
        today = now.date()
        news24 = len(state.news)
        videos = len(state.videos)
        videos_today = sum(1 for v in state.videos if getattr(v, "date", 0) and datetime.fromtimestamp(getattr(v, "date", 0) / 1000).date() == today)
        demands = len(state.demands)
        sources_total = len(getattr(self.controller, "news_sources", ()))
        values = {"news24": news24, "videos": videos, "videos_today": videos_today, "demands": demands, "sources": sources_total}
        for key, value in values.items():
            self.cards[key].value.setText(str(value))
            self.cards[key].trend.set_values([0, 0, max(0, value // 3), max(0, value // 2), value])

        busy = state.news_busy or state.video_busy
        self.status_title.setText("●  Status: Monitorando" if busy else "●  Status: Pronto")
        self.status_detail.setText(state.status if state.status else "Monitoramento ativo e funcionando normalmente.")

        counts = Counter(getattr(n, "source", "") or "Sem fonte" for n in state.news)
        for idx, (name, count) in enumerate(self.source_rows):
            if idx < len(counts.most_common(5)):
                source, total = counts.most_common(5)[idx]; name.setText(source); count.setText(str(total))
            else:
                name.setText("—"); count.setText("0")

        events = [
            ("Sistema iniciado", "Monitor de Notícias pronto"),
            ("Notícias", f"{news24} registro(s) nas últimas 24h"),
            ("Vídeos", f"{videos} registro(s) armazenado(s)"),
        ]
        for row, data in zip(self.activity_rows, events):
            row[0].setText(data[0]); row[1].setText(data[1])

        by_news = [0] * 24; by_videos = [0] * 24; by_demands = [0] * 24
        for n in state.news:
            try: by_news[datetime.fromtimestamp(getattr(n, "date", 0) / 1000).hour] += 1
            except Exception: pass
        for v in state.videos:
            try: by_videos[datetime.fromtimestamp(getattr(v, "date", 0) / 1000).hour] += 1
            except Exception: pass
        self.chart.set_values(by_news, by_videos, by_demands)


def install_v021_light_home_dashboard() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    from monitor_noticias.ui.v017_home_truth import ReferenceHome
    from monitor_noticias.ui import v019_exact_reference as exact

    def new_init(self, controller):
        QWidget.__init__(self)
        self.controller = controller
        self._light = LightHome(controller, self.navigate)
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.addWidget(self._light)

    def new_refresh(self, state):
        self._light.refresh(state)

    ReferenceHome.__init__ = new_init
    ReferenceHome.refresh = new_refresh

    def no_truth_surface(page):
        surface = getattr(page, "_v019_truth_surface", None)
        if surface is not None:
            surface.hide()

    exact._install_home_truth = no_truth_surface
