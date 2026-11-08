"""Render a strict resume Markdown draft into the generated Awesome CV sections."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "tex" / "generated"

EXPERIENCE_METADATA = {
    "Deloitte": ("Tech Analyst", "Coimbra, Portugal", "Apr. 2026 - Oct. 2026"),
    "Instituto Superior Técnico": (
        "Teaching Assistant",
        "Lisbon, Portugal",
        "Oct. 2024 - Jul. 2025",
    ),
}
EDUCATION_METADATA = {
    "Master's Degree": (
        "Instituto Superior Técnico",
        "M.Sc. Computer Science and Engineering",
        "Lisbon, Portugal",
        "Sep 2023 - Nov 2025",
    ),
    "Bachelor's Degree": (
        "Instituto Superior Técnico",
        "B.Sc. Computer Science and Engineering",
        "Lisbon, Portugal",
        "Sep 2020 - Jul 2023",
    ),
}

REQUIRED_SECTIONS = {
    "Summary",
    "Professional Experience",
    "Education",
    "Extracurricular",
    "Skills",
}


def fail(message: str) -> None:
    raise ValueError(message)


def escape_latex(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(character, character) for character in value)


INLINE_MARKUP = re.compile(r"\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)]+)\)")


def render_inline(value: str) -> str:
    """Convert supported Markdown inline syntax into escaped LaTeX."""
    rendered = []
    position = 0
    for match in INLINE_MARKUP.finditer(value):
        rendered.append(escape_latex(value[position : match.start()]))
        if match.group(1) is not None:
            rendered.append(r"\textbf{" + render_inline(match.group(1)) + "}")
        else:
            label, url = match.group(2), match.group(3)
            rendered.append(r"\cvref{" + escape_latex(url) + "}{" + render_inline(label) + "}")
        position = match.end()
    rendered.append(escape_latex(value[position:]))
    return "".join(rendered)


def parse_sections(text: str) -> dict[str, list[str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        fail("draft must start with YAML frontmatter")
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        fail("frontmatter is not closed")

    content = lines[end + 1 :]
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in content:
        match = re.match(r"^## (.+?)\s*$", line)
        if match:
            current = match.group(1)
            if current in sections:
                fail(f"duplicate section: {current}")
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line.rstrip())

    missing = REQUIRED_SECTIONS - sections.keys()
    if missing:
        fail("missing sections: " + ", ".join(sorted(missing)))
    return sections


def nonempty_lines(lines: list[str]) -> list[str]:
    return [line.strip() for line in lines if line.strip()]


def heading_blocks(lines: list[str]) -> dict[str, list[str]]:
    blocks: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines:
        match = re.match(r"^### (.+?)\s*$", line.strip())
        if match:
            current = match.group(1)
            blocks[current] = []
        elif current is not None:
            blocks[current].append(line)
    return blocks


def bullets(lines: list[str]) -> list[str]:
    values = []
    for line in lines:
        match = re.match(r"^\s*-\s+(.+?)\s*$", line)
        if match:
            values.append(match.group(1))
    return values


def required_bullets(lines: list[str], label: str) -> list[str]:
    values = bullets(lines)
    if not values:
        fail(f"{label} must contain at least one bullet")
    return values


def cvitems(values: list[str]) -> str:
    return "\n".join(f"        \\item {{{render_inline(value)}}}" for value in values)


def cventry(metadata: tuple[str, str, str, str], values: list[str]) -> str:
    organization, role, location, dates = metadata
    return f"""  \\cventry
    {{{escape_latex(role)}}}
    {{{escape_latex(organization)}}}
    {{{escape_latex(location)}}}
    {{{escape_latex(dates)}}}
    {{
      \\begin{{cvitems}}
{cvitems(values)}
      \\end{{cvitems}}
    }}
    {{}}
"""


def render_summary(lines: list[str]) -> str:
    paragraph = " ".join(nonempty_lines(lines))
    if not paragraph:
        fail("Summary must contain a paragraph")
    return """%% Generated from a job-specific resume Markdown draft.
\\begin{cvparagraph}
  %s
\\end{cvparagraph}
""" % render_inline(paragraph)


def render_experience(lines: list[str]) -> str:
    blocks = heading_blocks(lines)
    if set(blocks) != set(EXPERIENCE_METADATA):
        fail("Professional Experience headings must match static metadata exactly")
    entries = []
    for employer, metadata in EXPERIENCE_METADATA.items():
        entries.append(cventry((employer, *metadata), required_bullets(blocks[employer], employer)))
    return "\\cvsection{Professional Experience}\n\\begin{cventries}\n\n" + "\n".join(entries) + "\\end{cventries}\n"


def labelled_value(lines: list[str], label: str) -> str:
    prefix = f"- {label}:"
    for line in lines:
        if line.strip().startswith(prefix):
            value = line.strip()[len(prefix) :].strip()
            if value:
                return value
    fail(f"Education is missing: {label}")


def nested_bullets(lines: list[str]) -> list[str]:
    values = []
    for line in lines:
        match = re.match(r"^\s{2,}-\s+(.+?)\s*$", line)
        if match:
            values.append(match.group(1))
    return values


def render_education(lines: list[str]) -> str:
    blocks = heading_blocks(lines)
    if set(blocks) != set(EDUCATION_METADATA):
        fail("Education headings must contain exactly Master's Degree and Bachelor's Degree")

    master = blocks["Master's Degree"]
    master_description = labelled_value(master, "Description")
    coursework = labelled_value(master, "Relevant Coursework")
    thesis = labelled_value(master, "Thesis Title")
    thesis_points = nested_bullets(master)
    if not thesis_points:
        fail("Master's Degree must contain thesis points")

    bachelor = blocks["Bachelor's Degree"]
    areas = labelled_value(bachelor, "Relevant Areas")
    projects = nested_bullets(bachelor)
    if not projects:
        fail("Bachelor's Degree must contain relevant projects")

    institution, degree, location, dates = EDUCATION_METADATA["Master's Degree"]
    master_values = [
        master_description,
        "Relevant Coursework: " + coursework,
        "Thesis: " + thesis,
    ] + ["Thesis: " + point for point in thesis_points]
    output = ["\\cvsection{Education}", "\\begin{cventries}", "", cventry((institution, degree, location, dates), master_values)]

    institution, degree, location, dates = EDUCATION_METADATA["Bachelor's Degree"]
    bachelor_values = ["Relevant Areas: " + areas] + ["Relevant Project: " + project for project in projects]
    output.append(cventry((institution, degree, location, dates), bachelor_values))
    output.append("\\end{cventries}\n")
    return "\n".join(output)


def render_extracurricular(lines: list[str]) -> str:
    values = required_bullets(lines, "Extracurricular")
    return "\\cvsection{Extracurricular}\n\\begin{cventries}\n  \\cventry{}{}{}{}\n    {\\begin{cvitems}\n" + cvitems(values) + "\n    \\end{cvitems}}\n    {}\n\\end{cventries}\n"


def render_skills(lines: list[str]) -> str:
    values = required_bullets(lines, "Skills")
    skills = []
    for value in values:
        if ":" not in value:
            fail("each Skills bullet must use '<area>: <skills>'")
        area, technologies = value.split(":", 1)
        if not area.strip() or not technologies.strip():
            fail("each Skills bullet needs an area and at least one skill")
        skills.append("  \\cvskill\n    {%s}\n    {%s}" % (render_inline(area.strip()), render_inline(technologies.strip())))
    return "\\cvsection{Skills \\& Competencies}\n\\begin{cvskills}\n" + "\n\n".join(skills) + "\n\\end{cvskills}\n"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python scripts/render_resume.py drafts/<job-slug>/resume.md", file=sys.stderr)
        return 2
    draft = Path(sys.argv[1])
    if not draft.is_absolute():
        draft = ROOT / draft
    if not draft.is_file():
        print(f"draft not found: {draft}", file=sys.stderr)
        return 2

    try:
        sections = parse_sections(draft.read_text(encoding="utf-8"))
        rendered = {
            "0.summary.tex": render_summary(sections["Summary"]),
            "1.experience.tex": render_experience(sections["Professional Experience"]),
            "2.education.tex": render_education(sections["Education"]),
            "3.extracurricular.tex": render_extracurricular(sections["Extracurricular"]),
            "4.skills.tex": render_skills(sections["Skills"]),
        }
    except ValueError as error:
        print(f"invalid resume draft: {error}", file=sys.stderr)
        return 1

    GENERATED.mkdir(parents=True, exist_ok=True)
    for name, content in rendered.items():
        (GENERATED / name).write_text(content, encoding="utf-8")
    print(f"rendered {len(rendered)} sections from {draft}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
