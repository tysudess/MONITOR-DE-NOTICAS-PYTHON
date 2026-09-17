from __future__ import annotations

"""v0.0.21 — remove sobreposições e aplica imagens-verdade em Notícias, Fontes e Termos.

As páginas funcionais originais continuam instanciadas, recebendo refresh e callbacks.
A camada literal é opaca e visual; eventos de mouse atravessam para os controles reais
existentes por baixo. Dados variáveis são redesenhados a partir do controller/widgets reais.
"""

import sys
from pathlib import Path

from PySide6.QtCore import QLineF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QWidget

_INSTALLED = False
_PIX: dict[str, QPixmap] = {}
REF_W = 1447.0
REF_H = 855.0


def _resource_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "resources"
    return Path(__file__).resolve().parents[3] / "resources"


def _pix(name: str) -> QPixmap:
    cached = _PIX.get(name)
    if cached is not None and not cached.isNull():
        return cached
    path = _resource_root() / "ui" / "v021" / f"{name}-page-q90.webp"
    pix = QPixmap(str(path))
    if pix.isNull():
        raise RuntimeError(f"Imagem-verdade v0.0.21 não pôde ser carregada: {path}")
    _PIX[name] = pix
    return pix


def _font(size: float, bold: bool = False) -> QFont:
    f = QFont("Segoe UI")
    f.setPixelSize(max(8, round(size)))
    f.setBold(bold)
    return f


def _text(p: QPainter, r: QRectF, value, size=13, color="#eef6ff", bold=False,
          align=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter):
    p.setFont(_font(size, bold))
    p.setPen(QColor(color))
    p.drawText(r, align, str(value))


def _mask(p: QPainter, r: QRectF, color="#061d32", radius=3):
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(color))
    p.drawRoundedRect(r, radius, radius)


def _widget_text(widget, fallback=""):
    try:
        value = str(widget.text())
        return value if value.strip() else fallback
    except Exception:
        return fallback


class LiteralPageSurface(QWidget):
    def __init__(self, page, name: str):
        super().__init__(page)
        self.page = page
        self.name = name
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setObjectName(f"v021LiteralSurface_{name}")
        self.show()
        self.raise_()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        p.drawPixmap(QRectF(self.rect()), _pix(self.name), QRectF(0, 0, REF_W, REF_H))
        sx = self.width() / REF_W if self.width() else 1.0
        sy = self.height() / REF_H if self.height() else 1.0
        p.scale(sx, sy)
        if self.name == "noticias":
            _paint_news(self.page, p)
        elif self.name == "fontes":
            _paint_sources(self.page, p)
        elif self.name == "termos":
            _paint_terms(self.page, p)
        p.end()


def _paint_news(page, p: QPainter):
    state = page.controller.state
    rows = page._rows(state)

    # Busca digitada: cobre somente o placeholder quando há texto real.
    query = page.query.text().strip()
    if query:
        _mask(p, QRectF(65, 166, 790, 34), "#071e34")
        _text(p, QRectF(80, 166, 760, 34), query, 13, "#eaf4ff")

    # Status e métricas reais; a máscara é alta o bastante para eliminar
    # simultaneamente número congelado + qualquer overlay anterior.
    try:
        metrics = page.exec.metric_labels
        specs = (("pct", 714), ("found", 817), ("fresh", 922),
                 ("errors", 1026), ("steps", 1135), ("time", 1243))
        for key, x in specs:
            _mask(p, QRectF(x, 337, 80, 43), "#061d32")
            _text(p, QRectF(x, 337, 80, 43), _widget_text(metrics.get(key), "0"),
                  18, "#19d9ff" if key != "errors" else "#ff335e", True,
                  Qt.AlignmentFlag.AlignCenter)
    except Exception:
        pass

    # Resumo real da busca.
    _mask(p, QRectF(92, 323, 500, 33), "#061d32")
    status = getattr(state, "status", "") or "Pronto"
    _text(p, QRectF(100, 323, 480, 33), status, 13, "#dcecff", True)
    _mask(p, QRectF(246, 450, 330, 30), "#061d32")
    _text(p, QRectF(250, 450, 320, 30), f"{len(rows)} resultado(s) para o período selecionado",
          12, "#b6cbdd")

    # Lista real substitui integralmente os exemplos congelados do print.
    _mask(p, QRectF(0, 488, 1447, 367), "#031b2e", 0)
    y = 497.0
    for idx, item in enumerate(rows[:5]):
        accent = ("#13b8ff", "#9a55ff", "#ffc229", "#25b7ff", "#1ce0a0")[idx % 5]
        p.setPen(QPen(QColor("#0b6b9d"), 1))
        p.setBrush(QColor("#05233a"))
        p.drawRoundedRect(QRectF(10, y, 1418, 67), 10, 10)
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor(accent)); p.drawRect(QRectF(10, y, 7, 67))
        source = getattr(item, "source", "") or "Fonte"
        date = getattr(item, "date", "") or ""
        title = getattr(item, "title", "") or "Sem título"
        snippet = getattr(item, "snippet", "") or ""
        _text(p, QRectF(118, y + 5, 610, 18), f"{source}   •   {date}", 11, "#49caff")
        _text(p, QRectF(118, y + 21, 670, 23), title, 13, "#ffffff", True)
        if snippet:
            _text(p, QRectF(118, y + 43, 700, 18), snippet[:110], 10, "#b4c9dc")
        # Mantém visual dos botões da imagem; callbacks reais permanecem por baixo.
        for bx, bw, label, color in ((835, 130, "Abrir matéria", "#0b78b1"),
                                     (976, 120, "WhatsApp", "#05a979"),
                                     (1107, 120, "Copiar link", "#0b78b1"),
                                     (1238, 145, "Extrair matéria", "#8845c7")):
            p.setPen(QPen(QColor(color), 1)); p.setBrush(QColor("#08233b"))
            p.drawRoundedRect(QRectF(bx, y + 14, bw, 39), 8, 8)
            _text(p, QRectF(bx, y + 14, bw, 39), label, 11, "#eef7ff", True,
                  Qt.AlignmentFlag.AlignCenter)
        y += 75


def _paint_sources(page, p: QPainter):
    query = page.query.text().strip()
    if query:
        _mask(p, QRectF(602, 276, 470, 35), "#071e34")
        _text(p, QRectF(620, 276, 440, 35), query, 13)

    visible = page._selected_sources()
    selected = (page.controller.selected_video_source_ids if page._tab == 1
                else page.controller.selected_news_source_ids)
    all_mode = page.controller.news_all_sources and page._tab != 1

    _mask(p, QRectF(74, 348, 270, 54), "#061d32")
    _text(p, QRectF(95, 350, 95, 31), str(len(visible)), 25, "#ffffff", True)
    _text(p, QRectF(95, 378, 180, 20), "fontes visíveis", 13, "#00ccff", True)

    # Tabela real completa substitui os exemplos estáticos.
    _mask(p, QRectF(15, 421, 1412, 385), "#031b2e", 0)
    header = ((85, "Fonte"), (355, "Categoria"), (535, "Região"),
              (700, "Estado"), (805, "Tags"), (1170, "Selecionada"))
    p.setPen(QPen(QColor("#0a557d"), 1)); p.drawLine(QLineF(25, 444, 1415, 444))
    for x, label in header:
        _text(p, QRectF(x, 421, 170, 23), label, 11, "#d8e7f5", True)

    y = 450.0
    for idx, source in enumerate(visible[:8]):
        p.setPen(QPen(QColor("#0a4668"), 1)); p.drawLine(QLineF(25, y + 38, 1415, y + 38))
        name = getattr(source, "name", "")
        group = getattr(source, "group", "") or "Notícias"
        region = getattr(source, "region", "Nacional") or "Nacional"
        state = getattr(source, "state", "") or "--"
        sid = getattr(source, "id", "")
        checked = all_mode or sid in selected
        _text(p, QRectF(80, y, 260, 36), name, 12, "#ffffff", True)
        _text(p, QRectF(355, y, 165, 36), group, 11, "#72d3ff")
        _text(p, QRectF(535, y, 150, 36), region, 11, "#dce8f3")
        _text(p, QRectF(700, y, 90, 36), state, 11, "#dce8f3")
        aliases = list(getattr(source, "aliases", ()) or ())[:3]
        _text(p, QRectF(805, y, 330, 36), "  •  ".join(aliases) if aliases else group,
              10, "#65cfff")
        _text(p, QRectF(1170, y, 120, 36), "Sim" if checked else "Não", 11,
              "#28e6ad" if checked else "#bccbdd", True)
        y += 40


def _paint_terms(page, p: QPainter):
    news = list(page.controller.state.terms)
    videos = list(getattr(page.controller, "video_terms", []))

    # Contadores reais — máscara ampla elimina completamente os números da imagem.
    for x, value, color in ((548, len(news), "#2de8ff"), (1264, len(videos), "#e75cff")):
        _mask(p, QRectF(x, 166, 100, 60), "#071e34")
        _text(p, QRectF(x, 166, 100, 38), str(value), 27, color, True,
              Qt.AlignmentFlag.AlignCenter)
        _text(p, QRectF(x - 5, 202, 110, 22), "termos cadastrados", 10, "#b7cce0",
              False, Qt.AlignmentFlag.AlignCenter)

    # Texto digitado nos campos reais aparece sobre a referência.
    for edit, r in ((page.news_col.edit, QRectF(101, 276, 390, 43)),
                    (page.video_col.edit, QRectF(815, 276, 390, 43))):
        text = edit.text().strip()
        if text:
            _mask(p, r, "#071e34")
            _text(p, QRectF(r.x()+16, r.y(), r.width()-22, r.height()), text, 12)

    # Listas reais substituem as linhas congeladas.
    for values, x, w, accent in ((news, 36, 540, "#16cfff"), (videos, 751, 540, "#dc45ff")):
        _mask(p, QRectF(x, 346, w, 390), "#031b2e", 0)
        p.setPen(QPen(QColor("#0a557d"), 1)); p.drawLine(QLineF(x+10, 383, x+w-10, 383))
        _text(p, QRectF(x+68, 350, 260, 31), "Termo", 11, "#dce8f4", True)
        y = 389.0
        for idx, value in enumerate(values[:10]):
            p.setPen(QPen(QColor("#0a4668"), 1)); p.drawLine(QLineF(x+10, y+35, x+w-10, y+35))
            # checkbox visual
            p.setPen(QPen(QColor("#9ac8e5"), 1)); p.setBrush(QColor("#061d32"))
            p.drawRoundedRect(QRectF(x+18, y+8, 16, 16), 3, 3)
            _text(p, QRectF(x+68, y, w-140, 34), value, 12, "#eef6ff")
            _text(p, QRectF(x+w-46, y, 28, 34), "⋮", 18, "#dce8f4", True,
                  Qt.AlignmentFlag.AlignCenter)
            y += 36


def _install_surface(page, name: str):
    attr = f"_v021_{name}_surface"
    surface = getattr(page, attr, None)
    if surface is None:
        surface = LiteralPageSurface(page, name)
        setattr(page, attr, surface)
    surface.setGeometry(page.rect())
    surface.show(); surface.raise_(); surface.update()
    return surface


def _refresh_surfaces(window):
    from monitor_noticias.ui.sections import Section
    mapping = ((Section.NEWS, "noticias"), (Section.SOURCES, "fontes"), (Section.TERMS, "termos"))
    for section, name in mapping:
        page = getattr(window, "pages", {}).get(section)
        if page is not None:
            _install_surface(page, name)


def _cleanup_home(surface, event, old_paint):
    old_paint(surface, event)
    page = getattr(surface, "page", None)
    if page is None or surface.width() <= 0 or surface.height() <= 0:
        return
    from monitor_noticias.ui import v019_exact_reference as ref
    sx = surface.width() / ref.REF_CONTENT_W
    sy = surface.height() / ref.REF_CONTENT_H
    p = QPainter(surface); p.setRenderHint(QPainter.RenderHint.Antialiasing, True); p.scale(sx, sy)

    # Cards: apaga uma faixa única que engloba valor congelado e overlay v0.0.20.
    card_bg = {"NEWS":"#08243d","VIDEOS":"#111d45","DEMANDS":"#282619","SOURCES":"#07283b",
               "TERMS":"#111d43","COVERS":"#08243b","PDF_EDITOR":"#08283a","EXTRACTOR":"#101e43","VIDEO_EDITOR":"#291b3a"}
    cards = getattr(page, "module_cards", {})
    for x, y, w, h, route in surface.CARD_RECTS:
        _mask(p, QRectF(x+10, y+72, w-20, 58), card_bg.get(route, "#071d34"))
        card = cards.get(route); value = _widget_text(getattr(card, "value", None), "—") if card else "—"
        _text(p, QRectF(x+18, y+79, w-34, 34), value, 20, "#ffffff", True)

    live = getattr(page, "live_values", {})
    specs = (("pct",18,"#00e5c2"),("found",94,"#00d9ff"),("new",174,"#ff355d"),
             ("fails",247,"#8d68ff"),("steps",315,"#27baff"),("time",375,"#00e3d0"))
    _mask(p, QRectF(10, 406, 438, 54), "#052239")
    for key, x, color in specs:
        _text(p, QRectF(x, 414, 64, 31), _widget_text(live.get(key), "0"), 17, color, True,
              Qt.AlignmentFlag.AlignCenter)
    p.end()


def install_v021_literal_tabs() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    from monitor_noticias.ui.main_window import MainWindow
    from monitor_noticias.ui.refined_search import NewsPage
    from monitor_noticias.ui.refined_sources import SourcesPage
    from monitor_noticias.ui.refined_management import TermsPage
    from monitor_noticias.ui.v019_exact_reference import HomeTruthSurface

    old_build = MainWindow._build_ui
    old_nav = MainWindow.navigate
    old_news_refresh = NewsPage.refresh
    old_sources_refresh = SourcesPage.refresh
    old_terms_refresh = TermsPage.refresh
    old_home_paint = HomeTruthSurface.paintEvent

    def build(self):
        old_build(self)
        _refresh_surfaces(self)

    def navigate(self, section):
        old_nav(self, section)
        _refresh_surfaces(self)
        # reaplica após callbacks tardios para impedir qualquer UI histórica de subir.
        for delay in (0, 50, 250, 900):
            QTimer.singleShot(delay, lambda w=self: _refresh_surfaces(w))

    def news_refresh(self, state):
        old_news_refresh(self, state)
        surface = getattr(self, "_v021_noticias_surface", None)
        if surface is not None: surface.update()

    def sources_refresh(self, state):
        old_sources_refresh(self, state)
        surface = getattr(self, "_v021_fontes_surface", None)
        if surface is not None: surface.update()

    def terms_refresh(self, state):
        old_terms_refresh(self, state)
        surface = getattr(self, "_v021_termos_surface", None)
        if surface is not None: surface.update()

    def home_paint(self, event):
        _cleanup_home(self, event, old_home_paint)

    MainWindow._build_ui = build
    MainWindow.navigate = navigate
    NewsPage.refresh = news_refresh
    SourcesPage.refresh = sources_refresh
    TermsPage.refresh = terms_refresh
    HomeTruthSurface.paintEvent = home_paint
