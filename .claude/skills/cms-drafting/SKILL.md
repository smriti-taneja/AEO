---
name: cms-drafting
description: Push a finished, QA-passed blog or landing-page draft to a project's CMS (Webflow, WordPress, or Ghost) as a DRAFT — never publishes. Idempotent — updates the existing draft by slug instead of creating a duplicate. Handles asset upload, author assignment, and metadata. Use after blog-pipeline's QA gate passes, or standalone for "push this draft to [CMS]".
---

# CMS Drafting

Generic across CMS platforms — which one to use comes from the project config, not from this skill. Never call a publish endpoint. Ever. If the user says "push it live," push it as a draft and tell them to publish it themselves from the CMS — this skill does not have a path to publishing.

## Required project config

Read from `config/<slug>.json` (see `config/project.example.json` for the shape):
```json
{
  "cms": "webflow | wordpress | ghost",
  "cms_config": { "...platform-specific ids/urls..." }
}
```
Credentials are never stored in this config or committed anywhere — they come from environment variables named in `cms_config` (e.g. `WEBFLOW_API_TOKEN`). If the env var isn't set, stop and ask the user for it rather than guessing or proceeding without auth.

## Steps

1. **Read the draft** — front-matter must include title, meta title (≤60 chars), meta description (≤160 chars), author, slug, last-updated date, and body HTML/markdown. If any are missing, this is a QA-gate failure upstream — send it back to `blog-pipeline`'s QA step rather than filling in placeholders here.
2. **Upload assets first** (if any images) — get hosted URLs, then substitute them into the body before pushing the item itself.
3. **Look up by slug** — check whether an item/post with this slug already exists in the target collection/site.
   - Exists → **update it** (PATCH/PUT). Never create a second item for the same slug.
   - Doesn't exist → **create it**, with draft/unpublished status set explicitly.
4. **Assign the named author** from the front-matter (create/select the author reference the platform expects — a CMS user, an author collection reference, whatever the platform's `_push.py` script implements).
5. **Never call the platform's publish/go-live endpoint.** Draft status only, always.

## Platform scripts

- `scripts/cms/webflow_push.py` — Webflow CMS API v2, `isDraft: true`, idempotent by slug within a collection.
- `scripts/cms/wordpress_push.py` — WP REST API, `status: "draft"`, idempotent by `?slug=` lookup.
- `scripts/cms/ghost_push.py` — Ghost Admin API, `status: "draft"`, idempotent by slug lookup.

Each script takes a JSON payload (draft + metadata + asset paths) on stdin and prints back the resulting item ID and CMS edit URL. Run the one matching `cms_config.platform`, with credentials only from environment variables — never pass secrets as CLI args (they'd land in shell history/process listing).

## After push

Report back to `blog-pipeline` (or the user, if run standalone): which articles were created vs. updated, and the direct edit URL for each in the CMS, so the human-in-the-loop review step has something concrete to open.
