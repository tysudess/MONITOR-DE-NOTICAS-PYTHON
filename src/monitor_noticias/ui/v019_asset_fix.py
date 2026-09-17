from __future__ import annotations

"""Carregamento validado da imagem-verdade da Home v0.0.19.

A Home usa a referencia aprovada pelo usuario como superficie visual. O ativo e
remontado de fragmentos Base64 versionados para continuar compativel com o
portable e e validado integralmente por tamanho, SHA-256 e dimensoes.
"""

import base64
import hashlib

from PySide6.QtGui import QPixmap

EXPECTED_SIZE = 90006
EXPECTED_SHA256 = "0fc9a6fe741315ff1859374e84670c3b1017004ed6218ed8f5d8cc027b7351ff"
EXPECTED_WIDTH = 1755
EXPECTED_HEIGHT = 896
PART_COUNT = 14
_INSTALLED = False

# Um unico caractere foi acrescentado ao part07 durante o transporte textual
# para o repositorio. A correcao abaixo e deliberadamente especifica; o SHA-256
# da imagem inteira continua sendo a fonte de verdade e impede qualquer outra
# divergencia de passar silenciosamente.
_TRANSPORT_TYPO = "1fe4111j1X5cU2"
_TRANSPORT_FIXED = "1fe411j1X5cU2"


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

        parts_dir = ref._resource_root() / "ui" / "v019" / "home-user"
        parts = [parts_dir / f"part{i:02d}.b64" for i in range(PART_COUNT)]
        missing = [str(path) for path in parts if not path.is_file()]
        if missing:
            raise RuntimeError(
                "Imagem-verdade da Home v0.0.19 incompleta; fragmentos ausentes: "
                + ", ".join(missing)
            )

        encoded = "".join(path.read_text(encoding="ascii").strip() for path in parts)
        if _TRANSPORT_TYPO in encoded:
            encoded = encoded.replace(_TRANSPORT_TYPO, _TRANSPORT_FIXED, 1)

        try:
            raw = base64.b64decode(encoded, validate=True)
        except Exception as exc:
            raise RuntimeError("Imagem-verdade da Home v0.0.19 possui Base64 invalido") from exc

        if len(raw) != EXPECTED_SIZE:
            raise RuntimeError(
                f"Imagem-verdade da Home v0.0.19 com tamanho divergente: {len(raw)}; "
                f"esperado {EXPECTED_SIZE}"
            )
        digest = hashlib.sha256(raw).hexdigest()
        if digest != EXPECTED_SHA256:
            raise RuntimeError(
                f"Imagem-verdade da Home v0.0.19 com SHA-256 divergente: {digest}"
            )

        pixmap = QPixmap()
        if not pixmap.loadFromData(raw, "WEBP"):
            raise RuntimeError("Imagem-verdade da Home v0.0.19 nao pode ser decodificada como WEBP")
        if pixmap.width() != EXPECTED_WIDTH or pixmap.height() != EXPECTED_HEIGHT:
            raise RuntimeError(
                f"Imagem-verdade da Home v0.0.19 com dimensoes divergentes: "
                f"{pixmap.width()}x{pixmap.height()}"
            )

        cache = pixmap
        return cache

    ref._home_pixmap = load_truth_pixmap
