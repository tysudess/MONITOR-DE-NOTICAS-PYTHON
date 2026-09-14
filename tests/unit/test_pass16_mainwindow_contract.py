from pathlib import Path


def test_main_window_source_coordinates_tool_shutdown():
    source = (Path(__file__).resolve().parents[2] / "src" / "monitor_noticias" / "ui" / "main_window.py").read_text(encoding="utf-8")
    assert "extractor.shutdown()" in source
    assert 'getattr(page, "shutdown", None)' in source
    assert "Section.VIDEO_EDITOR" in source
    assert "Section.NEWS_EXTRACTOR" in source
    assert "Section.SHEET_AUTOMATION" in source
    assert "Section.COVERS" in source
    assert source.index("extractor.shutdown()") < source.index("self.controller.close()")
    assert source.index('getattr(page, "shutdown", None)') < source.index("self.controller.close()")
