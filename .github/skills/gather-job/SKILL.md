---
name: gather-job
description: "Fetch a public job posting, extract canonical requirements and keywords, and map them against repository candidate context in memory for immediate handoff to draft-author."
tools: [read, browser, vscodeBrowser]
user-invocable: true
metadata:
  allowed_tools:
    - read
    - browser
    - vscodeBrowser
---

# Gather Job & Context

## Purpose
- Fetch and canonicalize the job posting at the provided public HTTP/HTTPS URL using `browser` or `vscodeBrowser`.
- Extract requirement statements and categorize them into **Must Have**, **Strong Match**, **Nice To Have**, and **Unsupported**.
- Search and analyze the `context/` repository folder to map factual candidate evidence to every job requirement and keyword.
- Output a structured analysis directly in the conversation response so `draft-author` can immediately consume it without intermediate files.

## Inputs
- `job_url`: string (public HTTP/HTTPS URL) or local path under `posts/`

## Conversation Output Contract
Present the gathered findings clearly in your response using the following structure so the subsequent `draft-author` invocation has complete context:
- **Metadata**: `job_slug`, `company`, `role`, and `source_post` (the URL or `posts/<file>.md` path)
- **Alignment Score**: `0..100` based strictly on factual evidence found in `context/`
- **Keywords**: List of core technical and domain keywords extracted from the posting
- **Requirement Ranking & Evidence Mapping**:
  - **Must Have**: `<requirement>` — `<exact evidence from context/ or "not evidenced">`
  - **Strong Match**: `<requirement>` — `<exact evidence from context/ or "not evidenced">`
  - **Nice To Have**: `<requirement>` — `<exact evidence from context/ or "not evidenced">`
  - **Unsupported**: `<requirement>`
- **Verified URLs**: List any authoritative URLs found in `context/` or the job posting that are relevant to the candidate's projects, thesis, or coursework.

## Behavior & Rules
- **URL Validation**: Only fetch public HTTP/HTTPS URLs. Reject other protocols with a clear error.
- **Zero File Writes**: Do not create any artifact JSON files, temporary files, or context stores.
- **Strict Evidence Grounding**: Every match must be traceable to `context/`. Never inflate "contributed," "prototype," or "coursework" into ownership or production experience.
- **Context Window Hygiene**: Keep the extracted requirements, candidate evidence mappings, and verified URLs clearly visible in your final output for direct handoff to `draft-author`.