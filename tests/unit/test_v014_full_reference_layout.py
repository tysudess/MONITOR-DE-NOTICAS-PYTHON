from __future__ import annotations

from pathlib import Path


def test_v014_is_installed_after_preserved_overlays():
    run = Path("run.py").read_text(encoding="utf-8")
    assert run.index("install_v013_sidebar_reference()") < run.index("install_v014_full_reference_layout()")


def test_v014_is_visual_shell_only():
    source = Path("src/monitor_noticias/ui/v014_full_reference_layout.py").read_text(encoding="utf-8")
    assert "old_build(self)" in source
    assert "old_nav(self, section)" in source
    assert "old_tick(self)" in source
    for forbidden in ("ffmpeg", "ffprobe", "yt_dlp", "sqlite", "requests.get", "subprocess"):
        assert forbidden not in source.lower()


def test_v014_matches_reference_shell_contract():
    source = Path("src/monitor_noticias/ui/v014_full_reference_layout.py").read_text(encoding="utf-8")
    for token in ("#031525", "#00B7FF", "#00E5FF", "#FFC400", "referenceTopBar"):
        assert token in source
    assert "sidebar.setFixedWidth(220)" in source
    assert "border-left:5px solid #00E5FF" in source
    assert "Brasília - DF" in source


def test_global_search_reuses_existing_query_widgets():
    source = Path("src/monitor_noticias/ui/v014_full_reference_layout.py").read_text(encoding="utf-8")
    assert "pages.get(target)" in source
    assert "query.setText(text)" in source
    assert "self.window.navigate(target)" in source
    assert "search_news(" not in source
    assert "search_videos(" not in source
