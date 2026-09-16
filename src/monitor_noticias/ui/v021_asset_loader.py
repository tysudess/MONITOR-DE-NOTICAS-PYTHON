from __future__ import annotations

"""Loader determinístico dos ativos v0.0.21.

O Qt do runner Windows pode não expor o plugin WebP. Como Pillow já é dependência
fixa do programa, decodificamos o mesmo arquivo WebP por Pillow e entregamos um
QPixmap sem alterar o ativo nem a composição visual.
"""

from PIL import Image
from PySide6.QtGui import QImage, QPixmap

_INSTALLED = False


def install_v021_asset_loader() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    from monitor_noticias.ui import v021_literal_tabs as mod

    cache: dict[str, QPixmap] = {}

    def load(name: str) -> QPixmap:
        cached = cache.get(name)
        if cached is not None and not cached.isNull():
            return cached
        path = mod._resource_root() / "ui" / "v021" / f"{name}-page-q90.webp"
        if not path.is_file():
            raise RuntimeError(f"Imagem-verdade v0.0.21 ausente: {path}")
        with Image.open(path) as image:
            rgba = image.convert("RGBA")
            if rgba.size != (1447, 855):
                raise RuntimeError(f"Dimensão da imagem-verdade divergente: {path} = {rgba.size}")
            raw = rgba.tobytes("raw", "RGBA")
            qimg = QImage(raw, rgba.width, rgba.height, rgba.width * 4, QImage.Format.Format_RGBA8888).copy()
        pix = QPixmap.fromImage(qimg)
        if pix.isNull():
            raise RuntimeError(f"Imagem-verdade v0.0.21 não pôde ser convertida: {path}")
        cache[name] = pix
        return pix

    mod._pix = load
