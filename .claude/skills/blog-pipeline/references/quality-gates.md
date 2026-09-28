# Quality gates — refuse to hand off if any fail

Check every one of these, per article, before CMS handoff. Any single failure blocks the whole handoff for that article.

- [ ] **Word count** — pillar ≥ 2000 words, each cluster ≥ 800 words.
- [ ] **Meta title** ≤ 60 characters.
- [ ] **Meta description** ≤ 160 characters.
- [ ] **At least 2 authority sources** per article, cited inline (not just a link dump at the bottom).
- [ ] **Every image has alt text.**
- [ ] **No em dashes anywhere** (`—` or `--` used as a dash). Rewrite with a period, comma, or restructured sentence.
- [ ] **Every H2 starts with a 40–60 word direct-answer paragraph** — the reader (or an LLM extracting the section) gets the answer before any elaboration.
- [ ] **TL;DR present at the top.**
- [ ] **FAQ present at the bottom**, with FAQ JSON-LD schema markup included in the draft's front-matter or an appended `<script type="application/ld+json">` block.
- [ ] **Named author** (not "the team" or the brand name) and a **last-updated date**.
- [ ] **Query-pattern H2s** somewhere in the structure ("What is X?", "How does X work?", "X vs Y") — not every H2 needs this, but the piece should have at least a few that match how people actually phrase questions to an LLM.
- [ ] **Stat-dense with inline citations** — claims backed by a number and a source, not vague assertions.
- [ ] **Differentiation check passed** — this draft doesn't share structure, examples, or phrasing with another draft in the same cluster (the `copywriting` skill runs this).

If a gate fails, name exactly which one and which article, fix it, and re-run this checklist before proceeding. Do not proceed to Step 7 with a known failure "to save time."
