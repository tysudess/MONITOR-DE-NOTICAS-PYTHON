from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Esperava 1 ocorrência em {path}, encontrei {count}: {old[:80]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_main_window() -> None:
    old = '''        on_home=section==Section.HOME; self.header_widget.setVisible(not on_home); self.footer_widget.setVisible(not on_home)\n        if on_home: self.content_layout.setContentsMargins(0,0,0,0); self.content_layout.setSpacing(0)\n        else: self.content_layout.setContentsMargins(18,8,18,0); self.content_layout.setSpacing(10)\n        for tool in TOOL_SECTIONS: self.nav_holders[tool].setVisible(not on_home)\n'''
    new = '''        full_workspace = section in {Section.HOME, Section.EXTRACTOR, Section.SHEET_AUTOMATION}\n        self.header_widget.setVisible(not full_workspace); self.footer_widget.setVisible(not full_workspace)\n        if full_workspace: self.content_layout.setContentsMargins(0,0,0,0); self.content_layout.setSpacing(0)\n        else: self.content_layout.setContentsMargins(18,8,18,0); self.content_layout.setSpacing(10)\n        # As ferramentas devem existir e permanecer visíveis desde a primeira pintura.\n        # A release anterior as ocultava no HOME e só as mostrava após a primeira navegação.\n        for tool in TOOL_SECTIONS: self.nav_holders[tool].setVisible(True)\n'''
    replace_once("src/monitor_noticias/ui/main_window.py", old, new)


def patch_native_host() -> None:
    old = '''            host_w = max(1, self.width())\n            host_h = max(1, self.height())\n            flags = 0x0004 | 0x0010 | 0x0040  # NOZORDER | NOACTIVATE | SHOWWINDOW\n\n            # Primeiro oferecemos toda a área disponível ao aplicativo original.\n            # Alguns programas Electron/Qt possuem tamanho mínimo ou máximo próprio\n            # e podem rejeitar parte desse resize. Nesse caso não forçamos o motor:\n            # apenas centralizamos a janela real dentro da área do Monitor.\n            user32.SetWindowPos(hwnd, 0, 0, 0, host_w, host_h, flags)\n\n            rect = wintypes.RECT()\n            if user32.GetWindowRect(hwnd, ctypes.byref(rect)):\n                child_w = max(1, int(rect.right - rect.left))\n                child_h = max(1, int(rect.bottom - rect.top))\n                visible_w = min(host_w, child_w)\n                visible_h = min(host_h, child_h)\n                x = max(0, (host_w - visible_w) // 2)\n                y = max(0, (host_h - visible_h) // 2)\n                if child_w != host_w or child_h != host_h or x or y:\n                    user32.SetWindowPos(hwnd, 0, x, y, child_w, child_h, flags)\n'''
    new = '''            # winId()/GetClientRect trabalham no mesmo sistema de coordenadas Win32.\n            # self.width()/height() são pixels lógicos do Qt e causavam folgas/cortes\n            # quando o Windows estava em 125%, 150% ou outra escala de DPI.\n            parent_hwnd = int(self.winId())\n            client = wintypes.RECT()\n            if user32.GetClientRect(parent_hwnd, ctypes.byref(client)):\n                host_w = max(1, int(client.right - client.left))\n                host_h = max(1, int(client.bottom - client.top))\n            else:\n                host_w = max(1, self.width())\n                host_h = max(1, self.height())\n            flags = 0x0004 | 0x0010 | 0x0040 | 0x0020  # NOZORDER | NOACTIVATE | SHOWWINDOW | FRAMECHANGED\n            user32.SetWindowPos(hwnd, 0, 0, 0, host_w, host_h, flags)\n'''
    replace_once("src/monitor_noticias/ui/external_win32_page.py", old, new)


def patch_video_editor() -> None:
    replace_once(
        "src/monitor_noticias/video_editor/core.py",
        'SUPPORTED_EXTENSIONS = {".mp4", ".mkv", ".webm", ".mov", ".avi", ".m4v"}',
        'SUPPORTED_EXTENSIONS = {".3gp", ".avi", ".flv", ".m2ts", ".m4v", ".mkv", ".mov", ".mp4", ".mpeg", ".mpg", ".mts", ".mxf", ".ogv", ".ts", ".vob", ".webm", ".wmv"}',
    )
    replace_once(
        "src/monitor_noticias/video_editor/window.py",
        '        files, _ = QFileDialog.getOpenFileNames(self, "Abrir vídeos", str(Path.home()), "Vídeos (*.mp4 *.mkv *.webm *.mov *.avi *.m4v)")\n',
        '        patterns = " ".join(f"*{ext}" for ext in sorted(SUPPORTED_EXTENSIONS))\n        files, _ = QFileDialog.getOpenFileNames(self, "Abrir vídeos", str(Path.home()), f"Vídeos ({patterns});;Todos os arquivos (*.*)")\n',
    )


def patch_extractor_resilience() -> None:
    old = '''        except Exception as exc:\n            self.failed.emit(str(exc) or "Falha no download.")\n\n\nclass _UpdaterWorker'''
    new = '''        except BaseException as exc:\n            # yt-dlp/FFmpeg e seus auxiliares não podem encerrar o processo principal.\n            # Até SystemExit originado por dependência é convertido em erro da operação.\n            self.failed.emit(str(exc) or f"Falha no download ({type(exc).__name__}).")\n\n\nclass _UpdaterWorker'''
    replace_once("src/monitor_noticias/ui/extractor_page.py", old, new)


def patch_icon() -> None:
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#041d31"/><stop offset="1" stop-color="#0b4c78"/></linearGradient><linearGradient id="gold" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#ffd064"/><stop offset="1" stop-color="#f4a81d"/></linearGradient></defs>
<rect x="18" y="18" width="476" height="476" rx="108" fill="url(#bg)"/>
<circle cx="256" cy="256" r="154" fill="none" stroke="#1da4d8" stroke-width="18" opacity=".35"/>
<circle cx="256" cy="256" r="104" fill="none" stroke="#1da4d8" stroke-width="14" opacity=".55"/>
<path d="M256 256 L405 205 A158 158 0 0 1 413 240 Z" fill="#39c5f0" opacity=".82"/>
<circle cx="256" cy="256" r="25" fill="#39c5f0"/>
<circle cx="365" cy="158" r="18" fill="#ffbf3e"/>
<rect x="116" y="280" width="280" height="142" rx="22" fill="url(#gold)"/>
<rect x="142" y="307" width="90" height="86" rx="12" fill="#f7fbff"/>
<rect x="253" y="309" width="113" height="16" rx="8" fill="#08385c"/>
<rect x="253" y="342" width="113" height="16" rx="8" fill="#0a5f91"/>
<rect x="253" y="375" width="82" height="16" rx="8" fill="#0a5f91"/>
</svg>\n'''
    (ROOT / "resources/monitor-icon.svg").write_text(svg, encoding="utf-8")

    from PIL import Image, ImageDraw
    scale = 4
    size = 256 * scale
    im = Image.new("RGB", (size, size), "#05243a")
    d = ImageDraw.Draw(im)
    def box(v): return tuple(int(x * scale) for x in v)
    d.rounded_rectangle(box((9, 9, 247, 247)), radius=54*scale, fill="#073a5e")
    for r, width in ((77, 9), (52, 7)):
        d.ellipse(box((128-r,128-r,128+r,128+r)), outline="#219dcd", width=width*scale)
    d.pieslice(box((50,50,206,206)), start=340, end=358, fill="#3cc5ed")
    d.ellipse(box((116,116,140,140)), fill="#3cc5ed")
    d.ellipse(box((174,70,192,88)), fill="#ffc24b")
    d.rounded_rectangle(box((58,140,198,211)), radius=12*scale, fill="#f6b534")
    d.rounded_rectangle(box((71,154,116,197)), radius=6*scale, fill="#f7fbff")
    for y, x2 in ((155,183),(171,183),(187,168)):
        d.rounded_rectangle(box((126,y,x2,y+8)), radius=4*scale, fill="#08385c")
    im = im.resize((256,256), Image.Resampling.LANCZOS)
    im.save(ROOT / "resources/monitor-icon.ico", format="ICO", sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])

    spec = ROOT / "MonitorDeNoticias.spec"
    text = spec.read_text(encoding="utf-8")
    needle = '    entitlements_file=None,\n)\n\ncoll = COLLECT('
    replacement = '    entitlements_file=None,\n    icon="resources/monitor-icon.ico",\n)\n\ncoll = COLLECT('
    if needle not in text:
        raise RuntimeError("Ponto de inclusão do ícone não encontrado no spec")
    spec.write_text(text.replace(needle, replacement, 1), encoding="utf-8")


def add_regression_tests() -> None:
    test = '''from pathlib import Path\n\n\ndef test_v009_navigation_keeps_tool_buttons_visible_contract():\n    text = Path("src/monitor_noticias/ui/main_window.py").read_text(encoding="utf-8")\n    assert "self.nav_holders[tool].setVisible(True)" in text\n    assert "Section.EXTRACTOR, Section.SHEET_AUTOMATION" in text\n\n\ndef test_v009_native_host_uses_win32_client_rect():\n    text = Path("src/monitor_noticias/ui/external_win32_page.py").read_text(encoding="utf-8")\n    assert "GetClientRect(parent_hwnd" in text\n    assert "FRAMECHANGED" in text\n\n\ndef test_v009_video_editor_accepts_broadcast_formats():\n    from monitor_noticias.video_editor.core import SUPPORTED_EXTENSIONS\n    for ext in {".ts", ".mts", ".m2ts", ".mpg", ".mpeg", ".wmv", ".flv", ".mxf", ".vob"}:\n        assert ext in SUPPORTED_EXTENSIONS\n\n\ndef test_v009_pdf_default_cover_is_preserved():\n    path = Path("resources/pdf-default-cover.b64")\n    assert path.is_file()\n    assert path.stat().st_size > 10000\n\n\ndef test_v009_windows_executable_has_icon_asset():\n    assert Path("resources/monitor-icon.svg").is_file()\n    assert Path("resources/monitor-icon.ico").is_file()\n    assert "monitor-icon.ico" in Path("MonitorDeNoticias.spec").read_text(encoding="utf-8")\n'''
    (ROOT / "tests/unit/test_v009_corrections.py").write_text(test, encoding="utf-8")


def main() -> None:
    patch_main_window()
    patch_native_host()
    patch_video_editor()
    patch_extractor_resilience()
    patch_icon()
    add_regression_tests()
    print("V009_CORRECTIONS_APPLIED=YES")


if __name__ == "__main__":
    main()
