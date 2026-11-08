# CV tailoring workflow

1. Save and rank the job posting under `posts/`.
2. Run the `ATS Resume Planner` agent. It creates a complete draft at `drafts/<job-slug>/resume.md` from `context/`.
3. Review that Markdown draft. It is the only job-specific content source.
4. Run the `ATS Resume Renderer` agent, or run:

   `python scripts/render_resume.py drafts/<job-slug>/resume.md`

5. Build `tex/JoaoRoqueCosta.tex` with the existing LaTeX task and inspect the PDF.

The renderer overwrites every file in `tex/generated/`. It never reads the previous PDF or the old hand-authored section files, so omitted content cannot survive from a prior job.