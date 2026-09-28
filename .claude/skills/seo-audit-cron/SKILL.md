---
name: seo-audit-cron
description: Monthly competitor SEO/AEO audit for a project's target keywords using Firecrawl — pulls top-ranking pages, analyzes title/structure/word count/claims, finds gaps, and writes the report into wiki/seo/ so future blog-pipeline runs can reference it. Use when asked to "run the SEO audit", "set up the monthly audit", or when a scheduled Routine fires this skill by name.
---

# SEO Audit Cron

Two separate things live under this skill: **running the audit** (can happen any time, on demand) and **scheduling it monthly** (a one-time setup step per project, using a durable Routine — not a session-only cron).

## Running the audit

Requires, from the project config: `target_keywords`, `competitors` (or "top ranking pages" if no fixed competitor list), and `FIRECRAWL_API_KEY` in the environment.

```
scripts/seo/firecrawl_audit.py --project <slug> --config config/<slug>.json
```

For each target keyword, the script:
1. Pulls the current top-ranking pages (Firecrawl search).
2. Scrapes each one and extracts: title, approximate word count, H2/H3 structure, the specific claims/stats they cite, and whether they carry FAQ/Article schema.
3. Diffs that against the project's own published posts on the same keyword (if any).
4. Writes a dated report to `wiki/seo/ranking-reports/<YYYY-MM-DD>-<keyword-slug>.md`, and appends a rolling summary row to `wiki/seo/competitor-analysis.md`.

Read the resulting report and summarize the actionable gaps back to the user — don't just say "report written," name the 2–3 things worth acting on (a subtopic nobody covers, a stale competitor claim to out-date, a format competitors are missing).

## Scheduling it monthly

This needs a **project that actually exists** — real keywords, a real vault path, a real Firecrawl key. Don't create a schedule speculatively; only set this up when the user has onboarded a real brand through `blog-pipeline`'s Step 0 and confirmed they want recurring audits.

Session-scoped cron (the `CronCreate` tool) auto-expires after 7 days and only fires into this session — not durable enough for "monthly." Use the account-level Routine mechanism instead (`create_trigger`):

- `cron_expression`: e.g. `"0 9 1 * *"` (9am on the 1st of each month, in the project owner's timezone — write it as `CRON_TZ=<their IANA zone> 0 9 1 * *` if known)
- `prompt`: a complete, standalone instruction naming the project slug and asking to run this skill's audit and report back — e.g. *"Run the seo-audit-cron skill for project `<slug>` (config at config/<slug>.json) and summarize the top gaps found."*
- `initiation`: `human_request`
- Prefer `create_new_session_on_fire: true` so each monthly run starts clean rather than accumulating context in one long-lived session.

Confirm with the user before creating the Routine (it's a standing, recurring action), and tell them where the reports will land (`wiki/seo/ranking-reports/`) so they know where to look between runs.
