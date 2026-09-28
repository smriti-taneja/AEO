#!/usr/bin/env python3
"""Idempotent draft push to Ghost (Admin API). Never publishes.

Input: a JSON payload on stdin, shape:
{
  "admin_api_url": "https://example.com/ghost/api/admin",
  "admin_api_key_env": "GHOST_ADMIN_API_KEY",   # value is "<id>:<secret>"
  "slug": "...", "title": "...", "html": "...",
  "meta_title": "...", "meta_description": "...",
  "author_email": "jane@example.com"
}

Output: JSON on stdout: {"action": "created|updated", "post_id": "...", "edit_url": "..."}

Requires PyJWT (pip install pyjwt) for Ghost's short-lived Admin API JWT auth.
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error

try:
    import jwt
except ImportError:
    print("Missing dependency: pip install pyjwt", file=sys.stderr)
    sys.exit(1)


def make_token(admin_api_key):
    key_id, secret = admin_api_key.split(":")
    now = int(time.time())
    payload = {"iat": now, "exp": now + 5 * 60, "aud": "/admin/"}
    return jwt.encode(payload, bytes.fromhex(secret), algorithm="HS256", headers={"kid": key_id})


def api_request(method, url, token, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Ghost {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Ghost API {method} {url} failed: {e.code} {e.read().decode()}") from e


def find_existing_post(admin_api_url, token, slug):
    try:
        result = api_request("GET", f"{admin_api_url}/posts/slug/{slug}/?formats=html", token)
        posts = result.get("posts", [])
        return posts[0] if posts else None
    except RuntimeError:
        return None


def main():
    payload = json.load(sys.stdin)
    key_env = payload.get("admin_api_key_env", "GHOST_ADMIN_API_KEY")
    admin_api_key = os.environ.get(key_env)
    if not admin_api_key:
        print(f"Missing env var {key_env} with a Ghost Admin API key (id:secret).", file=sys.stderr)
        sys.exit(1)

    admin_api_url = payload["admin_api_url"].rstrip("/")
    slug = payload["slug"]
    token = make_token(admin_api_key)

    existing = find_existing_post(admin_api_url, token, slug)

    post_body = {
        "posts": [
            {
                "title": payload["title"],
                "slug": slug,
                "html": payload["html"],
                "status": "draft",
                "meta_title": payload.get("meta_title"),
                "meta_description": payload.get("meta_description"),
            }
        ]
    }

    if existing:
        post_id = existing["id"]
        # Ghost requires the current updated_at as a concurrency guard on updates.
        post_body["posts"][0]["updated_at"] = existing["updated_at"]
        post_body["posts"][0]["status"] = "draft" if existing.get("status") != "published" else "published"
        result = api_request(
            "PUT",
            f"{admin_api_url}/posts/{post_id}/?source=html",
            token,
            post_body,
        )
        action = "updated"
    else:
        result = api_request("POST", f"{admin_api_url}/posts/?source=html", token, post_body)
        action = "created"
        post_id = result["posts"][0]["id"]

    site_base = admin_api_url.split("/ghost/api/admin")[0]
    edit_url = f"{site_base}/ghost/#/editor/post/{post_id}"
    print(json.dumps({"action": action, "post_id": post_id, "edit_url": edit_url}))


if __name__ == "__main__":
    main()
