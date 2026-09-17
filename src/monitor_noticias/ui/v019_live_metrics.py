from __future__ import annotations

"""Dados vivos precisos sobre a imagem-verdade v0.0.19.

A Home funcional v0.0.17 continua sendo a única fonte dos valores. Esta camada
apenas substitui trechos pequenos da arte estática pelos valores reais, sem
redesenhar painéis, bordas ou a composição geral e sem alterar controller,
banco, coletores, automação ou rotas.
"""

from PySide6.QtCore import QLineF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen

_INSTALLED = False


def _widget_text(widget, fallback="—") -> str:
    try:
        value = str(widget.text()).strip()
        return value if value else fallback
    except Exception:
        return fallback


def _font(p: QPainter, size: int, *, bold: bool = True, color: str = "#ffffff") -> None:
    font = QFont("Segoe UI")
    font.setPixelSize(size)
    font.setBold(bold)
    p.setFont(font)
    p.setPen(QColor(color))


def _draw_value(p: QPainter, rect: QRectF, value: str, *, size: int = 20,
                color: str = "#ffffff", bold: bool = True,
                align=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter) -> None:
    _font(p, size, bold=bold, color=color)
    p.drawText(rect, align, str(value))


def _replace_text(p: QPainter, rect: QRectF, value: str, *, bg: str,
                  size: int = 14, color: str = "#ffffff", bold: bool = True,
                  align=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                  radius: float = 2.0) -> None:
    """Apaga só a área ocupada pelo texto estático e escreve o valor real."""
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(bg))
    p.drawRoundedRect(rect, radius, radius)
    _draw_value(p, rect, value, size=size, color=color, bold=bold, align=align)


def _paint_chart(p: QPainter, page) -> None:
    chart = getattr(page, "chart", None)
    if chart is None:
        return

    news = list(getattr(chart, "news", [0] * 24))[:24]
    videos = list(getattr(chart, "videos", [0] * 24))[:24]
    demands = list(getattr(chart, "demands", [0] * 24))[:24]
    news += [0] * (24 - len(news))
    videos += [0] * (24 - len(videos))
    demands += [0] * (24 - len(demands))

    # Somente a área interna do gráfico é atualizada. Título, legenda, seletor e
    # moldura continuam vindo literalmente da imagem-verdade.
    plot = QRectF(610, 620, 790, 119)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#051d31"))
    p.drawRect(plot)

    p.setPen(QPen(QColor(91, 145, 177, 60), 1))
    for i in range(5):
        yy = plot.bottom() - plot.height() * i / 4.0
        p.drawLine(QLineF(plot.left(), yy, plot.right(), yy))

    maximum = max([1] + news + videos + demands)
    group = plot.width() / 24.0
    bw = max(2.0, group * .18)
    colors = (QColor("#00c9ff"), QColor("#9256ff"), QColor("#ffc21a"))
    for hour in range(24):
        x0 = plot.left() + hour * group + group * .18
        for idx, data in enumerate((news, videos, demands)):
            height = plot.height() * float(data[hour]) / maximum
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(colors[idx])
            p.drawRoundedRect(
                QRectF(x0 + idx * bw * 1.25, plot.bottom() - height, bw, height),
                1.5, 1.5,
            )


def install_v019_live_metrics() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    from monitor_noticias.ui.v017_home_truth import ReferenceHome
    from monitor_noticias.ui.v019_exact_reference import HomeTruthSurface
    from monitor_noticias.ui import v019_exact_reference as ref

    old_paint = HomeTruthSurface.paintEvent
    old_refresh = ReferenceHome.refresh

    def paint(self, event):
        old_paint(self, event)
        page = getattr(self, "page", None)
        if page is None or self.width() <= 0 or self.height() <= 0:
            return

        sx = self.width() / ref.REF_CONTENT_W
        sy = self.height() / ref.REF_CONTENT_H
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.scale(sx, sy)

        # Cards superiores: apaga exclusivamente o número estático.
        cards = getattr(page, "module_cards", {})
        card_specs = {
            "NEWS": (QRectF(26, 244, 90, 34), "#08243d"),
            "VIDEOS": (QRectF(177, 244, 90, 34), "#111d45"),
            "DEMANDS": (QRectF(323, 244, 90, 34), "#282619"),
            "SOURCES": (QRectF(475, 244, 90, 34), "#07283b"),
            "TERMS": (QRectF(625, 244, 90, 34), "#111d43"),
            "COVERS": (QRectF(776, 244, 90, 34), "#08243b"),
        }
        for route, (rect, bg) in card_specs.items():
            card = cards.get(route)
            if card is not None:
                _replace_text(p, rect, _widget_text(getattr(card, "value", None)),
                              bg=bg, size=21)

        # Monitoramento em tempo real: seis métricas, cada uma substituída dentro
        # da mesma pequena caixa ocupada pelo número original.
        live = getattr(page, "live_values", {})
        metric_specs = (
            ("pct", QRectF(18, 418, 64, 29), "#00e5c2"),
            ("found", QRectF(94, 418, 64, 29), "#00d9ff"),
            ("new", QRectF(174, 418, 64, 29), "#ff355d"),
            ("fails", QRectF(247, 418, 64, 29), "#8d68ff"),
            ("steps", QRectF(315, 418, 64, 29), "#27baff"),
            ("time", QRectF(375, 418, 64, 29), "#00e3d0"),
        )
        for key, rect, color in metric_specs:
            _replace_text(
                p, rect, _widget_text(live.get(key), "0"), bg="#052239",
                size=17, color=color, align=Qt.AlignmentFlag.AlignCenter,
            )

        # Fontes mais ativas: limpa somente texto/barra de cada linha.
        rows = getattr(page, "source_rows", [])
        for idx in range(5):
            y = 373 + idx * 29
            if idx >= len(rows):
                continue
            name, bar, count = rows[idx]
            _replace_text(p, QRectF(452, y, 126, 23), _widget_text(name, "—"),
                          bg="#061f35", size=12, bold=False)
            try:
                pct = max(0, min(100, int(bar.value())))
            except Exception:
                pct = 0
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor("#07314d"))
            p.drawRoundedRect(QRectF(586, y + 9, 110, 6), 3, 3)
            p.setBrush(QColor("#00d9ff"))
            p.drawRoundedRect(QRectF(586, y + 9, 110 * pct / 100.0, 6), 3, 3)
            _replace_text(
                p, QRectF(704, y, 36, 23), _widget_text(count, ""),
                bg="#061f35", size=12, bold=False,
                align=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            )

        # Automação: apenas detalhe e status das três linhas.
        auto_rows = getattr(page, "auto_rows", {})
        for idx, key in enumerate(("news", "demands", "videos")):
            entry = auto_rows.get(key)
            if not entry:
                continue
            y = 374 + idx * 47
            detail, active = entry
            _replace_text(
                p, QRectF(846, y + 15, 150, 22), _widget_text(detail, "—"),
                bg="#061f35", size=11, color="#a9bfd3", bold=False,
            )
            _replace_text(
                p, QRectF(1021, y + 3, 68, 29), _widget_text(active, "—"),
                bg="#063a38", size=11, color="#36e6ae",
                align=Qt.AlignmentFlag.AlignCenter, radius=8,
            )

        # Atividade recente: substitui só os dois campos textuais por linha.
        activity = getattr(page, "activity_labels", [])
        for idx in range(min(5, len(activity))):
            y = 620 + idx * 39
            time_label, text_label = activity[idx]
            _replace_text(
                p, QRectF(62, y, 57, 30), _widget_text(time_label, ""),
                bg="#061f35", size=12, color="#b9d0e3", bold=False,
            )
            _replace_text(
                p, QRectF(125, y, 340, 30), _widget_text(text_label, ""),
                bg="#061f35", size=11, color="#eef5ff", bold=False,
            )

        _paint_chart(p, page)

        # Totais inferiores.
        summary = getattr(page, "summary", {})
        summary_specs = {
            "news": (QRectF(639, 778, 95, 34), "#06243b"),
            "videos": (QRectF(906, 778, 95, 34), "#101f43"),
            "demands": (QRectF(1173, 778, 95, 34), "#292619"),
        }
        for key, (rect, bg) in summary_specs.items():
            _replace_text(p, rect, _widget_text(summary.get(key), "0"),
                          bg=bg, size=19)

        p.end()

    def refresh(self, state):
        old_refresh(self, state)
        surface = getattr(self, "_v019_truth_surface", None)
        if surface is not None:
            surface.update()

    HomeTruthSurface.paintEvent = paint
    ReferenceHome.refresh = refresh
