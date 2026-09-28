---
name: copywriting
description: Brand-voice enforcement and copy-editing for any blog or landing-page draft — banned phrases, no em dashes, no generic unsourced stats, and a differentiation check so no two pieces in a cluster read the same. Use when drafting or editing content produced by blog-pipeline, or standalone for "edit this for voice" / "check this draft" requests. Voice rules come from the active project's brain, not a hardcoded style.
---

# Copywriting + Copy-Editing

Enforces a specific brand's voice on a draft. The rules themselves live in the project's vault, not in this skill — read them fresh each time instead of assuming a house style.

## Before editing

Read from the active vault:
- `wiki/voice/tone-of-voice.md` — tone, sentence rhythm, POV, examples of on-voice writing
- `wiki/voice/banned-phrases.md` — words/phrases never to use
- `wiki/voice/approved-stats.md` — stats this brand is allowed to cite as its own

If these files are still template placeholders (vault just scaffolded), fall back to the hard rules below and flag to the user that voice rules haven't been customized yet.

## Hard rules (apply regardless of what's in the vault)

- **No em dashes anywhere** — not `—`, not `--` used as a dash. Rewrite with a period, a comma, or a restructured sentence. Check every draft for this specifically; it's the single most common tell.
- **No fluff openers** ("In today's fast-paced world...", "In this article, we'll explore...").
- **No generic analyst stats** — no "studies show", "experts agree", "research indicates" without a specific, named, linked source. If a stat isn't in `wiki/voice/approved-stats.md` and wasn't freshly sourced with a citation during research, cut it rather than leave it vague.
- **No banned vocabulary** from the vault's list, plus the common AI-tell words (leverage, unlock, seamless, robust, game-changer, dive into, unpack, elevate) unless the vault explicitly allows one.

## Differentiation check (cluster-level, not per-article)

Once all drafts in a cluster exist, compare them against each other:
- Same structure (identical H2 pattern, same order of points)?
- Same examples or analogies reused across pieces?
- Same opening/closing pattern?

If any of these show up across two or more drafts, rewrite the weaker one's structure or examples until each piece has its own shape. A pillar and its clusters should read like they were written by someone who deeply understands the topic from multiple angles, not like a template filled in four times.

## Delegation

- Base drafting ruleset (structure, research-to-prose process, the full anti-AI-slop vocabulary/phrase list): use the `write-content` skill.
- Final AI-tell removal pass (passive voice, inflated symbolism, negative parallelisms, rule-of-three padding): use the `humanizer` skill.

This skill's job is the brand-specific layer on top of those two: what's on-voice for *this* brand, and making sure a cluster doesn't read as repetitive.
