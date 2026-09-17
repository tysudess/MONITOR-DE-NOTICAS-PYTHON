from __future__ import annotations

"""Ajusta a Home v0.0.19 à imagem-verdade aprovada pelo usuário.

Não desenha dados, máscaras ou painéis adicionais. Apenas informa à camada de
imagem-verdade as dimensões/corte corretos e mantém o shell funcional alinhado
à referência visual 1755x896.
"""

_INSTALLED = False


def install_v019_home_user_truth() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    from monitor_noticias.ui import v019_exact_reference as ref

    # Imagem integral aprovada: 1755x896. O conteúdo útil começa depois da
    # sidebar de 250 px e da topbar de 90 px.
    ref.REF_FULL_W = 1755.0
    ref.REF_FULL_H = 896.0
    ref.REF_SIDE_W = 250.0
    ref.REF_TOP_H = 90.0
    ref.REF_CONTENT_W = ref.REF_FULL_W - ref.REF_SIDE_W
    ref.REF_CONTENT_H = ref.REF_FULL_H - ref.REF_TOP_H

    # Hotspots dos cards relativos apenas à área de conteúdo recortada.
    ref.HomeTruthSurface.CARD_RECTS = (
        (14, 160, 151, 142, "NEWS"),
        (173, 160, 143, 142, "VIDEOS"),
        (326, 160, 144, 142, "DEMANDS"),
        (481, 160, 144, 142, "SOURCES"),
        (637, 160, 145, 142, "TERMS"),
        (793, 160, 139, 142, "COVERS"),
        (944, 160, 149, 142, "PDF_EDITOR"),
        (1105, 160, 181, 142, "EXTRACTOR"),
        (1298, 160, 164, 142, "VIDEO_EDITOR"),
    )

    old_sidebar = ref._arrange_global_sidebar
    old_topbar = ref._style_global_topbar

    def arrange_sidebar(window) -> None:
        old_sidebar(window)
        sidebar = getattr(window, "sidebar", None)
        if sidebar is not None:
            sidebar.setFixedWidth(250)

    def style_topbar(window) -> None:
        old_topbar(window)
        top = getattr(window, "reference_top_bar", None)
        if top is not None:
            top.setFixedHeight(90)

    ref._arrange_global_sidebar = arrange_sidebar
    ref._style_global_topbar = style_topbar
