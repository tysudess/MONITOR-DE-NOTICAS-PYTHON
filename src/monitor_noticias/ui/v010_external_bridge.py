from __future__ import annotations

from pathlib import Path


def install_v010_external_bridge() -> None:
    from monitor_noticias.ui.external_win32_page import ExternalWin32AppPage

    if getattr(ExternalWin32AppPage, "_v010_file_bridge_patched", False):
        return

    previous = getattr(ExternalWin32AppPage, "set_url_and_paste", None)

    def set_url_and_paste(self, url: str) -> None:
        value = str(url or "").strip()
        if not value:
            return
        # O executável Electron v0.0.10 monitora este arquivo no próprio
        # diretório. Escrever de forma atômica evita leitura parcial.
        try:
            target = Path(self.executable).parent / "monitor-url.txt"
            temp = target.with_suffix(".tmp")
            temp.write_text(value, encoding="utf-8")
            temp.replace(target)
            self.status.setText("● Link enviado ao Extrator de Notícias")
        except Exception:
            # Mantém o fallback Win32/clipboard instalado no runtime v0.0.10.
            pass
        if callable(previous):
            previous(self, value)
        elif self._process is None:
            self.start()

    ExternalWin32AppPage.set_url_and_paste = set_url_and_paste
    ExternalWin32AppPage._v010_file_bridge_patched = True
