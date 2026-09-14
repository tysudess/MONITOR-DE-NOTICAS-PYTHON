from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from monitor_noticias.ui.refined_base import (
    BasePage,
    ProxyTestThread,
    ToggleSwitch,
    card,
    dangerous,
    heading,
    secondary,
)


class AutomationBlock(QFrame):
    """Card visual para uma rotina automática, sem duplicar o motor de automação."""

    def __init__(
        self,
        title: str,
        subtitle: str,
        color: str,
        interval_options: list[str] | None = None,
    ) -> None:
        super().__init__()
        self.setObjectName("techCard")
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(8)

        top = QHBoxLayout()
        glyph = "▤" if title == "Notícias" else "▣" if title == "Demandas" else "▶"
        icon = QLabel(glyph)
        icon.setFixedSize(44, 44)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            f"color:{color};background:#063052;border:1px solid {color};"
            "border-radius:9px;font-size:21px;font-weight:800;"
        )
        top.addWidget(icon)
        titles = QVBoxLayout()
        titles.setSpacing(1)
        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("smallText")
        subtitle_label.setWordWrap(True)
        titles.addWidget(title_label)
        titles.addWidget(subtitle_label)
        top.addLayout(titles, 1)
        self.toggle = ToggleSwitch()
        top.addWidget(self.toggle)
        root.addLayout(top)

        bottom = QHBoxLayout()
        self.badge = QLabel("Automático ativo")
        self.badge.setStyleSheet(
            "color:#14e69a;border:1px solid #0bb47b;border-radius:7px;"
            "padding:4px 8px;font-weight:700;"
        )
        bottom.addWidget(self.badge)
        bottom.addStretch()
        self.interval: QComboBox | None = None
        if interval_options:
            label = QLabel("Intervalo")
            label.setObjectName("smallText")
            bottom.addWidget(label)
            self.interval = QComboBox()
            for value in interval_options:
                self.interval.addItem(f"{value} min", value)
            self.interval.setMinimumWidth(118)
            bottom.addWidget(self.interval)
        root.addLayout(bottom)
        self.toggle.toggled.connect(self._sync_badge)

    def _sync_badge(self, checked: bool) -> None:
        self.badge.setText("Automático ativo" if checked else "Automático pausado")
        self.badge.setStyleSheet(
            ("color:#14e69a;border:1px solid #0bb47b;" if checked else
             "color:#ffc21a;border:1px solid #a87900;")
            + "border-radius:7px;padding:4px 8px;font-weight:700;"
        )

    def set_interval_value(self, value: int) -> None:
        if self.interval is None:
            return
        index = self.interval.findData(str(value))
        if index >= 0:
            self.interval.setCurrentIndex(index)

    def interval_value(self, fallback: int) -> int:
        if self.interval is None:
            return fallback
        data = self.interval.currentData()
        return int(data) if data is not None else fallback


class SettingsPage(BasePage):
    """Configurações refinadas mantendo AutomationSettings/ProxySettings como fonte de verdade."""

    def __init__(self, controller):
        super().__init__(controller)
        self._proxy_thread = None
        self._loading = False
        self._proxy_dirty = False
        self._automation_dirty = False

        summary, summary_layout = card("filterCard", (16, 10, 16, 10), 4)
        summary_row = QHBoxLayout()
        info = QVBoxLayout()
        title = QLabel("Central de configurações")
        title.setObjectName("sectionTitle")
        subtitle = QLabel(
            "Ajuste rede, inicialização e horários automáticos. Alterações de automação só entram em vigor ao clicar em Aplicar automação."
        )
        subtitle.setObjectName("smallText")
        subtitle.setWordWrap(True)
        info.addWidget(title)
        info.addWidget(subtitle)
        summary_row.addLayout(info, 1)
        self.save_state = QLabel("Configurações carregadas")
        self.save_state.setObjectName("greenText")
        summary_row.addWidget(self.save_state)
        summary_layout.addLayout(summary_row)
        self.root.addWidget(summary)

        upper = QHBoxLayout()
        upper.setSpacing(12)

        proxy, proxy_layout = card("techCard", (16, 13, 16, 13), 9)
        proxy.setMinimumWidth(620)
        ph = QHBoxLayout()
        lock = QLabel("▣")
        lock.setFixedSize(50, 50)
        lock.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lock.setStyleSheet(
            "color:#56cbff;background:#075884;border:1px solid #0a86b8;"
            "border-radius:10px;font-size:23px;"
        )
        ph.addWidget(lock)
        titles = QVBoxLayout()
        ptitle = QLabel("Configuração de proxy")
        ptitle.setObjectName("sectionTitle")
        self.proxy_description = QLabel()
        self.proxy_description.setObjectName("smallText")
        self.proxy_description.setWordWrap(True)
        titles.addWidget(ptitle)
        titles.addWidget(self.proxy_description)
        ph.addLayout(titles, 1)
        self.proxy_state = QLabel()
        self.proxy_state.setObjectName("smallTitle")
        ph.addWidget(self.proxy_state)
        self.proxy_enabled = ToggleSwitch()
        ph.addWidget(self.proxy_enabled)
        proxy_layout.addLayout(ph)

        fields = QGridLayout()
        fields.setHorizontalSpacing(8)
        fields.setVerticalSpacing(5)
        self.host = QLineEdit()
        self.host.setPlaceholderText("Servidor/IP")
        self.port = QSpinBox()
        self.port.setRange(1, 65535)
        self.user = QLineEdit()
        self.user.setPlaceholderText("Usuário")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Senha")
        for col, text in enumerate(("Servidor", "Porta", "Usuário", "Senha")):
            label = QLabel(text)
            label.setObjectName("smallText")
            fields.addWidget(label, 0, col)
        fields.addWidget(self.host, 1, 0)
        fields.addWidget(self.port, 1, 1)
        fields.addWidget(self.user, 1, 2)
        fields.addWidget(self.password, 1, 3)
        proxy_layout.addLayout(fields)

        proxy_actions = QHBoxLayout()
        self.save_proxy = QPushButton("✓  Salvar e aplicar")
        self.test_proxy = secondary(QPushButton("⌁  Testar conexão"))
        proxy_actions.addWidget(self.save_proxy)
        proxy_actions.addWidget(self.test_proxy)
        proxy_actions.addStretch()
        proxy_layout.addLayout(proxy_actions)
        self.proxy_message = QLabel()
        self.proxy_message.setObjectName("smallText")
        self.proxy_message.setWordWrap(True)
        proxy_layout.addWidget(self.proxy_message)
        upper.addWidget(proxy, 3)

        general, general_layout = card("techCard", (16, 13, 16, 13), 10)
        general.setMinimumWidth(360)
        general_layout.addWidget(heading("Automação e inicialização", "Controles gerais do Monitor."))
        g1 = QHBoxLayout()
        gtext = QVBoxLayout()
        glabel = QLabel("Buscas automáticas")
        glabel.setObjectName("smallTitle")
        gsub = QLabel("Liga ou pausa todas as rotinas automáticas.")
        gsub.setObjectName("smallText")
        gsub.setWordWrap(True)
        gtext.addWidget(glabel)
        gtext.addWidget(gsub)
        g1.addLayout(gtext, 1)
        self.general = ToggleSwitch()
        g1.addWidget(self.general)
        general_layout.addLayout(g1)
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background:#0b5f85;border:0;")
        general_layout.addWidget(divider)
        g2 = QHBoxLayout()
        stext = QVBoxLayout()
        st = QLabel("Iniciar com o Windows")
        st.setObjectName("smallTitle")
        st2 = QLabel("Inicialização automática ao entrar no sistema.")
        st2.setObjectName("smallText")
        st2.setWordWrap(True)
        stext.addWidget(st)
        stext.addWidget(st2)
        g2.addLayout(stext, 1)
        self.startup = ToggleSwitch()
        g2.addWidget(self.startup)
        general_layout.addLayout(g2)
        general_layout.addStretch()
        upper.addWidget(general, 2)
        self.root.addLayout(upper)

        schedules = QHBoxLayout()
        schedules.setSpacing(12)
        self.news_block = AutomationBlock(
            "Notícias", "Varredura das fontes selecionadas", "#38c9ff", ["15", "30", "45", "60", "120"]
        )
        self.dem_block = AutomationBlock(
            "Demandas", "Pesquisa de todas as demandas ativas", "#ffc21a", ["15", "30", "45", "60", "120"]
        )
        self.video_block = AutomationBlock(
            "Vídeos", "Execução nos horários definidos abaixo", "#b45cff", None
        )
        schedules.addWidget(self.news_block, 1)
        schedules.addWidget(self.dem_block, 1)
        schedules.addWidget(self.video_block, 1)
        self.root.addLayout(schedules)

        video_card, video_layout = card("filterCard", (16, 10, 16, 10), 7)
        vrow = QHBoxLayout()
        vt = QVBoxLayout()
        vl = QLabel("Horários automáticos dos vídeos")
        vl.setObjectName("smallTitle")
        vh = QLabel("Use HH:MM separados por vírgula. Ex.: 08:00, 12:00, 15:00, 19:00, 21:00")
        vh.setObjectName("smallText")
        vt.addWidget(vl)
        vt.addWidget(vh)
        vrow.addLayout(vt)
        self.video_times = QLineEdit()
        self.video_times.setPlaceholderText("08:00, 12:00, 15:00, 19:00, 21:00")
        self.video_times.setMinimumWidth(420)
        vrow.addWidget(self.video_times, 1)
        self.apply_auto = QPushButton("✓  Aplicar automação")
        self.apply_auto.setMinimumHeight(42)
        vrow.addWidget(self.apply_auto)
        video_layout.addLayout(vrow)
        self.auto_message = QLabel()
        self.auto_message.setObjectName("smallText")
        video_layout.addWidget(self.auto_message)
        self.root.addWidget(video_card)
        self.root.addStretch()

        self.save_proxy.clicked.connect(self._save_proxy)
        self.test_proxy.clicked.connect(self._test_proxy)
        self.apply_auto.clicked.connect(self._apply_auto)
        self.startup.toggled.connect(self._startup)

        self.host.textEdited.connect(self._mark_proxy_dirty)
        self.user.textEdited.connect(self._mark_proxy_dirty)
        self.password.textEdited.connect(self._mark_proxy_dirty)
        self.port.valueChanged.connect(lambda _value: self._mark_proxy_dirty())
        self.proxy_enabled.toggled.connect(lambda _value: self._mark_proxy_dirty())

        for switch in (self.general, self.news_block.toggle, self.dem_block.toggle, self.video_block.toggle):
            switch.toggled.connect(lambda _value: self._mark_automation_dirty())
        if self.news_block.interval is not None:
            self.news_block.interval.currentIndexChanged.connect(lambda _index: self._mark_automation_dirty())
        if self.dem_block.interval is not None:
            self.dem_block.interval.currentIndexChanged.connect(lambda _index: self._mark_automation_dirty())
        self.video_times.textEdited.connect(self._mark_automation_dirty)

    def _mark_proxy_dirty(self) -> None:
        if self._loading:
            return
        self._proxy_dirty = True
        self.save_state.setText("Alterações de proxy pendentes")

    def _mark_automation_dirty(self) -> None:
        if self._loading:
            return
        self._automation_dirty = True
        self.save_state.setText("Alterações de automação pendentes")

    def _save_proxy(self) -> None:
        cfg = self.controller.save_proxy(
            self.proxy_enabled.isChecked(),
            self.host.text(),
            self.port.value(),
            self.user.text(),
            self.password.text(),
        )
        self.proxy_message.setText("Configuração de proxy salva e aplicada.")
        self.password.clear()
        self.host.setText(cfg.host)
        self.port.setValue(cfg.port)
        self._proxy_dirty = False
        self.save_state.setText("Proxy salvo")

    def _test_proxy(self) -> None:
        self.test_proxy.setEnabled(False)
        self.proxy_message.setText("Testando conexão...")
        self._proxy_thread = ProxyTestThread(self.controller)
        self._proxy_thread.completed.connect(self._proxy_done)
        self._proxy_thread.start()

    def _proxy_done(self, ok, text) -> None:
        self.proxy_message.setText(text)
        self.test_proxy.setEnabled(True)
        self._proxy_thread = None

    def _startup(self, checked) -> None:
        if self._loading:
            return
        ok = self.controller.set_start_with_windows(checked)
        if checked and not ok:
            self.startup.setToolTip(
                "Executável empacotado ainda não existe; preferência preservada para o portable final."
            )

    def _apply_auto(self) -> None:
        settings = self.controller.automation_settings
        settings.automatic_monitoring = self.general.isChecked()
        settings.news_automatic = self.news_block.toggle.isChecked()
        settings.demand_automatic = self.dem_block.toggle.isChecked()
        settings.video_automatic = self.video_block.toggle.isChecked()
        settings.news_interval_minutes = self.news_block.interval_value(settings.news_interval_minutes)
        settings.demand_interval_minutes = self.dem_block.interval_value(settings.demand_interval_minutes)
        settings.video_schedule_times = {
            value.strip() for value in self.video_times.text().split(",") if value.strip()
        }
        self._automation_dirty = False
        self.auto_message.setText("Automação salva. Os novos intervalos e horários já estão ativos.")
        self.save_state.setText("Automação salva")
        self.controller.refresh()

    def refresh(self, state) -> None:
        self._loading = True
        try:
            cfg = self.controller.proxy_config
            self.proxy_state.setText("Ativado" if cfg.enabled else "Desativado")
            self.proxy_description.setText(
                f"Servidor fixo {cfg.host}:{cfg.port}. Informe usuário e senha para autenticação."
                if cfg.host else
                "Configure o servidor proxy já suportado pelo aplicativo."
            )
            if not self._proxy_dirty:
                self.proxy_enabled.setChecked(cfg.enabled)
                self.proxy_enabled._sync(cfg.enabled)
                self.host.setText(cfg.host)
                self.port.setValue(cfg.port)
                self.user.setText(cfg.username)

            settings = self.controller.automation_settings
            if not self._automation_dirty:
                for widget, value in (
                    (self.general, settings.automatic_monitoring),
                    (self.news_block.toggle, settings.news_automatic),
                    (self.dem_block.toggle, settings.demand_automatic),
                    (self.video_block.toggle, settings.video_automatic),
                ):
                    widget.setChecked(value)
                    widget._sync(value)
                self.news_block.set_interval_value(settings.news_interval_minutes)
                self.dem_block.set_interval_value(settings.demand_interval_minutes)
                self.video_times.setText(", ".join(sorted(settings.video_schedule_times)))

            self.news_block._sync_badge(self.news_block.toggle.isChecked())
            self.dem_block._sync_badge(self.dem_block.toggle.isChecked())
            self.video_block._sync_badge(self.video_block.toggle.isChecked())

            self.startup.setChecked(self.controller.start_with_windows)
            self.startup._sync(self.controller.start_with_windows)
        finally:
            self._loading = False


class StopPage(BasePage):
    def __init__(self, controller):
        super().__init__(controller)
        self.news_status = QLabel()
        self.video_status = QLabel()
        self.news = dangerous(QPushButton("■  Parar notícias/demandas"))
        self.video = dangerous(QPushButton("■  Parar vídeos"))
        self.all = dangerous(QPushButton("■  Parar tudo"))
        self.news.clicked.connect(controller.stop_news_search)
        self.video.clicked.connect(controller.stop_video_search)
        self.all.clicked.connect(controller.stop_all_searches)
        for title, label, button in (
            ("Notícias e demandas", self.news_status, self.news),
            ("Vídeos", self.video_status, self.video),
        ):
            frame, layout = card("techCard", (18, 16, 18, 16), 8)
            layout.addWidget(heading(title, "Interrompa somente a execução atual; a automação permanece configurada."))
            label.setObjectName("smallText")
            layout.addWidget(label)
            layout.addWidget(button, 0, Qt.AlignmentFlag.AlignLeft)
            self.root.addWidget(frame)
        self.root.addWidget(self.all, 0, Qt.AlignmentFlag.AlignLeft)
        self.root.addStretch()

    def refresh(self, state):
        self.news_status.setText(state.status if state.news_busy else "Nenhuma busca em andamento")
        self.video_status.setText(state.video_status if state.video_busy else "Nenhuma busca em andamento")
        self.news.setEnabled(state.news_busy)
        self.video.setEnabled(state.video_busy)
        self.all.setEnabled(state.news_busy or state.video_busy)
