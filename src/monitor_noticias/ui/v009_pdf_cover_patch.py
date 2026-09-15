from __future__ import annotations

import logging
from pathlib import Path

log = logging.getLogger(__name__)
_INSTALLED = False


def install_v009_pdf_cover_patch() -> None:
    """Usa a capa MÍDIA IMPRESSA HD como padrão sem alterar o motor do PDF.

    A capa personalizada do usuário continua tendo prioridade. A correção apenas
    aponta o fallback HD já existente do modelo para o recurso 1245x2048
    empacotado em resources/pdf-default-cover.webp.
    """
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    from monitor_noticias.pdf_editor import PdfEditorModel

    original_init = PdfEditorModel.__init__

    def init(self, app_root):
        original_init(self, app_root)
        resource = Path(app_root) / "resources" / "pdf-default-cover.webp"
        if resource.is_file():
            self.hd_default_cover_file = resource

    PdfEditorModel.__init__ = init
