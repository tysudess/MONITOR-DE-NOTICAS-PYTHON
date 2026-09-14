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

install_v009_runtime_fixes()

from monitor_noticias.app.application import main

if __name__ == "__main__":
    raise SystemExit(main())
