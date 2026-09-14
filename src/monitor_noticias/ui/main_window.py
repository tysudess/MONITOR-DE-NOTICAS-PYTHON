from __future__ import annotations

import logging

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QCloseEvent, QIcon, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QPushButton,
    QStackedWidget,
    QStyle,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from monitor_noticias.app.paths import AppPaths
from monitor_noticias.collectors.video.catalog import VIDEO_SOURCES
from monitor_noticias.ui.catalog import NEWS_SOURCES, SPECIALIZED
from monitor_noticias.ui.controller import MainUiController
from monitor_noticias.ui.home_dashboard import HomeDashboard
from monitor_noticias.ui.refined_pages import (
    DemandsPage,
    HistoryPage,
    NewsPage,
    SettingsPage,
    SourcesPage,
    StopPage,
    TermsPage,
    VideosPage,
)
from monitor_noticias.ui.refined_shell import RadarHeader, TechFooter
from monitor_noticias.ui.refined_tools import RefinedExtractorPage, RefinedPdfEditorPage
from monitor_noticias.ui.sections import SECTION_ORDER, TOOL_SECTIONS, Section
from monitor_noticias.ui.theme import APP_STYLESHEET
from monitor_noticias.ui.video_editor_page import VideoEditorPage
from monitor_noticias.windows.notifications import WindowsTrayNotifier

log = logging.getLogger(__name__)


SIDEBAR_STYLESHEET = """
QFrame#sidebar {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #052e50, stop:0.58 #042642, stop:1 #031a30);
    border: 1px solid #087eae;
    border-radius: 14px;
}
QLabel#brandTitle { color:#ffffff; font-size:17px; font-weight:800; }
QLabel#brandSub { color:#a8c3db; font-size:10px; }
QLabel#anchorMark { color:#f5aa00; font-family:'Segoe UI Symbol'; font-size:46px; font-weight:700; }
QPushButton#navButton {
    color:#eef6ff; background:transparent; border:0; border-radius:9px;
    padding:9px 12px; text-align:left; font-size:13px; font-weight:500;
}
QPushButton#navButton:hover { background:#083657; }
QPushButton#navButton:checked {
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0a659d,stop:1 #06375d);
    border:1px solid #00a9e8; color:#ffffff; font-weight:800;
}
QLabel#newsBadge { color:#062440; background:#ffc21a; border-radius:10px; padding:2px 7px; font-size:9px; font-weight:800; }
QFrame#sideStatusCard { background:#052b48; border:1px solid #0a638d; border-radius:10px; }
QLabel#sideStatusTitle { color:#ffffff; font-size:10px; font-weight:800; }
QLabel#sideStatusText, QLabel#sideStatusGood { color:#a9c6df; font-size:9px; }
QLabel#sideMotto { color:#54bff2; font-size:8px; font-weight:700; letter-spacing:1px; }
"""


class SidebarShipArt(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(72)
        self.setMaximumHeight(82)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        w, h = self.width(), self.height()
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(0, 70, 110, 190))
        hull = QPolygonF([
            QPointF(w * .08, h * .67), QPointF(w * .86, h * .67),
            QPointF(w * .76, h * .83), QPointF(w * .20, h * .83),
        ])
        p.drawPolygon(hull)
        p.drawRect(QRectF(w * .35, h * .47, w * .34, h * .20))
        p.drawRect(QRectF(w * .47, h * .31, w * .14, h * .18))
        p.drawRect(QRectF(w * .52, h * .18, w * .02, h * .16))
        p.setPen(QPen(QColor(0, 86, 128, 190), 2))
        p.drawLine(QPointF(w * .53, h * .20), QPointF(w * .67, h * .42))
        p.drawLine(QPointF(w * .53, h * .20), QPointF(w * .40, h * .42))
        p.setPen(QPen(QColor(0, 112, 156, 85), 1))
        p.drawLine(QPointF(w * .05, h * .88), QPointF(w * .93, h * .88))
        p.drawLine(QPointF(w * .18, h * .94), QPointF(w * .82, h * .94))


class MainWindow(QMainWindow):
    def __init__(self, controller: MainUiController | None = None, paths: AppPaths | None = None) -> None:
        super().__init__()
        self.paths = paths or (controller.paths if controller is not None else AppPaths.discover())
        self.controller = controller or MainUiController.create_default(
            self.paths,
            news_sources=NEWS_SOURCES,
            video_sources=VIDEO_SOURCES,
            specialized_sources=SPECIALIZED,
        )
        self._allow_close = False
        self._current = Section.HOME
        self.setWindowTitle("Monitor de Notícias - Windows Portable v4.0.2")
        self.resize(1600, 960)

        icon_path = self.paths.resources / "monitor-icon.svg"
        if icon_path.is_file():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.setStyleSheet(APP_STYLESHEET)
        self._build_ui()
        self._build_tray()
        if hasattr(self.controller, "set_notifier"):
            self.controller.set_notifier(self.notifier)
        self.controller.subscribe(self._state_changed)

        self._timer = QTimer(self)
        self._timer.setInterval(250)
        self._timer.timeout.connect(self._tick)
        self._timer.start()
        self.navigate(Section.HOME)

    def _build_ui(self) -> None:
        root = QWidget(); root.setObjectName("root"); self.setCentralWidget(root)
        outer = QHBoxLayout(root); outer.setContentsMargins(0, 0, 0, 0); outer.setSpacing(0)

        self.sidebar = QFrame(); self.sidebar.setObjectName("sidebar"); self.sidebar.setStyleSheet(SIDEBAR_STYLESHEET); self.sidebar.setFixedWidth(255)
        side = QVBoxLayout(self.sidebar); side.setContentsMargins(14, 13, 14, 10); side.setSpacing(4)

        brand_row = QHBoxLayout(); brand_row.setSpacing(8)
        anchor = QLabel("⚓︎"); anchor.setObjectName("anchorMark"); anchor.setFixedWidth(58); anchor.setAlignment(Qt.AlignmentFlag.AlignCenter); brand_row.addWidget(anchor)
        brand_text = QVBoxLayout(); brand_text.setSpacing(0)
        brand = QLabel("MONITOR\nDE NOTÍCIAS"); brand.setObjectName("brandTitle"); brand_text.addWidget(brand)
        sub = QLabel("Inteligência de mídia"); sub.setObjectName("brandSub"); brand_text.addWidget(sub)
        brand_row.addLayout(brand_text, 1); side.addLayout(brand_row); side.addSpacing(10)

        self.nav_buttons: dict[Section, QPushButton] = {}
        self.nav_holders: dict[Section, QWidget] = {}
        self.news_badge = QLabel("0"); self.news_badge.setObjectName("newsBadge"); self.news_badge.setAlignment(Qt.AlignmentFlag.AlignCenter); self.news_badge.setMinimumWidth(34)
        for section in SECTION_ORDER:
            holder = QWidget(); holder.setStyleSheet("background:transparent;")
            row = QHBoxLayout(holder); row.setContentsMargins(0,0,0,0); row.setSpacing(4)
            button = QPushButton(f"{section.value.icon}   {section.value.label}"); button.setObjectName("navButton"); button.setCheckable(True); button.setMinimumHeight(44); button.clicked.connect(lambda _=False,s=section:self.navigate(s)); row.addWidget(button,1)
            if section == Section.NEWS: row.addWidget(self.news_badge,0,Qt.AlignmentFlag.AlignVCenter)
            self.nav_buttons[section]=button; self.nav_holders[section]=holder; side.addWidget(holder)
        side.addSpacing(8)

        self.side_status_card = QFrame(); self.side_status_card.setObjectName("sideStatusCard"); self.side_status_card.setMinimumHeight(164)
        status_lay = QVBoxLayout(self.side_status_card); status_lay.setContentsMargins(14,10,14,10); status_lay.setSpacing(6)
        self.side_status_title = QLabel("●   Sistema operacional"); self.side_status_title.setObjectName("sideStatusTitle"); status_lay.addWidget(self.side_status_title)
        local = QLabel("Dados locais · modo portátil"); local.setObjectName("sideStatusText"); status_lay.addWidget(local)
        self.side_proxy=QLabel(); self.side_proxy.setObjectName("sideStatusGood"); status_lay.addWidget(self.side_proxy)
        self.side_automation=QLabel(); self.side_automation.setObjectName("sideStatusGood"); status_lay.addWidget(self.side_automation)
        divider=QFrame(); divider.setFixedHeight(1); divider.setStyleSheet("background:#0a4568;border:0;"); status_lay.addWidget(divider)
        ver=QLabel("Windows Portable v4.0.2"); ver.setObjectName("sideStatusText"); status_lay.addWidget(ver); side.addWidget(self.side_status_card)
        ship=SidebarShipArt(); side.addWidget(ship)
        motto_row=QHBoxLayout(); gold=QLabel("━━"); gold.setStyleSheet("color:#ffc21a;font-weight:800;"); motto_row.addWidget(gold); motto=QLabel("INFORMAÇÃO\nEM DEFESA DO BRASIL"); motto.setObjectName("sideMotto"); motto_row.addWidget(motto,1); side.addLayout(motto_row); side.addStretch(1)
        outer.addWidget(self.sidebar)

        content = QWidget(); content.setObjectName("mainContent")
        self.content_layout = QVBoxLayout(content); self.content_layout.setContentsMargins(18, 8, 18, 0); self.content_layout.setSpacing(10)
        self.header_widget = RadarHeader(); self.content_layout.addWidget(self.header_widget)
        self.stack = QStackedWidget(); self.content_layout.addWidget(self.stack,1)
        self.pages = {
            Section.HOME: HomeDashboard(self.controller),
            Section.NEWS: NewsPage(self.controller),
            Section.VIDEOS: VideosPage(self.controller),
            Section.DEMANDS: DemandsPage(self.controller),
            Section.SOURCES: SourcesPage(self.controller),
            Section.HISTORY: HistoryPage(self.controller),
            Section.TERMS: TermsPage(self.controller),
            Section.STOP: StopPage(self.controller),
            Section.SETTINGS: SettingsPage(self.controller),
            Section.PDF_EDITOR: RefinedPdfEditorPage(self.paths.root),
            Section.EXTRACTOR: RefinedExtractorPage(self.paths.root),
            Section.VIDEO_EDITOR: VideoEditorPage(self.paths.root),
        }
        for section in SECTION_ORDER: self.stack.addWidget(self.pages[section])
        home=self.pages[Section.HOME]
        if isinstance(home,HomeDashboard): home.navigate.connect(lambda name:self.navigate(Section[name]))
        pdf_page=self.pages[Section.PDF_EDITOR]
        if isinstance(pdf_page,RefinedPdfEditorPage): pdf_page.back_requested.connect(lambda:self.navigate(Section.HOME))
        video_page=self.pages[Section.VIDEO_EDITOR]
        if isinstance(video_page,VideoEditorPage): video_page.back_requested.connect(lambda:self.navigate(Section.HOME))
        self.footer_widget=TechFooter(); self.content_layout.addWidget(self.footer_widget)
        outer.addWidget(content,1)

    def _build_tray(self) -> None:
        icon=self.windowIcon()
        if icon.isNull(): icon=self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray=QSystemTrayIcon(icon,self); self.tray.setToolTip("Monitor de Notícias")
        menu=QMenu(); open_action=menu.addAction("Abrir"); open_action.triggered.connect(self._restore); menu.addSeparator()
        news=menu.addAction("Buscar notícias agora"); news.triggered.connect(self.controller.search_news)
        videos=menu.addAction("Buscar vídeos agora"); videos.triggered.connect(self.controller.search_videos)
        demands=menu.addAction("Buscar demandas agora"); demands.triggered.connect(self.controller.search_all_demands)
        stop=menu.addAction("Parar buscas"); stop.triggered.connect(self.controller.stop_all_searches); menu.addSeparator()
        tools=menu.addMenu("Ferramentas"); pdf=tools.addAction("Editor de PDF"); pdf.triggered.connect(lambda:self.navigate(Section.PDF_EDITOR)); extractor=tools.addAction("Extrator de Vídeos"); extractor.triggered.connect(lambda:self.navigate(Section.EXTRACTOR)); video_editor=tools.addAction("Editor de Vídeo"); video_editor.triggered.connect(lambda:self.navigate(Section.VIDEO_EDITOR)); menu.addSeparator(); exit_action=menu.addAction("Sair"); exit_action.triggered.connect(self.exit_application)
        self.tray.setContextMenu(menu); self.tray.activated.connect(lambda reason:self._restore() if reason==QSystemTrayIcon.ActivationReason.Trigger else None)
        if QSystemTrayIcon.isSystemTrayAvailable(): self.tray.show()
        self.notifier=WindowsTrayNotifier(self.tray)

    def navigate(self, section: Section) -> None:
        keep_maximized = self.isMaximized() or bool(
            self.windowState() & Qt.WindowState.WindowMaximized
        )
        self._current=section; self.stack.setCurrentIndex(SECTION_ORDER.index(section))
        for sec,button in self.nav_buttons.items(): button.setChecked(sec==section)
        on_home=section==Section.HOME; self.header_widget.setVisible(not on_home); self.footer_widget.setVisible(not on_home)
        if on_home: self.content_layout.setContentsMargins(0,0,0,0); self.content_layout.setSpacing(0)
        else: self.content_layout.setContentsMargins(18,8,18,0); self.content_layout.setSpacing(10)
        for tool in TOOL_SECTIONS: self.nav_holders[tool].setVisible(not on_home)
        self.header_widget.set_section(section.value.label,section.value.subtitle)
        self.pages[section].refresh(self.controller.state)
        if keep_maximized:
            QTimer.singleShot(0, self._restore_maximized_after_navigation)

    def _restore_maximized_after_navigation(self) -> None:
        if self.isVisible() and not self.isMaximized():
            self.showMaximized()

    def _tick(self) -> None:
        self.controller.sync_automation_state(); self.pages[self._current].refresh(self.controller.state)
        state=self.controller.state; cfg=self.controller.proxy_config; auto=self.controller.automation_settings
        if self._current != Section.HOME: self.header_widget.update_runtime(self.controller)
        new_count=len(state.new_news_links); self.news_badge.setText(str(new_count)); self.news_badge.setVisible(new_count>0)
        busy=state.news_busy or state.video_busy
        self.side_status_title.setText("●   Busca em andamento" if busy else "●   Sistema operacional"); self.side_status_title.setStyleSheet("color:#ffffff;")
        self.side_proxy.setText(f"●   {cfg.status_label}"); self.side_proxy.setStyleSheet("color:#54e69d;" if "desativ" in cfg.status_label.lower() or "ok" in cfg.status_label.lower() else "color:#ffc21a;")
        self.side_automation.setText(f"●   Automação {'ativa' if auto.automatic_monitoring else 'pausada'}"); self.side_automation.setStyleSheet("color:#54e69d;" if auto.automatic_monitoring else "color:#ffc21a;")
        self.footer_widget.set_busy(busy)

    def _state_changed(self, _state) -> None: pass
    def _restore(self) -> None: self.show(); self.raise_(); self.activateWindow()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._allow_close: event.accept(); return
        event.ignore(); self.hide()

    def exit_application(self) -> None:
        extractor=self.pages.get(Section.EXTRACTOR)
        if isinstance(extractor,RefinedExtractorPage) and not extractor.shutdown(): self.footer_widget.status.setText("Aguardando o Extrator encerrar a operação ativa antes de sair."); self._restore(); return
        video_editor=self.pages.get(Section.VIDEO_EDITOR)
        if isinstance(video_editor,VideoEditorPage) and not video_editor.shutdown(): self.footer_widget.status.setText("Não foi possível fechar todas as janelas do Editor de Vídeo."); self._restore(); return
        self._allow_close=True; self._timer.stop(); self.controller.close(); self.tray.hide(); self.close()
