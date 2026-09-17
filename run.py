from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

if "--extractor-worker" in sys.argv:
    from monitor_noticias.extractor_worker_process import main as extractor_worker_main

    args = [arg for arg in sys.argv[1:] if arg != "--extractor-worker"]
    raise SystemExit(extractor_worker_main(args))

from monitor_noticias.ui.v009_runtime_fixes import install_v009_runtime_fixes
from monitor_noticias.ui.v009_pdf_cover_patch import install_v009_pdf_cover_patch
from monitor_noticias.ui.v010_runtime_fixes import install_v010_runtime_fixes
from monitor_noticias.ui.v010_external_bridge import install_v010_external_bridge
from monitor_noticias.ui.v010_video_boundary import install_v010_video_boundary_fix
from monitor_noticias.ui.v011_pdf_stability import install_v011_pdf_stability
from monitor_noticias.ui.v011_sidebar_fidelity import install_v011_sidebar_fidelity
from monitor_noticias.ui.v012_runtime_fixes import install_v012_runtime_fixes
from monitor_noticias.ui.v013_sidebar_reference import install_v013_sidebar_reference
from monitor_noticias.ui.v014_full_reference_layout import install_v014_full_reference_layout
from monitor_noticias.ui.v014_reference_sidebar_local import install_v014_reference_sidebar_local
from monitor_noticias.ui.v015_shell_reference import install_v015_shell_reference
from monitor_noticias.ui.v016_layout_only import install_v016_layout_only
from monitor_noticias.ui.v017_home_truth import install_v017_home_truth
from monitor_noticias.ui.v017_home_truth_refine import install_v017_home_truth_refine
from monitor_noticias.ui.v017_home_truth_precision import install_v017_home_truth_precision
from monitor_noticias.ui.v018_home_visual_fidelity import install_v018_home_visual_fidelity
from monitor_noticias.ui.v019_exact_reference import install_v019_exact_reference
from monitor_noticias.ui.v019_asset_fix import install_v019_asset_fix
from monitor_noticias.ui.v019_home_user_truth import install_v019_home_user_truth
from monitor_noticias.ui.v019_news_reference import install_v019_news_reference
from monitor_noticias.ui.v019_news_scroll_fix import install_v019_news_scroll_fix

install_v009_runtime_fixes()
install_v009_pdf_cover_patch()
install_v010_runtime_fixes()
install_v010_external_bridge()
install_v010_video_boundary_fix()
install_v011_pdf_stability()
install_v011_sidebar_fidelity()
# v0.0.12
install_v012_runtime_fixes()
install_v013_sidebar_reference()
install_v014_full_reference_layout()
install_v014_reference_sidebar_local()
# v0.0.16: as imagens comandam apenas a aparencia.
# Nao substituir paginas, nao esconder secoes, nao trocar callbacks.
install_v015_shell_reference()
install_v016_layout_only()
# v0.0.17-home: somente a aba Inicio e reconstruida visualmente.
# Motor, controller, rotas e paginas dos demais modulos permanecem intactos.
install_v017_home_truth()
install_v017_home_truth_refine()
install_v017_home_truth_precision()
# v0.0.18-home: refino de brilho, contraste e fidelidade visual somente da Home/shell.
install_v018_home_visual_fidelity()
# v0.0.19: imagem-verdade literal na Home e sidebar/topbar globais invariantes.
install_v019_exact_reference()
# O ativo aprovado pelo usuario e remontado byte-a-byte e validado antes da exibicao.
install_v019_asset_fix()
# Ajusta corte, sidebar, topbar e hotspots à nova imagem-verdade 1755x896.
install_v019_home_user_truth()
# O antigo overlay de métricas permanece deliberadamente desativado: ele causava
# blocos e números sobrepostos à arte. Os dados serão reintroduzidos depois em
# âncoras pequenas e transparentes sobre esta imagem já validada.
# Aba Notícias fiel à referência visual, mantendo o motor e os callbacks existentes.
install_v019_news_reference()
# A lista mostra 25 resultados por página com rolagem vertical própria.
install_v019_news_scroll_fix()

from monitor_noticias.app.application import main

if __name__ == "__main__":
    raise SystemExit(main())
