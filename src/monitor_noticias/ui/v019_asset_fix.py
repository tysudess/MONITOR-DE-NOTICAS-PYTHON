from __future__ import annotations

"""Carregamento validado do ativo visual integral da Home v0.0.19.

Nao altera controller, rotas, callbacks ou motores. Apenas substitui o loader
visual da camada v0.0.19 para remontar a imagem-verdade a partir dos fragmentos
Base64 versionados no repositorio e validar tamanho/SHA-256 antes de exibir.
"""

import base64
import hashlib

from PySide6.QtGui import QPixmap

EXPECTED_SIZE = 180128
EXPECTED_SHA256 = "eea22fed79290a01a5fff991147edf41a139c9c5cf020c886069152c9da39201"
PART_COUNT = 14
_INSTALLED = False


def install_v019_asset_fix() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    from monitor_noticias.ui import v019_exact_reference as ref

    cache: QPixmap | None = None

    def load_truth_pixmap() -> QPixmap:
        nonlocal cache
        if cache is not None and not cache.isNull():
            return cache

        parts_dir = ref._resource_root() / "ui" / "v019" / "home-full-q90"
        parts = [parts_dir / f"part{i:02d}.b64" for i in range(PART_COUNT)]
        missing = [str(path) for path in parts if not path.is_file()]
        if missing:
            raise RuntimeError(
                "Imagem-verdade v0.0.19 incompleta; fragmentos ausentes: "
                + ", ".join(missing)
            )

        encoded = "".join(path.read_text(encoding="ascii").strip() for path in parts)
        try:
            raw = base64.b64decode(encoded, validate=True)
        except Exception as exc:
            raise RuntimeError("Imagem-verdade v0.0.19 possui Base64 invalido") from exc

        if len(raw) != EXPECTED_SIZE:
            raise RuntimeError(
                f"Imagem-verdade v0.0.19 com tamanho divergente: {len(raw)}; "
                f"esperado {EXPECTED_SIZE}"
            )
        digest = hashlib.sha256(raw).hexdigest()
        if digest != EXPECTED_SHA256:
            raise RuntimeError(
                f"Imagem-verdade v0.0.19 com SHA-256 divergente: {digest}"
            )

        pixmap = QPixmap()
        if not pixmap.loadFromData(raw, "WEBP"):
            raise RuntimeError("Imagem-verdade integral v0.0.19 nao pode ser decodificada como WEBP")
        if pixmap.width() != 1672 or pixmap.height() != 941:
            raise RuntimeError(
                f"Imagem-verdade v0.0.19 com dimensoes divergentes: "
                f"{pixmap.width()}x{pixmap.height()}"
            )

        cache = pixmap
        return cache

    ref._home_pixmap = load_truth_pixmap
