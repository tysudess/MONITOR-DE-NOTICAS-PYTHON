from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from monitor_noticias.extractor import EXTRACTOR_QUALITIES, ExtractorEngine


_EVENT_FILE: Path | None = None


def _emit(payload: dict) -> None:
    line = json.dumps(payload, ensure_ascii=False) + "\n"
    if _EVENT_FILE is not None:
        _EVENT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with _EVENT_FILE.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(line)
            stream.flush()
        return
    stream = getattr(sys, "stdout", None)
    if stream is not None:
        stream.write(line)
        stream.flush()


def main(argv: list[str] | None = None) -> int:
    global _EVENT_FILE
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--app-root", default="")
    parser.add_argument("--url", default="")
    parser.add_argument("--quality-index", type=int, default=1)
    parser.add_argument("--event-file", default="")
    parser.add_argument("--self-test", action="store_true")
    args, _unknown = parser.parse_known_args(argv)
    _EVENT_FILE = Path(args.event_file).resolve() if args.event_file else None

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
        # O processo principal permanece vivo mesmo se o motor/biblioteca de
        # download provocar SystemExit ou erro nativo dentro deste worker.
        _emit({"type": "error", "message": str(exc) or exc.__class__.__name__})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
