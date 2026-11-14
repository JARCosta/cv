"""Simple renderer tool wrapper.

Runs scripts/render_resume.py on a given markdown draft, captures stdout/stderr,
and emits a JSON summary describing the outcome and generated files.

Designed to be called by an orchestrator or by Copilot Chat as a local tool.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "tex" / "generated"
RENDER_SCRIPT = Path(__file__).resolve().parent / "render_resume.py"


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run the renderer and return JSON metadata")
    parser.add_argument("draft", help="Path to drafts/<job-slug>/resume.md")
    parser.add_argument("--json", action="store_true", help="Print only JSON to stdout")
    args = parser.parse_args()

    draft = Path(args.draft)
    if not draft.is_absolute():
        draft = ROOT / draft
    if not draft.is_file():
        payload = {"success": False, "error": f"draft not found: {draft}"}
        print(json.dumps(payload), file=sys.stdout)
        return 2

    # snapshot pre-run files
    pre_files = {p.name for p in GENERATED.glob("*") if p.is_file()} if GENERATED.exists() else set()
    start = time.time()

    proc = subprocess.Popen([sys.executable, str(RENDER_SCRIPT), str(draft)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate()
    rc = proc.returncode
    duration = time.time() - start

    # list generated files after run
    generated_files = []
    if GENERATED.exists():
        for p in sorted(GENERATED.glob("*")):
            if p.is_file():
                generated_files.append(str(p))

    payload = {
        "success": rc == 0,
        "returncode": rc,
        "duration_sec": round(duration, 3),
        "stdout": out.strip(),
        "stderr": err.strip(),
        "generated_dir": str(GENERATED),
        "generated_files": generated_files,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("Renderer wrapper result:")
        print(json.dumps(payload, indent=2))

    return 0 if rc == 0 else rc


if __name__ == "__main__":
    raise SystemExit(main())
