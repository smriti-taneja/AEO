#!/usr/bin/env python3
"""Idempotent draft push to WordPress (REST API). Never publishes.

Input: a JSON payload on stdin, shape:
{
  "base_url": "https://example.com", "user": "...", "app_password_env": "WORDPRESS_APP_PASSWORD",
  "slug": "...", "title": "...", "content_html": "...", "excerpt": "...",
  "author_id": 1, "meta": {"title": "...", "description": "..."}
}

Output: JSON on stdout: {"action": "created|updated", "post_id": ..., "edit_url": "..."}
"""
import base64
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse


def api_request(method, url, auth_header, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", auth_header)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"WordPress API {method} {url} failed: {e.code} {e.read().decode()}") from e


def find_existing_post(base_url, auth_header, slug):
    q = urllib.parse.urlencode({"slug": slug, "status": "draft,publish,pending,future"})
    results = api_request("GET", f"{base_url}/wp-json/wp/v2/posts?{q}", auth_header)
    return results[0] if results else None


def main():
    payload = json.load(sys.stdin)
    pw_env = payload.get("app_password_env", "WORDPRESS_APP_PASSWORD")
    app_password = os.environ.get(pw_env)
    if not app_password:
        print(f"Missing env var {pw_env} with a WordPress application password.", file=sys.stderr)
        sys.exit(1)

    base_url = payload["base_url"].rstrip("/")
    user = payload["user"]
    slug = payload["slug"]

    token = base64.b64encode(f"{user}:{app_password}".encode()).decode()
    auth_header = f"Basic {token}"

    body = {
        "title": payload["title"],
        "content": payload["content_html"],
        "slug": slug,
        "status": "draft",
        "excerpt": payload.get("excerpt", ""),
    }
    if "author_id" in payload:
        body["author"] = payload["author_id"]
    if "meta" in payload:
        body["meta"] = payload["meta"]

    existing = find_existing_post(base_url, auth_header, slug)

    if existing:
        post_id = existing["id"]
        body["status"] = existing.get("status", "draft") if existing.get("status") == "publish" else "draft"
        api_request("POST", f"{base_url}/wp-json/wp/v2/posts/{post_id}", auth_header, body)
        action = "updated"
    else:
        result = api_request("POST", f"{base_url}/wp-json/wp/v2/posts", auth_header, body)
        post_id = result["id"]
        action = "created"

    edit_url = f"{base_url}/wp-admin/post.php?post={post_id}&action=edit"
    print(json.dumps({"action": action, "post_id": post_id, "edit_url": edit_url}))


if __name__ == "__main__":
    main()
