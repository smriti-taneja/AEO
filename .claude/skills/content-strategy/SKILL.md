---
name: content-strategy
description: Pillar/cluster topic planning, search-intent mapping, and internal-linking architecture for a content cluster. Invoked by blog-pipeline's plan step, or standalone for "plan a content cluster", "map search intent", "how should I structure this topic" requests. Works for any brand — takes the topic and brand context as input.
---

# Content Strategy

Turns a brief (target keyword, audience, competitors, unique angle) into a concrete pillar/cluster plan. This wraps the `topic-cluster-planning` skill for hub/spoke research and `fanout-mapper` for AEO sub-query coverage — use both, don't re-derive their methodology from scratch.

## Process

1. **Hub/spoke research** — hand the seed keyword to `topic-cluster-planning`. Get the hub topic and candidate spokes back.
2. **Fan-out coverage** — hand the same keyword (plus domain, if known) to `fanout-mapper` to see what sub-queries AI systems actually fire for this topic. Cross-reference against the spokes from step 1 — this catches AEO-relevant angles that pure SERP-based clustering misses.
3. **Narrow to 3–4 clusters.** More than 4 dilutes the pillar's link equity and is rarely deliverable in one session. Fewer than 3 usually means the topic doesn't need a cluster — say so instead of forcing it.
4. **Classify intent per node** (pillar and each cluster): informational, comparison, or decision. This determines structure — a decision-intent cluster needs pricing/specs/CTAs; an informational one needs depth and PAA coverage.
5. **Set word-count targets** — pillar ≥ 2000 words, each cluster ≥ 800 words. Never negotiate these down to hit a deadline; negotiate the cluster count instead.
6. **Build the internal-linking matrix** — every cluster links up to the pillar with descriptive (not "click here") anchor text; the pillar links down to every cluster in the relevant section; clusters cross-link where genuinely relevant (not forced). Include links to the existing posts the user named at the interview.
7. **Check for angle overlap** — if two clusters would answer the same underlying question, merge them or sharpen the angles until they're clearly distinct. This is checked again later by `copywriting`'s differentiation pass, but catching it at the planning stage saves a rewrite.

Output: a plan with one row per node — title, target query, intent, angle, word-count target, links in/out. This is what `blog-pipeline` saves to `pipelines/blog/<slug>/plan.md`.
