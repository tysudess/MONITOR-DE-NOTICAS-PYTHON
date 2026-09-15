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
from monitor_noticias.ui.v015_image_truth_layout import install_v015_image_truth_layout
from monitor_noticias.ui.v015_home_installer import install_v015_home_reference

install_v009_runtime_fixes()
install_v009_pdf_cover_patch()
install_v010_runtime_fixes()
install_v010_external_bridge()
install_v010_video_boundary_fix()
install_v011_pdf_stability()
install_v011_sidebar_fidelity()
install_v012_runtime_fixes()
install_v013_sidebar_reference()
install_v014_full_reference_layout()
install_v014_reference_sidebar_local()
# v0.0.15 usa as imagens fornecidas como verdade visual sem mudar os motores.
install_v015_image_truth_layout()
install_v015_home_reference()

from monitor_noticias.app.application import main

if __name__ == "__main__":
    raise SystemExit(main())
