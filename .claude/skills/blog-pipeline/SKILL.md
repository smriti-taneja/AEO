---
name: blog-pipeline
description: Master orchestrator for pillar/cluster blog and landing-page content aimed at ranking in LLM search (ChatGPT, Claude, Perplexity, Google AI Overviews) and traditional SEO. Trigger on "write a blog", "create a pillar", "draft a post", "build a content cluster", "onboard a brand". Runs interview -> research -> plan -> build -> draft -> crosslink -> QA -> CMS handoff, using parallel subagents and enforcing hard quality gates before any draft reaches the CMS. Works for any brand/website — brand details are collected at run time, never hardcoded.
---

# Blog Pipeline

This is a generic, multi-tenant orchestrator. It is not wired to one brand — every run starts by identifying which project it's working on, then reads that project's own "brain" (an Obsidian-style knowledge base) for voice, positioning, and SEO context.

It composes these existing skills rather than duplicating them:
- `content-strategy` (this repo) — pillar/cluster architecture, wraps `topic-cluster-planning` and `fanout-mapper`
- `copywriting` (this repo) — voice/banned-phrase enforcement, wraps `write-content` and `humanizer`
- `cms-drafting` (this repo) — idempotent draft push to Webflow/WordPress/Ghost
- `ai-seo`, `content-brief`, `cite-me`, `eeat-audit` (anthropic-skills) — AEO strategy and citation-readiness

## Step 0 — Identify the project and its brain

Ask (if not already known this session): **brand name + domain**, and the **vault path** — default `~/Documents/<brand-slug>-brain/`. Do not invent these.

Check whether the vault exists at that path (`ls`/`Glob`). If it doesn't:
```
scripts/init_brain.sh "<Brand Name>" <brand-slug> [target-dir]
```
This scaffolds `wiki/seo/`, `wiki/voice/`, `wiki/positioning/`, `raw/research/`, `pipelines/blog/`, `output/reports/` from `templates/brain/`. Tell the user it was created and that `wiki/voice/` and `wiki/positioning/` are currently just templates — they should fill them in or answer thoroughly at the interview gate so this run can fill them in for them.

If the vault exists, read `wiki/voice/*.md`, `wiki/positioning/*.md`, and `wiki/seo/keyword-map.md` before the interview — don't re-ask what's already on file, just confirm it's still current.

## Step 1 — Interview gate (mandatory)

Full question list and push-back rules: `references/interview-questions.md`. Ask all of them in one pass. **Push back on thin answers** — a vague audience ("marketers"), a generic differentiation ("we're better"), or "beat everyone" as a competitor list is not an answer. Do not proceed to research until each answer is specific enough to act on.

Save the finished brief to `pipelines/blog/<slug>/brief.md`.

## Step 2 — Research (3 parallel subagents — never sequential)

Launch all three in **one message, multiple Agent calls**:
1. **Brain query** — read the vault's `wiki/`, existing `raw/research/`, and any posts named as internal-link targets. Summarize what's already known/claimed so new content doesn't contradict it.
2. **Fresh web** — research the target keyword, cluster angles, and named competitors (SERP, PAA, competitor structure/word counts/claims). Use Firecrawl if `FIRECRAWL_API_KEY` is set for this project, otherwise WebSearch/WebFetch.
3. **Structure plan** — hand the brief to the `content-strategy` skill for a first-pass pillar/cluster map and intent classification.

Merge the three outputs into `raw/research/<slug>.json`.

## Step 3 — Plan

Produce the pillar + 3–4 cluster plan: target query, intent (informational/comparison/decision), angle, word-count target (pillar ≥2000, cluster ≥800), and an internal-linking map (which piece links to which, plus links to the existing posts named in the interview). Save to `pipelines/blog/<slug>/plan.md` and show it to the user as a checkpoint before drafting, unless they've explicitly said to skip confirmation.

## Step 4 — Build (parallel subagents — one per article, never sequential)

Once the plan is confirmed, spawn **one subagent per article** (pillar + each cluster) in a single message. Each subagent:
- Gets the plan node, the merged research, and the vault's voice/positioning context
- Applies `references/quality-gates.md` formatting rules (direct-answer H2s, TL;DR, FAQ, etc.) while writing, not as an afterthought
- Runs its draft through the `copywriting` skill's voice rules before returning
- Writes to `pipelines/blog/<slug>/drafts/<article-slug>.md` with front-matter (title, meta title, meta description, author, last-updated date, target keyword)

## Step 5 — Crosslink

After every draft in the set exists, do one pass (this step needs the full set, so it's not parallelized) inserting the internal links from the plan's linking map: pillar ↔ clusters, and links to existing posts named at the interview.

## Step 6 — QA gate (hard stop)

Check every draft against the full checklist in `references/quality-gates.md`. **If any item fails on any article, do not hand off.** Report exactly what's missing per article, fix it, and re-check. This gate cannot be skipped or soft-passed.

## Step 7 — CMS handoff

Once all drafts pass QA, hand each one to the `cms-drafting` skill. Always pushes as **draft** status — never published.

## Step 8 — Human-in-the-loop

After the push, message the user with the list of articles pushed and their CMS draft edit URLs. Ask them to review, approve, or send edits in chat. Never auto-publish, and never re-push a publish action on their behalf even if they say "looks good" — publishing happens in their CMS, by them.

## Notes

- If the user asks for a monthly competitor audit for this project, hand off to `seo-audit-cron` — it documents how to register the recurring check.
- If the user only wants one article (no cluster), Steps 3–6 still apply but with a single node instead of a pillar+cluster set — the word-count and quality gates are unchanged.
