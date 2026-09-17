from __future__ import annotations

"""Loader determinístico e íntegro dos ativos visuais v0.0.21.

Os ativos são armazenados como fragmentos Base64 de texto para evitar qualquer
truncamento do transporte binário. A imagem só é aceita quando quantidade de
fragmentos, tamanho e SHA-256 batem exatamente com o ativo aprovado.
"""

import base64
import hashlib
from io import BytesIO

from PIL import Image
from PySide6.QtGui import QImage, QPixmap

_INSTALLED = False

META = {
    "noticias": (60060, "6b591934b3abd1d926ad80ca8e19b3c2729d5387f2195c320bdd972a87f7a330", 3),
    "fontes": (51696, "1b415b75282136b9fe90f6c0053b607e1fb7d0452547248f46fa1f37cb363956", 2),
    "termos": (47636, "01f7e28ae0ffbcc4862a3e91b844a1f6a4603c2a9002f2f2f1f6c5035cc3fdeb", 2),
}


def _decode_asset(root, name: str) -> bytes:
    expected_size, expected_sha, expected_parts = META[name]
    encoded = root / "ui" / "v021" / "encoded"
    parts = sorted(encoded.glob(f"{name}.part*.b64"))
    if len(parts) != expected_parts:
        raise RuntimeError(
            f"Ativo v0.0.21 {name}: esperado(s) {expected_parts} fragmento(s), encontrado(s) {len(parts)}"
        )
    expected_names = [f"{name}.part{i:02d}.b64" for i in range(expected_parts)]
    if [p.name for p in parts] != expected_names:
        raise RuntimeError(f"Ativo v0.0.21 {name}: sequência de fragmentos inválida")
    try:
        payload = "".join(p.read_text(encoding="ascii").strip() for p in parts)
        data = base64.b64decode(payload, validate=True)
    except Exception as exc:
        raise RuntimeError(f"Ativo v0.0.21 {name}: Base64 inválido") from exc
    actual_sha = hashlib.sha256(data).hexdigest()
    if len(data) != expected_size or actual_sha != expected_sha:
        raise RuntimeError(
            f"Ativo v0.0.21 {name}: integridade divergente "
            f"(size={len(data)}, sha256={actual_sha})"
        )
    return data


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
        if name not in META:
            raise RuntimeError(f"Ativo v0.0.21 desconhecido: {name}")
        data = _decode_asset(mod._resource_root(), name)
        try:
            with Image.open(BytesIO(data)) as image:
                image.load()
                rgba = image.convert("RGBA")
                if rgba.size != (1447, 855):
                    raise RuntimeError(
                        f"Dimensão da imagem-verdade divergente: {name} = {rgba.size}"
                    )
                raw = rgba.tobytes("raw", "RGBA")
                qimg = QImage(
                    raw,
                    rgba.width,
                    rgba.height,
                    rgba.width * 4,
                    QImage.Format.Format_RGBA8888,
                ).copy()
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(f"Imagem-verdade v0.0.21 {name} não pôde ser decodificada") from exc
        pix = QPixmap.fromImage(qimg)
        if pix.isNull():
            raise RuntimeError(f"Imagem-verdade v0.0.21 {name} não pôde ser convertida para QPixmap")
        cache[name] = pix
        return pix

    mod._pix = load
