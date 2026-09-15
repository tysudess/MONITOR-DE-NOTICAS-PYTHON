from pathlib import Path


def test_v009_navigation_keeps_tool_buttons_visible_contract():
    text = Path("src/monitor_noticias/ui/main_window.py").read_text(encoding="utf-8")
    assert "self.nav_holders[tool].setVisible(True)" in text
    assert "Section.EXTRACTOR, Section.SHEET_AUTOMATION" in text


def test_v009_native_host_uses_win32_client_rect():
    text = Path("src/monitor_noticias/ui/external_win32_page.py").read_text(encoding="utf-8")
    assert "GetClientRect(parent_hwnd" in text
    assert "FRAMECHANGED" in text


def test_v009_video_editor_accepts_broadcast_formats():
    from monitor_noticias.video_editor.core import SUPPORTED_EXTENSIONS
    for ext in {".ts", ".mts", ".m2ts", ".mpg", ".mpeg", ".wmv", ".flv", ".mxf", ".vob"}:
        assert ext in SUPPORTED_EXTENSIONS


def test_v009_pdf_default_cover_is_preserved():
    path = Path("resources/pdf-default-cover.b64")
    assert path.is_file()
    assert path.stat().st_size > 10000


def test_v009_windows_executable_has_icon_asset():
    assert Path("resources/monitor-icon.svg").is_file()
    assert Path("resources/monitor-icon.ico").is_file()
    assert "monitor-icon.ico" in Path("MonitorDeNoticias.spec").read_text(encoding="utf-8")
