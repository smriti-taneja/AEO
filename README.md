# AEO — pillar/cluster blog agent

A generic, multi-tenant system for writing blog content that ranks in LLM search (ChatGPT, Claude, Perplexity, Google AI Overviews) and traditional SEO, using a pillar/cluster architecture. Not tied to one brand or website — every run starts by identifying which project it's working on.

## How it fits together

- **`.claude/skills/`** — the skills themselves (this repo, versioned, works wherever Claude Code runs against this repo):
  - `blog-pipeline` — the master orchestrator. Say "write a blog", "create a pillar", "onboard a brand" to trigger it. Runs: identify project → interview → research → plan → build → crosslink → QA → CMS handoff → human review.
  - `content-strategy` — pillar/cluster planning and internal-linking architecture (wraps the installed `topic-cluster-planning` and `fanout-mapper` skills).
  - `copywriting` — brand-voice enforcement and the cluster differentiation check (wraps the installed `write-content` and `humanizer` skills).
  - `cms-drafting` — idempotent draft push to Webflow/WordPress/Ghost. Never publishes.
  - `seo-audit-cron` — monthly Firecrawl-based competitor audit, written into the project's `wiki/seo/`.

  This account also has the `anthropic-skills` plugin installed (`ai-seo`, `content-brief`, `cite-me`, `eeat-audit`, `keyword-deep-dive`, `expert-interview`, `revive-content`, `linkbuilding`, `page-audit`, `semantic-gap-analysis`, `improve-content`, `featured-snippet-optimizer`). `blog-pipeline` and its sub-skills call into these rather than re-implementing them — this repo only adds what wasn't already covered: the orchestrator itself, brand-agnostic brain scaffolding, idempotent CMS push, and the audit cron.

- **`scripts/`** — the executable parts:
  - `init_brain.sh` — scaffolds a new project's Obsidian vault from `templates/brain/`.
  - `cms/{webflow,wordpress,ghost}_push.py` — one script per platform, all idempotent-by-slug, all draft-only.
  - `seo/firecrawl_audit.py` — the competitor audit logic behind `seo-audit-cron`.

- **`templates/brain/`** — the starter vault structure copied into every new project:
  ```
  wiki/seo/          target keywords, competitor analysis, ranking reports
  wiki/voice/        tone of voice, banned phrases, approved stats
  wiki/positioning/  product positioning, ICP, differentiation
  raw/research/      per-article research packs (JSON)
  pipelines/blog/    active cluster state, drafts, assets
  output/reports/    SEO audit outputs
  ```

- **`config/`** — one JSON file per real project (`config/<slug>.json`, gitignored — copy `project.example.json` as the starting point). Holds the CMS platform, collection/site IDs, target keywords, competitors, and vault path. **Credentials are never stored here** — only the *names* of environment variables (`WEBFLOW_API_TOKEN`, `FIRECRAWL_API_KEY`, etc.) that must be set wherever the pipeline runs.

## Onboarding a new brand/website

Just say "onboard a brand" or "write a blog for \<brand\>" and `blog-pipeline` will:
1. Ask for the brand name, domain, and where its vault should live (defaults to `~/Documents/<slug>-brain/` — kept local to your machine by design, not committed to this repo).
2. Scaffold the vault via `init_brain.sh` if it doesn't exist yet.
3. Run the 12-question interview gate (target keyword, audience, intent, cluster angles, competitors, unique angle, internal links, visuals, author, publish target, things to avoid) — and push back on thin answers rather than proceeding with guesses.
4. From there: parallel research (3 subagents), a pillar+cluster plan you confirm, parallel drafting (1 subagent per article), crosslinking, a hard quality-gate check, and a draft-only CMS push — ending with a ping to you for review. Nothing publishes itself, ever.

## Quality gates (enforced, not advisory)

Pillar ≥2000 words · clusters ≥800 words · meta title ≤60 chars · meta description ≤160 chars · ≥2 authority sources per article · every image has alt text · no em dashes · every H2 opens with a 40–60 word direct answer · TL;DR + FAQ (with JSON-LD) present · named author + last-updated date · cluster differentiation check passed. Full list: `.claude/skills/blog-pipeline/references/quality-gates.md`.

## Setting up the monthly SEO audit for a real project

Once a project is onboarded and `config/<slug>.json` exists with real keywords and a `FIRECRAWL_API_KEY`, ask to "set up the monthly audit for \<brand\>" — `seo-audit-cron` registers a durable, account-level scheduled Routine (not a session-only cron) that reruns the audit and writes reports into that project's `wiki/seo/ranking-reports/`.

## What's intentionally not built yet

- Real Webflow/WordPress/Ghost credentials — the push scripts are complete and tested for syntax, but untested against live APIs since no project has credentials yet. First real use of `cms-drafting` should be treated as a dry run: check the created/updated draft in the CMS UI before trusting it blindly.
- Local asset upload in `webflow_push.py` (raises `NotImplementedError` with a clear message) — host images via CDN/media library first and pass URLs, or extend that function when needed.
- No monthly Routine exists yet anywhere — it's created per-project, on request, once real keywords exist.
