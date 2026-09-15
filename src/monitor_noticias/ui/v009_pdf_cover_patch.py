from __future__ import annotations

import logging
from pathlib import Path

log = logging.getLogger(__name__)
_INSTALLED = False


def install_v009_pdf_cover_patch() -> None:
    """Usa a capa MÍDIA IMPRESSA HD enviada pelo usuário como padrão.

    A capa continua respeitando a regra antiga: uma capa personalizada salva pelo
    usuário em data/capa_padrao_usuario.png tem prioridade. Este patch altera
    somente o recurso padrão empacotado.
    """
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    from monitor_noticias.pdf_editor import PdfEditorModel

    original_init = PdfEditorModel.__init__

    def init(self, app_root):
        original_init(self, app_root)
        parts_dir = Path(app_root) / "resources" / "pdf-cover-hd"
        parts = sorted(parts_dir.glob("part*.b64")) if parts_dir.is_dir() else []
        if not parts:
            return
        cache_dir = Path(app_root) / "data" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        assembled = cache_dir / "pdf-default-cover-hd.b64"
        try:
            expected = sum(part.stat().st_size for part in parts)
            if not assembled.is_file() or assembled.stat().st_size != expected:
                temp = assembled.with_suffix(".tmp")
                with temp.open("wb") as target:
                    for part in parts:
                        target.write(part.read_bytes())
                temp.replace(assembled)
            self._default_cover_resource = assembled
            self._default_cover_cache = None
        except Exception:
            log.exception("Falha ao montar capa padrão HD do Editor de PDF")

    PdfEditorModel.__init__ = init
