from __future__ import annotations

"""v0.0.20 — dados reais sobre a Home imagem-verdade e shell estável.

Não cria novas fontes de dados. A Home funcional v0.0.17 continua recebendo o
UiState e calculando todos os valores; esta camada apenas pinta esses valores
sobre as posições equivalentes da imagem v0.0.19. Também reaplica o shell
v0.0.19 depois de eventos tardios de navegação para impedir overlays históricos
de restaurarem a sidebar antiga.
"""

from PySide6.QtCore import QLineF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPen

# IMPORTANTE: run.py importa este módulo antes de executar qualquer instalador
# visual. Guardamos aqui o navigate original do MainWindow, antes dos wrappers
# v0.0.17/v0.0.18/v0.0.19. Isso permite preservar a navegação funcional e
# ignorar apenas mutações visuais legadas que reorganizam/deletam a sidebar.
from monitor_noticias.ui.main_window import MainWindow as _UnpatchedMainWindow

_BASE_NAVIGATE = _UnpatchedMainWindow.navigate
_INSTALLED = False


def _text(p: QPainter, rect: QRectF, value: str, *, size: float = 15.0,
          color: str = "#ffffff", bold: bool = True,
          align=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter) -> None:
    font = QFont("Segoe UI")
    font.setPixelSize(max(8, round(size)))
    font.setBold(bold)
    p.setFont(font)
    p.setPen(QColor(color))
    p.drawText(rect, align, str(value))


def _mask(p: QPainter, rect: QRectF, color: str = "#071d34") -> None:
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(color))
    p.drawRoundedRect(rect, 3, 3)


def _widget_text(widget, fallback="—") -> str:
    try:
        value = widget.text()
        return str(value) if str(value).strip() else fallback
    except Exception:
        return fallback


def _paint_live_overlay(surface, event, old_paint) -> None:
    old_paint(surface, event)
    page = getattr(surface, "page", None)
    if page is None or surface.width() <= 0 or surface.height() <= 0:
        return

    from monitor_noticias.ui import v019_exact_reference as ref
    sx = surface.width() / ref.REF_CONTENT_W
    sy = surface.height() / ref.REF_CONTENT_H

    p = QPainter(surface)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.scale(sx, sy)

    card_values = getattr(page, "module_cards", {})
    card_bg = {
        "NEWS": "#08243d", "VIDEOS": "#111d45", "DEMANDS": "#282619",
        "SOURCES": "#07283b", "TERMS": "#111d43", "COVERS": "#08243b",
        "PDF_EDITOR": "#08283a", "EXTRACTOR": "#101e43", "VIDEO_EDITOR": "#291b3a",
    }
    for x, y, w, h, route in surface.CARD_RECTS:
        card = card_values.get(route)
        value = _widget_text(getattr(card, "value", None)) if card is not None else "—"
        r = QRectF(x + 17, y + 82, max(45, w - 44), 31)
        _mask(p, r, card_bg.get(route, "#071d34"))
        _text(p, r, value, size=20, color="#ffffff", bold=True)

    live = getattr(page, "live_values", {})
    metric_spec = (
        ("pct", 18, "#00e5c2"), ("found", 94, "#00d9ff"),
        ("new", 174, "#ff355d"), ("fails", 247, "#8d68ff"),
        ("steps", 315, "#27baff"), ("time", 375, "#00e3d0"),
    )
    for key, x, color in metric_spec:
        r = QRectF(x, 418, 64, 29)
        _mask(p, r, "#052239")
        _text(p, r, _widget_text(live.get(key), "0"), size=17, color=color,
              align=Qt.AlignmentFlag.AlignCenter)

    rows = getattr(page, "source_rows", [])
    for idx in range(5):
        y = 373 + idx * 29
        _mask(p, QRectF(446, y, 300, 24), "#061f35")
        if idx < len(rows):
            name, bar, count = rows[idx]
            name_text = _widget_text(name, "—")
            count_text = _widget_text(count, "")
            try:
                pct = max(0, min(100, int(bar.value())))
            except Exception:
                pct = 0
            _text(p, QRectF(452, y, 128, 23), name_text, size=12, bold=False)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor("#07314d"))
            p.drawRoundedRect(QRectF(586, y + 9, 110, 6), 3, 3)
            p.setBrush(QColor("#00d9ff"))
            p.drawRoundedRect(QRectF(586, y + 9, 110 * pct / 100.0, 6), 3, 3)
            _text(p, QRectF(704, y, 36, 23), count_text, size=12,
                  align=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

    auto_rows = getattr(page, "auto_rows", {})
    for idx, key in enumerate(("news", "demands", "videos")):
        y = 374 + idx * 47
        entry = auto_rows.get(key)
        if not entry:
            continue
        detail, active = entry
        _mask(p, QRectF(843, y + 15, 178, 23), "#061f35")
        _text(p, QRectF(846, y + 15, 136, 22), _widget_text(detail, "—"),
              size=11, color="#a9bfd3", bold=False)
        status = _widget_text(active, "—")
        _mask(p, QRectF(1021, y + 3, 68, 29), "#063a38")
        _text(p, QRectF(1021, y + 3, 68, 29), status, size=11,
              color="#36e6ae", align=Qt.AlignmentFlag.AlignCenter)

    activity = getattr(page, "activity_labels", [])
    for idx in range(5):
        y = 620 + idx * 39
        _mask(p, QRectF(57, y, 410, 34), "#061f35")
        if idx < len(activity):
            time_label, text_label = activity[idx]
            _text(p, QRectF(62, y, 57, 30), _widget_text(time_label, ""),
                  size=12, color="#b9d0e3", bold=False)
            _text(p, QRectF(125, y, 330, 30), _widget_text(text_label, ""),
                  size=11, color="#eef5ff", bold=False)

    chart = getattr(page, "chart", None)
    plot = QRectF(610, 620, 790, 119)
    _mask(p, plot, "#051d31")
    p.setPen(QPen(QColor(91, 145, 177, 60), 1))
    for i in range(5):
        yy = plot.bottom() - plot.height() * i / 4.0
        p.drawLine(QLineF(plot.left(), yy, plot.right(), yy))
    if chart is not None:
        news = list(getattr(chart, "news", [0] * 24))[:24]
        videos = list(getattr(chart, "videos", [0] * 24))[:24]
        demands = list(getattr(chart, "demands", [0] * 24))[:24]
        news += [0] * (24 - len(news)); videos += [0] * (24 - len(videos)); demands += [0] * (24 - len(demands))
        maximum = max([1] + news + videos + demands)
        group = plot.width() / 24.0
        bw = max(2.0, group * .18)
        colors = (QColor("#00c9ff"), QColor("#9256ff"), QColor("#ffc21a"))
        for hour in range(24):
            x0 = plot.left() + hour * group + group * .18
            for j, data in enumerate((news, videos, demands)):
                height = plot.height() * float(data[hour]) / maximum
                p.setPen(Qt.PenStyle.NoPen); p.setBrush(colors[j])
                p.drawRoundedRect(QRectF(x0 + j * bw * 1.25, plot.bottom() - height, bw, height), 1.5, 1.5)

    summary = getattr(page, "summary", {})
    for key, x in (("news", 638), ("videos", 903), ("demands", 1170)):
        r = QRectF(x, 768, 83, 31)
        _mask(p, r, "#06243b")
        _text(p, r, _widget_text(summary.get(key), "0"), size=18, color="#ffffff")

    p.end()


def _reapply_shell(window) -> None:
    from monitor_noticias.ui import v019_exact_reference as ref
    from monitor_noticias.ui.sections import Section

    ref._apply_global_shell(window)
    page = getattr(window, "pages", {}).get(Section.HOME)
    if page is not None:
        ref._install_home_truth(page)
        surface = getattr(page, "_v019_truth_surface", None)
        if surface is not None:
            surface.setGeometry(page.rect())
            surface.show()
            surface.raise_()
            surface.update()


def _schedule_shell(window) -> None:
    for delay in (0, 25, 100, 300, 900):
        QTimer.singleShot(delay, lambda w=window: _reapply_shell(w))


def install_v020_live_home_stable_shell() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    from monitor_noticias.ui.main_window import MainWindow
    from monitor_noticias.ui.v017_home_truth import ReferenceHome
    from monitor_noticias.ui.v019_exact_reference import HomeTruthSurface

    old_paint = HomeTruthSurface.paintEvent
    old_refresh = ReferenceHome.refresh
    old_build = MainWindow._build_ui

    def paint(self, event):
        _paint_live_overlay(self, event, old_paint)

    def refresh(self, state):
        old_refresh(self, state)
        surface = getattr(self, "_v019_truth_surface", None)
        if surface is not None:
            surface.update()

    def build(self):
        old_build(self)
        stack = getattr(self, "stack", None)
        if stack is not None and not getattr(self, "_v020_stack_hook", False):
            stack.currentChanged.connect(lambda _index, w=self: _schedule_shell(w))
            self._v020_stack_hook = True
        timer = QTimer(self)
        timer.setInterval(1500)
        timer.timeout.connect(lambda w=self: _reapply_shell(w))
        timer.start()
        self._v020_shell_timer = timer
        _schedule_shell(self)

    def navigate(self, section):
        # Chama a implementação original, capturada antes de qualquer patch
        # visual. Preserva stack, seleção, refresh, visibilidade funcional das
        # ferramentas e restauração de maximização; ignora apenas wrappers
        # visuais legados que tentam reconstruir a sidebar.
        _BASE_NAVIGATE(self, section)
        _schedule_shell(self)

    HomeTruthSurface.paintEvent = paint
    ReferenceHome.refresh = refresh
    MainWindow._build_ui = build
    MainWindow.navigate = navigate
