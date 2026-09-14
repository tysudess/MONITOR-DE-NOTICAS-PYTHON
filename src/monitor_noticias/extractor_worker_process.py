from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from monitor_noticias.extractor import EXTRACTOR_QUALITIES, ExtractorEngine


def _emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--app-root", default="")
    parser.add_argument("--url", default="")
    parser.add_argument("--quality-index", type=int, default=1)
    parser.add_argument("--self-test", action="store_true")
    args, _unknown = parser.parse_known_args(argv)

    if args.self_test:
        _emit({"type": "self-test", "ok": True})
        return 0

    root = Path(args.app_root).resolve()
    index = max(0, min(int(args.quality_index), len(EXTRACTOR_QUALITIES) - 1))
    try:
        engine = ExtractorEngine(root)
        result = engine.download(
            args.url,
            EXTRACTOR_QUALITIES[index],
            "",
            lambda pct, message: _emit(
                {"type": "progress", "pct": int(pct), "message": str(message)}
            ),
        )
        _emit({"type": "done", "path": str(Path(result).resolve())})
        return 0
    except BaseException as exc:
        # O worker é propositalmente o limite de falha: até SystemExit/erros
        # nativos do fluxo de download ficam fora do processo principal.
        _emit({"type": "error", "message": str(exc) or exc.__class__.__name__})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
