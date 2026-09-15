from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]


def test_default_pdf_cover_is_valid_high_resolution_png():
    cover = ROOT / "resources" / "pdf-default-cover.png"
    assert cover.is_file()
    with Image.open(cover) as image:
        image.load()
        assert image.format == "PNG"
        assert image.width >= 1000
        assert image.height >= 1000
    assert not (ROOT / "resources" / "pdf-default-cover.webp").exists()


def test_v011_pdf_patch_serializes_ui_rendering_and_uses_png():
    text = (ROOT / "src/monitor_noticias/ui/v011_pdf_stability.py").read_text(encoding="utf-8")
    assert 'pdf-default-cover.png' in text
    assert 'PdfEditorPage._run_image_worker = run_image_sync' in text
    assert 'PdfEditorPage._refresh_all = refresh_all_sync' in text
    assert 'PdfEditorPage._export = export_sync' in text
    assert 'except BaseException as exc' in text


def test_v011_sidebar_matches_reference_structure():
    text = (ROOT / "src/monitor_noticias/ui/v011_sidebar_fidelity.py").read_text(encoding="utf-8")
    for group in ("PRINCIPAL", "GERENCIAMENTO", "FERRAMENTAS", "SISTEMA"):
        assert group in text
    assert 'border-left:6px solid #ffc400' in text
    assert 'Busca em andamento' in text
    assert 'Windows Portable v4.0.2' in text
    assert 'self.sidebar.setFixedWidth(318)' in text
