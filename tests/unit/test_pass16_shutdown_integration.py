from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from monitor_noticias.ui.video_editor_page import VideoEditorPage


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_video_editor_page_shutdown_stops_and_closes_tracked_windows(tmp_path: Path):
    _app()
    page = VideoEditorPage(tmp_path)
    page.open_editor()
    assert page._windows
    window = page._windows[0]
    window.show()
    assert window.isVisible()

    assert page.shutdown() is True
    assert not window.isVisible()
