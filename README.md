# CV tailoring workflow

This project automates the process of tailoring a CV for specific job applications.

## Workflow:
1. (persistent) Load the candidate's base history into `context/`.
2. Load the job offer description using the `browser` tool.
3. Build the tailored CV markdown file in `drafts/` using the job offer content and the candidate's base history.
4. Use the `latexify` custom tool to convert the markdown CV into a PDF format.

## CLI entrypoints (minimal)

Two small helper scripts are provided to make orchestration from Copilot Chat or locally easy and token-cheap:

- scripts/run_renderer_tool.py
  - Wrapper around scripts/render_resume.py. Run:

      python scripts/run_renderer_tool.py drafts/<job-slug>/resume.md --json

  - Returns JSON containing success, returncode, stdout/stderr, generated_dir and a list of generated files.

- scripts/orchestrator.py
  - Simple pipeline runner that invokes the renderer wrapper and optionally runs a LaTeX command to produce a PDF. Example:

      python scripts/orchestrator.py --draft drafts/<job-slug>/resume.md --latex-cmd "pdflatex -interaction=nonstopmode -output-directory tex/generated tex/JoaoRoqueCosta.tex"

  - The orchestrator prints JSON summaries and exits with a non-zero code on failure.

Typical Copilot Chat usage: run the Planner agent (provide a job posting URL via the browser tool) so it writes `drafts/<job-slug>/resume.md`, then call `scripts/orchestrator.py --draft drafts/<job-slug>/resume.md` to render the sections and (optionally) build the PDF. This keeps rendering as a local tool call and reduces LLM token usage.