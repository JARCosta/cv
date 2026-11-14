"""Simple orchestrator that runs the pipeline: draft -> renderer tool -> optional LaTeX build.

Usage examples:
  python scripts/orchestrator.py --draft drafts/<job-slug>/resume.md
  python scripts/orchestrator.py --draft drafts/<job-slug>/resume.md --latex-cmd "pdflatex -interaction=nonstopmode -output-directory tex/generated tex/JoaoRoqueCosta.tex"

The orchestrator keeps behavior minimal so Copilot Chat can call it as a local tool.
"""
from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_TOOL = Path(__file__).resolve().parent / "run_renderer_tool.py"


def run_renderer(draft: Path) -> dict:
    proc = subprocess.run([sys.executable, str(RUN_TOOL), str(draft), "--json"], capture_output=True, text=True)
    try:
        return json.loads(proc.stdout)
    except Exception:
        return {"success": False, "error": "failed to parse renderer output", "stdout": proc.stdout, "stderr": proc.stderr}


def run_latex(latex_cmd: str) -> dict:
    # Shell-split the command; do not use shell=True to avoid injection risks
    args = shlex.split(latex_cmd)
    proc = subprocess.run(args, capture_output=True, text=True)
    return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Orchestrate planner output -> renderer tool -> optional LaTeX build")
    parser.add_argument("--draft", help="Path to drafts/<job-slug>/resume.md", required=True)
    parser.add_argument("--latex-cmd", help="Optional LaTeX command to compile the template (single command string)")
    args = parser.parse_args()

    draft = Path(args.draft)
    if not draft.is_absolute():
        draft = ROOT / draft
    if not draft.is_file():
        print(json.dumps({"success": False, "error": f"draft not found: {draft}"}, indent=2))
        return 2

    print(f"Running renderer on {draft}")
    renderer_result = run_renderer(draft)
    print(json.dumps(renderer_result, indent=2))

    if not renderer_result.get("success"):
        print("Renderer reported failure; aborting orchestrator.")
        return 1

    if args.latex_cmd:
        print("Running LaTeX build...")
        latex_result = run_latex(args.latex_cmd)
        print(json.dumps(latex_result, indent=2))
        if latex_result.get("returncode", 1) != 0:
            print("LaTeX build failed.")
            return 1

    print("Orchestration complete. Generated files:")
    for f in renderer_result.get("generated_files", []):
        print(f)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
