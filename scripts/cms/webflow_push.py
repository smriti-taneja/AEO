#!/usr/bin/env python3
"""Idempotent draft push to Webflow CMS (API v2). Never publishes.

Input: a JSON payload on stdin, shape:
{
  "site_id": "...", "collection_id": "...", "token_env": "WEBFLOW_API_TOKEN",
  "slug": "...", "fields": { "name": "...", "post-body": "...", ... },
  "assets": [{"path": "/local/or/remote/image.png", "alt": "..."}]
}
"fields" maps directly onto Webflow's fieldData (minus slug, which is handled here).

Output: JSON on stdout: {"action": "created|updated", "item_id": "...", "edit_url": "..."}
"""
import json
import os
import sys
import urllib.request
import urllib.error

API_BASE = "https://api.webflow.com/v2"


def api_request(method, path, token, body=None):
    url = f"{API_BASE}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("accept", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Webflow API {method} {path} failed: {e.code} {e.read().decode()}") from e


def find_existing_item(token, collection_id, slug):
    offset = 0
    while True:
        page = api_request("GET", f"/collections/{collection_id}/items?limit=100&offset={offset}", token)
        items = page.get("items", [])
        for item in items:
            if item.get("fieldData", {}).get("slug") == slug:
                return item
        if len(items) < 100:
            return None
        offset += 100


def upload_asset(token, site_id, local_path):
    # Webflow assets require a two-step upload (metadata call, then upload to the returned S3 URL).
    # Left as a documented extension point — most drafts here are pushed with already-hosted image URLs
    # from the research/asset step, so this only runs when a raw local file is passed.
    raise NotImplementedError(
        "Local asset upload not wired up yet — host the image (e.g. via the CMS media library or a CDN) "
        "and pass its URL directly in fields instead of a local path."
    )


def main():
    payload = json.load(sys.stdin)
    token_env = payload.get("token_env", "WEBFLOW_API_TOKEN")
    token = os.environ.get(token_env)
    if not token:
        print(f"Missing env var {token_env} with a Webflow API token.", file=sys.stderr)
        sys.exit(1)

    site_id = payload["site_id"]
    collection_id = payload["collection_id"]
    slug = payload["slug"]
    fields = dict(payload.get("fields", {}))
    fields["slug"] = slug

    for asset in payload.get("assets", []):
        if asset["path"].startswith("http://") or asset["path"].startswith("https://"):
            continue
        upload_asset(token, site_id, asset["path"])

    existing = find_existing_item(token, collection_id, slug)

    body = {"isDraft": True, "isArchived": False, "fieldData": fields}

    if existing:
        item_id = existing["id"]
        api_request("PATCH", f"/collections/{collection_id}/items/{item_id}", token, body)
        action = "updated"
    else:
        result = api_request("POST", f"/collections/{collection_id}/items", token, body)
        item_id = result["id"]
        action = "created"

    edit_url = f"https://webflow.com/dashboard/sites/{site_id}/collections/{collection_id}/items/{item_id}"
    print(json.dumps({"action": action, "item_id": item_id, "edit_url": edit_url}))


if __name__ == "__main__":
    main()
