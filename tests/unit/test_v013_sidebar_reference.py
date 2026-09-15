from __future__ import annotations

from pathlib import Path


def test_v013_overlay_is_last_and_visual_only():
    run = Path("run.py").read_text(encoding="utf-8")
    assert run.index("install_v012_runtime_fixes()") < run.index("install_v013_sidebar_reference()")
    source = Path("src/monitor_noticias/ui/v013_sidebar_reference.py").read_text(encoding="utf-8")
    assert "MainWindow._build_ui=build" in source
    assert "MainWindow.navigate=navigate" in source
    assert "MainWindow._tick=tick" in source
    for forbidden in ("database", "collectors", "ffmpeg", "ffprobe", "yt_dlp", "stop_all_searches"):
        assert forbidden not in source.lower()


def test_v013_reference_palette_and_navigation_style():
    source = Path("src/monitor_noticias/ui/v013_sidebar_reference.py").read_text(encoding="utf-8")
    for token in ("#FAC305", "#EDB707", "#164A6E", "#EAEDF1", "#02192D"):
        assert token in source
    assert "border-left:7px solid #FAC305" in source
    assert "QPushButton#navButton:checked" in source
    assert "border:2px solid #EDB707" in source
    assert "QScrollBar:vertical" in source


def test_v013_status_card_reuses_live_labels():
    source = Path("src/monitor_noticias/ui/v013_sidebar_reference.py").read_text(encoding="utf-8")
    assert "window.side_status_title" in source
    assert "window.side_proxy" in source
    assert "window.side_automation" in source
    assert "old_tick(self)" in source
    assert "Windows Portable" in source
