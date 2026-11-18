---
name: draft-author
description: "Consume the gathered job analysis from the conversation context and repository files to produce a canonical job-specific Markdown resume at drafts/<job-slug>/resume.md."
tools: [read, edit]
user-invocable: true
metadata:
  allowed_tools:
    - read
    - edit
---

# Draft Author

## Purpose
- Consume the job analysis, requirement ranking, and evidence mappings produced by `gather-job` in the current conversation.
- Produce a complete, truthful Markdown draft at `drafts/<job-slug>/resume.md` adhering strictly to the parser contract required by `scripts/render_resume.py`.
- Overwrite the target draft file atomically and return a brief validation summary.

## Inputs
- Gathered job analysis and evidence mappings present in the active conversation history from `gather-job`.
- Candidate context files in `context/` (for verifying exact phrasing, dates, or details as needed).

## Outputs
- **File written**: `drafts/<job-slug>/resume.md` (create parent directories if needed).
- **Validation summary in response**:
  - `draft_path`: `drafts/<job-slug>/resume.md`
  - `alignment_score`: `0..100`
  - `missing_musts`: list of any Must Have requirements lacking evidence (or empty list)
  - `warnings`: any structural or coverage notes

## Rules & Evidence Guidelines
- **No Artifact Files**: Do not look for or read JSON artifacts. Rely on the conversation context from `gather-job` and verify directly against `context/`.
- **No Stale Templates**: Never read existing `.tex` files or previous drafts under `drafts/` as evidence or wording templates. Write every section from scratch for the current role.
- **Strict Traceability**: Every claim must be backed by `context/`. Never invent metrics, ownership, production status, technologies, certifications, or proficiency. Do not upgrade "contributed," "prototype," or "coursework" into production ownership.
- **Inline Formatting Rules**:
  - Use `**bold text**` selectively (typically 1–2 key phrases per bullet) for job-relevant technologies, methods, and evidence across the Summary, Experience, Education, Extracurricular, and Skills sections.
  - Add Markdown hyperlinks `[visible label](https://example.com)` **only** when the exact URL exists in `context/` or the job posting. Never invent URLs.
  - Never write raw LaTeX commands in the draft.
- **Static Metadata Preservation**: Keep exact heading names for `Professional Experience` (`Deloitte` and `Instituto Superior Técnico`) and `Education` (`Master's Degree` and `Bachelor's Degree`) so `scripts/render_resume.py` can map static metadata accurately.
- **Selective Extracurriculars**: Include only the strongest job-relevant extracurricular projects rather than dumping the entire inventory.
## Draft Format Contract
The file `drafts/<job-slug>/resume.md` must match this exact Markdown structure so `scripts/render_resume.py` parses it without error:

```markdown
---
job_slug: <job-slug>
company: <company>
role: <role>
source_post: <source_post>
---

# Resume Draft

## Requirement Ranking
### Must Have
- <requirement>: <candidate evidence or "not evidenced">
### Strong Match
- <requirement>: <candidate evidence or "not evidenced">
### Nice To Have
- <requirement>: <candidate evidence or "not evidenced">
### Unsupported
- <requirement>

## Summary
<one concise paragraph>

## Professional Experience
### Deloitte
- <complete job-specific bullet>
### Instituto Superior Técnico
- <complete job-specific bullet>

## Education
### Master's Degree
- Description: <small factual description>
- Relevant Coursework: <comma-separated courses>
- Thesis Title: <title or [title](url)>
  - <relevant thesis point>
### Bachelor's Degree
- Relevant Areas: <comma-separated areas>
- Relevant Projects:
  - <project or factual academic evidence>

## Extracurricular
- <relevant project or activity>

## Skills
- <area>: <comma-separated supported technologies or capabilities>
```