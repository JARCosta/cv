# Orchestrator / Main Copilot Agent Instructions

Purpose: drive the Planner -> Renderer -> LaTeX build flow inside GitHub Copilot Chat, minimizing LLM tokens by using local tool calls for rendering and build steps.

Agent responsibilities (high level)

- Input: one job-posting URL (user provides it in the chat).
- Step 1 — Planner: open the URL using the browser tool, extract job content, map requirements/keywords to candidate context, and write the canonical draft at `drafts/<job-slug>/resume.md`.
  - Always write/overwrite `drafts/<job-slug>/resume.md` as the single source of truth.
  - Do not rely on `posts/`.
- Step 2 — Renderer: call the renderer as a local tool rather than generating LaTeX via LLM. Run the repository tool:

    python scripts/run_renderer_tool.py drafts/<job-slug>/resume.md --json

  - Expect JSON with keys: success (bool), returncode, stdout, stderr, generated_dir, generated_files.
  - If success is false, return the error to the user and stop.
- Step 3 — LaTeX build: invoke the repository's VS Code task or a user-provided single-shell command to compile the template into PDF. Example command (agent may run via the environment's run-command):

    pdflatex -interaction=nonstopmode -output-directory tex/generated tex/JoaoRoqueCosta.tex

  - Report build stdout/stderr and final PDF path(s) to the user.

Tool contract and best practices

- Planner must only accept a single URL as input and produce a complete Markdown draft; do not attempt to render or build inside the Planner LLM turn.
- Use the provided renderer wrapper (`scripts/run_renderer_tool.py`) as the canonical local tool to convert the draft into LaTeX sections. This avoids extra LLM tokens and keeps rendering deterministic.
- The orchestrator must not pass the Markdown content back into the LLM for rendering; treat the renderer output files as authoritative.
- Sanitize user-provided URLs minimally: only allow HTTP/HTTPS; report unreachable or blocked pages clearly.

Failure modes and reporting

- If the Planner cannot fetch/parse the URL, explain why and provide the raw page snippet if permitted.
- If the renderer returns success=false or non-zero returncode, present stderr and a concise explanation of likely draft issues (e.g., missing sections, malformed bullets).
- If LaTeX build fails, surface the first 100 lines of stderr and suggest common fixes (missing package, unescaped characters).

Privacy and security

- Do not exfiltrate local files or secrets. When running local commands, avoid shell=True and prefer explicit args.

Notes on tool alternatives

- A true Copilot "custom tool" that runs the renderer is possible, but the wrapper script is intentionally minimal and explicit to keep behavior auditable. If a custom tool is later preferred, implement a lightweight extension that runs the same script and returns the same JSON contract.

Example short run summary the agent should return to the user on success

- "Draft written: drafts/<job-slug>/resume.md\nRenderer: success, 5 sections written to tex/generated/\nLaTeX: PDF built at tex/generated/JoaoRoqueCosta.pdf"

End of instructions.