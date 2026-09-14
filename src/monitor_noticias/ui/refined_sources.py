from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from monitor_noticias.ui.catalog import REGIONS, STATES
from monitor_noticias.ui.refined_base import BasePage, ToggleSwitch, card, secondary


class SourceRow(QWidget):
    toggled = Signal(str, bool)

    def __init__(self, source, checked: bool, enabled: bool, all_mode: bool = False) -> None:
        super().__init__()
        self.source = source
        row = QHBoxLayout(self)
        row.setContentsMargins(12, 5, 12, 5)
        row.setSpacing(12)

        self.check = QCheckBox()
        self.check.setChecked(checked)
        self.check.setEnabled(enabled)
        self.check.setToolTip(
            "Desative 'Todos os veículos' para escolher fontes individualmente."
            if not enabled and all_mode else
            "Incluir ou remover esta fonte das buscas."
        )
        row.addWidget(self.check)

        initials = "".join(part[:1] for part in source.name.split()[:3]).upper()[:3] or source.name[:3].upper()
        sig = QLabel(initials)
        sig.setFixedSize(58, 42)
        sig.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sig.setStyleSheet(
            "color:#ffffff;background:#087af7;border:1px solid #22c5ff;"
            "border-radius:9px;font-weight:800;"
        )
        row.addWidget(sig)

        text = QVBoxLayout()
        text.setSpacing(1)
        name = QLabel(source.name)
        name.setObjectName("smallTitle")
        meta = QLabel(
            f"{source.group}  •  {getattr(source, 'region', 'Nacional') or 'Nacional'}"
            f"  •  {getattr(source, 'state', '') or 'BR'}"
        )
        meta.setObjectName("smallText")
        text.addWidget(name)
        text.addWidget(meta)
        row.addLayout(text, 1)

        self.badge = QLabel()
        self.badge.setMinimumWidth(118)
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if not enabled and all_mode:
            badge_text = "Incluída por Todos"
            badge_style = "color:#18e39c;border:1px solid #0ba779;background:#063b3f;"
        elif checked:
            badge_text = "Selecionada"
            badge_style = "color:#18e39c;border:1px solid #0ba779;background:#063b3f;"
        else:
            badge_text = "Disponível"
            badge_style = "color:#8fc9e9;border:1px solid #0a6b98;background:#062d49;"
        self.badge.setText(badge_text)
        self.badge.setStyleSheet(
            badge_style + "border-radius:7px;padding:5px 9px;font-weight:700;"
        )
        row.addWidget(self.badge)
        self.check.toggled.connect(lambda value: self.toggled.emit(source.id, value))


class SourcesPage(BasePage):
    """Seleção de fontes com filtros legíveis, preservando as preferências existentes."""

    def __init__(self, controller):
        super().__init__(controller)
        self._guard = False
        self._signature = None
        self._tab = 0
        self.region = "Todas"
        self.state = "Todos"
        self._state_regions = {code: region for code, _name, region in STATES}

        top, top_layout = card("filterCard", (14, 11, 14, 12), 9)

        first = QHBoxLayout()
        self.tab_buttons: list[QPushButton] = []
        for index, text in enumerate(("Notícias", "Vídeos", "Mídia especializada")):
            button = secondary(QPushButton(text))
            button.setCheckable(True)
            button.setMinimumHeight(42)
            button.setChecked(index == 0)
            button.clicked.connect(lambda _checked=False, i=index: self._set_tab(i))
            first.addWidget(button)
            self.tab_buttons.append(button)
        first.addStretch()
        self.query = QLineEdit()
        self.query.setPlaceholderText("⌕   Pesquisar por nome, região, estado ou grupo...")
        self.query.setMinimumWidth(390)
        self.query.setMaximumWidth(560)
        first.addWidget(self.query)
        top_layout.addLayout(first)

        filters = QHBoxLayout()
        filters.setSpacing(8)
        region_label = QLabel("Região")
        region_label.setObjectName("smallTitle")
        filters.addWidget(region_label)
        self.region_combo = QComboBox()
        self.region_combo.setMinimumWidth(170)
        self.region_combo.addItems(REGIONS)
        filters.addWidget(self.region_combo)
        state_label = QLabel("Estado")
        state_label.setObjectName("smallTitle")
        filters.addWidget(state_label)
        self.state_combo = QComboBox()
        self.state_combo.setMinimumWidth(185)
        filters.addWidget(self.state_combo)
        self.filter_hint = QLabel("Use os filtros para reduzir a lista sem alterar sua seleção.")
        self.filter_hint.setObjectName("smallText")
        filters.addWidget(self.filter_hint)
        filters.addStretch()
        top_layout.addLayout(filters)
        self.root.addWidget(top)

        allbox, all_layout = card("statusCard", (16, 11, 16, 11), 5)
        all_row = QHBoxLayout()
        globe = QLabel("●")
        globe.setStyleSheet("color:#13e39a;font-size:27px;")
        all_row.addWidget(globe)
        all_text = QVBoxLayout()
        self.all_title = QLabel("Todos os veículos — sem exceção")
        self.all_title.setObjectName("greenText")
        self.all_description = QLabel(
            "Quando ligado, qualquer veículo encontrado é aceito e a seleção individual abaixo fica apenas informativa."
        )
        self.all_description.setObjectName("smallText")
        self.all_description.setWordWrap(True)
        all_text.addWidget(self.all_title)
        all_text.addWidget(self.all_description)
        all_row.addLayout(all_text, 1)
        self.all_label = QLabel("LIGADO")
        self.all_label.setObjectName("greenText")
        all_row.addWidget(self.all_label)
        self.all_news = ToggleSwitch()
        all_row.addWidget(self.all_news)
        all_layout.addLayout(all_row)
        self.root.addWidget(allbox)

        tools, tools_layout = card("filterCard", (14, 9, 14, 9), 5)
        toolbar = QHBoxLayout()
        self.info = QLabel()
        self.info.setObjectName("sectionTitle")
        toolbar.addWidget(self.info)
        self.selection_note = QLabel()
        self.selection_note.setObjectName("smallText")
        toolbar.addWidget(self.selection_note)
        toolbar.addStretch()
        self.select_visible = QPushButton("✓  Selecionar visíveis")
        self.clear_visible = secondary(QPushButton("Limpar visíveis"))
        self.select_all = secondary(QPushButton("Selecionar todas"))
        self.clear_all = secondary(QPushButton("Limpar todas"))
        for button in (self.select_visible, self.clear_visible, self.select_all, self.clear_all):
            toolbar.addWidget(button)
        tools_layout.addLayout(toolbar)
        self.root.addWidget(tools)

        self.list = QListWidget()
        self.list.setSpacing(4)
        self.list.setAlternatingRowColors(False)
        self.root.addWidget(self.list, 1)

        self.query.textChanged.connect(lambda _text: self._request_refresh())
        self.region_combo.currentTextChanged.connect(self._region_changed)
        self.state_combo.currentTextChanged.connect(self._state_changed)
        self.all_news.toggled.connect(self._all_news_changed)
        self.select_visible.clicked.connect(lambda: self._set_visible(True))
        self.clear_visible.clicked.connect(lambda: self._set_visible(False))
        self.select_all.clicked.connect(lambda: self._set_all(True))
        self.clear_all.clicked.connect(lambda: self._set_all(False))
        self._populate_states()

    def _request_refresh(self) -> None:
        if self._guard:
            return
        self._signature = None
        self.refresh(self.controller.state)

    def _set_tab(self, index: int) -> None:
        self._tab = index
        for current, button in enumerate(self.tab_buttons):
            button.setChecked(current == index)
        self._signature = None
        self.refresh(self.controller.state)

    def _region_changed(self, region: str) -> None:
        if self._guard:
            return
        self.region = region or "Todas"
        self.state = "Todos"
        self._populate_states()
        self._signature = None
        self.refresh(self.controller.state)

    def _state_changed(self, state: str) -> None:
        if self._guard:
            return
        self.state = state or "Todos"
        self._signature = None
        self.refresh(self.controller.state)

    def _populate_states(self) -> None:
        self._guard = True
        try:
            self.state_combo.clear()
            self.state_combo.addItem("Todos")
            if self.region == "Nacional":
                pass
            else:
                for code, name, region in STATES:
                    if self.region == "Todas" or region == self.region:
                        self.state_combo.addItem(f"{code} — {name}", code)
            self.state_combo.setCurrentIndex(0)
        finally:
            self._guard = False

    def _selected_state_code(self) -> str:
        if self.state_combo.currentIndex() <= 0:
            return "Todos"
        data = self.state_combo.currentData()
        return str(data) if data else "Todos"

    def _all_news_changed(self, value: bool) -> None:
        if self._guard or self._tab == 1:
            return
        self.controller.news_all_sources = value
        self._signature = None
        self.refresh(self.controller.state)

    def _base(self):
        if self._tab == 0:
            return self.controller.news_sources
        if self._tab == 1:
            return self.controller.video_sources
        return self.controller.specialized_sources

    def _selected_sources(self):
        query = self.query.text().strip().lower()
        result = []
        selected_state = self._selected_state_code()
        for source in self._base():
            src_region = getattr(source, "region", "Nacional") or "Nacional"
            src_state = getattr(source, "state", "") or "BR"
            if self.region != "Todas" and src_region != self.region:
                continue
            if selected_state != "Todos" and src_state != selected_state:
                continue
            haystack = (
                f"{source.name} {src_region} {src_state} {source.group} "
                f"{' '.join(getattr(source, 'aliases', ()))}"
            ).lower()
            if query and query not in haystack:
                continue
            result.append(source)
        return result

    def refresh(self, state) -> None:
        all_mode = self.controller.news_all_sources and self._tab != 1
        self._guard = True
        try:
            self.all_news.setEnabled(self._tab != 1)
            self.all_news.setChecked(all_mode)
            self.all_news._sync(all_mode)
            if self._tab == 1:
                self.all_label.setText("N/A")
                self.all_title.setText("Fontes de vídeo")
                self.all_description.setText(
                    "Vídeos usam seleção própria; escolha abaixo quais fontes participam da varredura."
                )
            else:
                self.all_label.setText("LIGADO" if all_mode else "DESLIGADO")
                self.all_title.setText("Todos os veículos — sem exceção")
                self.all_description.setText(
                    "Quando ligado, qualquer veículo encontrado é aceito e a seleção individual abaixo fica apenas informativa."
                    if all_mode else
                    "Modo seletivo ativo: somente as fontes marcadas abaixo participam da seleção por catálogo."
                )
        finally:
            self._guard = False

        visible = self._selected_sources()
        selected = (
            self.controller.selected_video_source_ids
            if self._tab == 1 else
            self.controller.selected_news_source_ids
        )
        enabled = self._tab == 1 or not all_mode
        selected_visible = sum(1 for source in visible if source.id in selected)
        if all_mode:
            selected_visible = len(visible)
        self.info.setText(f"▤   {len(visible)} fonte(s) visível(is)")
        self.selection_note.setText(
            "Modo Todos ativo — seleção individual ignorada"
            if all_mode else
            f"{selected_visible} selecionada(s) neste filtro"
        )
        for button in (self.select_visible, self.clear_visible, self.select_all, self.clear_all):
            button.setEnabled(enabled)

        signature = (
            self._tab,
            self.region,
            self._selected_state_code(),
            self.query.text(),
            all_mode,
            tuple(sorted(selected)),
            tuple(source.id for source in visible),
        )
        if signature == self._signature:
            return
        self._signature = signature
        self.list.clear()
        for source in visible:
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 68))
            self.list.addItem(item)
            widget = SourceRow(
                source,
                all_mode or source.id in selected,
                enabled,
                all_mode=all_mode,
            )
            widget.toggled.connect(self._source_toggled)
            self.list.setItemWidget(item, widget)

    def _source_toggled(self, source_id: str, checked: bool) -> None:
        if self._tab == 1:
            self.controller.set_video_source(source_id, checked)
        else:
            self.controller.set_news_source(source_id, checked)
        self._signature = None
        self.refresh(self.controller.state)

    def _set_visible(self, checked: bool) -> None:
        for source in self._selected_sources():
            if self._tab == 1:
                self.controller.set_video_source(source.id, checked)
            else:
                self.controller.set_news_source(source.id, checked)
        self._signature = None
        self.refresh(self.controller.state)

    def _set_all(self, checked: bool) -> None:
        base = self._base()
        if self._tab == 1:
            self.controller.selected_video_source_ids = {source.id for source in base} if checked else set()
        else:
            if self._tab == 0 and checked:
                self.controller.news_all_sources = True
            elif self._tab == 0 and not checked:
                self.controller.news_all_sources = False
                self.controller.selected_news_source_ids = set()
            else:
                ids = self.controller.selected_news_source_ids
                specialized = {source.id for source in base}
                self.controller.selected_news_source_ids = (
                    ids | specialized if checked else ids - specialized
                )
        self._signature = None
        self.refresh(self.controller.state)
