---
name: gather-job
description: "Fetch a public job posting and extract canonical text, ranked requirements/keywords, and repository context matches for the candidate evidence. Produces artifacts/gather/<job-slug>.json."
tools: [edit, browser, vscodeBrowser]
user-invocable: true
metadata:
  allowed_tools:
    - read
    - browser
    - vscodeBrowser
---

# Gather Job & Context

## Purpose
- Fetch and canonicalize the job posting at the provided public HTTP/HTTPS URL (use the `browser` or `vscodeBrowser` tool).
- Extract requirement statements and rank them (must/strong/nice/unsupported).
- Analyze the `context/` repository folder for candidate-evidence matches to the job posting requirements and keywords.

## Inputs
- job_url: string (public HTTP/HTTPS)

## Outputs (artifact JSON)
- job_slug: string
- company: string | null
- role: string | null
- source_post_snippet: string
- requirements: [{ text: string, category: "must"|"strong"|"nice"|"unsupported" }]
- keywords: [string]
- allignment: [float] (0..100)

## Behavior & Rules
- Only fetch HTTP/HTTPS URLs. Reject others with a clear error.
- Decide on an allignment score (0..100) based on the candidate context and job posting match.
- Do not create any output file or context stores.
- Organize your context window to keep the job posting and candidate context visible for reference.