from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from monitor_noticias.app.preferences import SharedPreferences
from monitor_noticias.automation.settings import AutomationSettings
from monitor_noticias.ui.refined_settings import SettingsPage


class _Controller:
    def __init__(self, root: Path) -> None:
        self.prefs = SharedPreferences(root / "prefs.properties")
        self._automation = AutomationSettings(self.prefs)
        self._proxy = SimpleNamespace(
            enabled=False,
            host="",
            port=8080,
            username="",
            status_label="Proxy desativado",
        )
        self.start_with_windows = False
        self.refresh_count = 0

    @property
    def automation_settings(self):
        return self._automation

    @property
    def proxy_config(self):
        return self._proxy

    def refresh(self) -> None:
        self.refresh_count += 1

    def save_proxy(self, enabled, host, port, username, password):
        self._proxy = SimpleNamespace(
            enabled=bool(enabled),
            host=str(host),
            port=int(port),
            username=str(username),
            status_label="Proxy ativo" if enabled else "Proxy desativado",
        )
        return self._proxy

    def test_proxy(self):
        return True, "ok"

    def set_start_with_windows(self, enabled: bool) -> bool:
        self.start_with_windows = bool(enabled)
        return True


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_refresh_does_not_erase_pending_automation_edit(tmp_path: Path) -> None:
    _app()
    controller = _Controller(tmp_path)
    page = SettingsPage(controller)
    page.refresh(None)

    combo = page.news_block.interval
    assert combo is not None
    index = combo.findData("45")
    assert index >= 0
    combo.setCurrentIndex(index)
    assert page._automation_dirty is True

    # Simula o refresh periódico do MainWindow enquanto o usuário ainda edita.
    page.refresh(None)
    assert combo.currentData() == "45"


def test_apply_automation_persists_intervals_and_video_times(tmp_path: Path) -> None:
    _app()
    controller = _Controller(tmp_path)
    page = SettingsPage(controller)
    page.refresh(None)

    news = page.news_block.interval
    demands = page.dem_block.interval
    assert news is not None and demands is not None
    news.setCurrentIndex(news.findData("45"))
    demands.setCurrentIndex(demands.findData("120"))
    page.video_times.setText("07:15, 18:45")
    page.video_block.toggle.setChecked(True)
    page._apply_auto()

    settings = AutomationSettings(controller.prefs)
    assert settings.news_interval_minutes == 45
    assert settings.demand_interval_minutes == 120
    assert settings.video_schedule_times == {"07:15", "18:45"}
    assert controller.refresh_count == 1
