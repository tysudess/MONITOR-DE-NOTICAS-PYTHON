from __future__ import annotations

"""Dados vivos mínimos sobre a imagem-verdade v0.0.19.

Esta camada atualiza apenas os valores numéricos dos cards superiores e dos
resumos inferiores. Não cria máscaras largas, não redesenha painéis e não altera
rotas, controller, banco, coletores ou automação.
"""

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter

_INSTALLED = False


def _widget_text(widget, fallback="—") -> str:
    try:
        value = widget.text()
        value = str(value).strip()
        return value if value else fallback
    except Exception:
        return fallback


def _draw_value(p: QPainter, rect: QRectF, value: str, *, size: int = 20,
                align=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter) -> None:
    font = QFont("Segoe UI")
    font.setPixelSize(size)
    font.setBold(True)
    p.setFont(font)
    p.setPen(QColor("#ffffff"))
    p.drawText(rect, align, str(value))


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
        p.scale(sx, sy)

        cards = getattr(page, "module_cards", {})
        # Posições calibradas para substituir apenas os números da arte,
        # sem cobrir os títulos, subtítulos ou bordas dos cards.
        card_rects = {
            "NEWS": QRectF(26, 244, 90, 34),
            "VIDEOS": QRectF(177, 244, 90, 34),
            "DEMANDS": QRectF(323, 244, 90, 34),
            "SOURCES": QRectF(475, 244, 90, 34),
            "TERMS": QRectF(625, 244, 90, 34),
            "COVERS": QRectF(776, 244, 90, 34),
        }
        for route, rect in card_rects.items():
            card = cards.get(route)
            if card is None:
                continue
            _draw_value(p, rect, _widget_text(getattr(card, "value", None)), size=21)

        summary = getattr(page, "summary", {})
        summary_rects = {
            "news": QRectF(639, 778, 95, 34),
            "videos": QRectF(906, 778, 95, 34),
            "demands": QRectF(1173, 778, 95, 34),
        }
        for key, rect in summary_rects.items():
            _draw_value(p, rect, _widget_text(summary.get(key), "0"), size=19)

        p.end()

    def refresh(self, state):
        old_refresh(self, state)
        surface = getattr(self, "_v019_truth_surface", None)
        if surface is not None:
            surface.update()

    HomeTruthSurface.paintEvent = paint
    ReferenceHome.refresh = refresh
