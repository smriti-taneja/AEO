#!/usr/bin/env python3
"""Monthly competitor SEO/AEO audit using Firecrawl.

Usage:
  firecrawl_audit.py --project <slug> --config config/<slug>.json [--vault /path/to/vault]

For each keyword in the project config's target_keywords:
  1. Firecrawl search for the top-ranking pages.
  2. Scrape each result for title, word count, heading structure, and notable claims/stats.
  3. Write a dated markdown report to <vault>/wiki/seo/ranking-reports/.
  4. Append a rolling summary row to <vault>/wiki/seo/competitor-analysis.md.

Requires FIRECRAWL_API_KEY (or the project's configured firecrawl_api_key_env) in the environment.
"""
import argparse
import datetime
import json
import os
import re
import sys
import urllib.request
import urllib.error

FIRECRAWL_BASE = "https://api.firecrawl.dev/v1"


def api_request(method, path, api_key, body=None):
    url = f"{FIRECRAWL_BASE}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Firecrawl API {method} {path} failed: {e.code} {e.read().decode()}") from e


def search_top_pages(api_key, keyword, limit=10):
    result = api_request("POST", "/search", api_key, {"query": keyword, "limit": limit})
    return [r["url"] for r in result.get("data", [])]


def scrape_page(api_key, url):
    result = api_request(
        "POST",
        "/scrape",
        api_key,
        {"url": url, "formats": ["markdown"]},
    )
    return result.get("data", {})


def analyze_page(url, scraped):
    markdown = scraped.get("markdown", "") or ""
    metadata = scraped.get("metadata", {}) or {}
    word_count = len(markdown.split())
    headings = re.findall(r"^(#{2,3})\s+(.+)$", markdown, flags=re.MULTILINE)
    stats = re.findall(r"[\d,]+(?:\.\d+)?%|\$[\d,]+(?:\.\d+)?[MBK]?", markdown)
    has_faq_schema = "FAQPage" in markdown or "faqpage" in markdown.lower()
    return {
        "url": url,
        "title": metadata.get("title", ""),
        "word_count": word_count,
        "headings": [f"{level} {text}" for level, text in headings[:20]],
        "stat_mentions": stats[:15],
        "has_faq_schema_hint": has_faq_schema,
    }


def write_report(vault_path, keyword, pages):
    date_str = datetime.date.today().isoformat()
    keyword_slug = re.sub(r"[^a-z0-9]+", "-", keyword.lower()).strip("-")
    report_dir = os.path.join(vault_path, "wiki", "seo", "ranking-reports")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"{date_str}-{keyword_slug}.md")

    lines = [f"# SEO/AEO audit: {keyword}", "", f"Run date: {date_str}", ""]
    for p in pages:
        lines.append(f"## {p['title'] or p['url']}")
        lines.append(f"- URL: {p['url']}")
        lines.append(f"- Word count: {p['word_count']}")
        lines.append(f"- FAQ schema hint: {'yes' if p['has_faq_schema_hint'] else 'no'}")
        if p["headings"]:
            lines.append("- Structure:")
            for h in p["headings"]:
                lines.append(f"  - {h}")
        if p["stat_mentions"]:
            lines.append(f"- Stats/numbers cited: {', '.join(p['stat_mentions'])}")
        lines.append("")

    avg_wc = round(sum(p["word_count"] for p in pages) / len(pages)) if pages else 0
    faq_count = sum(1 for p in pages if p["has_faq_schema_hint"])
    lines.append("## Gaps and opportunities")
    lines.append(f"- Average competitor word count: {avg_wc}")
    lines.append(f"- {faq_count}/{len(pages)} top results show FAQ schema — {'a gap to exploit' if faq_count < len(pages) else 'table stakes here'}")
    lines.append("- Review headings above for query-pattern H2s ('what is', 'how does', 'vs') competitors are or aren't using.")
    lines.append("")

    with open(report_path, "w") as f:
        f.write("\n".join(lines))

    return report_path, avg_wc, faq_count


def append_summary(vault_path, keyword, report_path, avg_wc, faq_count, page_count):
    summary_path = os.path.join(vault_path, "wiki", "seo", "competitor-analysis.md")
    date_str = datetime.date.today().isoformat()
    row = f"| {date_str} | {keyword} | {avg_wc} | {faq_count}/{page_count} | [{os.path.basename(report_path)}]({report_path}) |\n"

    header = "| Date | Keyword | Avg. competitor word count | FAQ schema present | Full report |\n|---|---|---|---|---|\n"
    if not os.path.exists(summary_path) or header.split("\n")[0] not in open(summary_path).read():
        os.makedirs(os.path.dirname(summary_path), exist_ok=True)
        with open(summary_path, "a") as f:
            f.write(header)
    with open(summary_path, "a") as f:
        f.write(row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--vault", help="Override vault_path from config")
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    api_key_env = config.get("firecrawl_api_key_env", "FIRECRAWL_API_KEY")
    api_key = os.environ.get(api_key_env)
    if not api_key:
        print(f"Missing env var {api_key_env} with a Firecrawl API key.", file=sys.stderr)
        sys.exit(1)

    vault_path = os.path.expanduser(args.vault or config["vault_path"])
    keywords = config.get("target_keywords", [])
    if not keywords:
        print("No target_keywords in project config — nothing to audit.", file=sys.stderr)
        sys.exit(1)

    for keyword in keywords:
        print(f"Auditing: {keyword}", file=sys.stderr)
        urls = search_top_pages(api_key, keyword)
        pages = []
        for url in urls:
            try:
                scraped = scrape_page(api_key, url)
                pages.append(analyze_page(url, scraped))
            except RuntimeError as e:
                print(f"  skip {url}: {e}", file=sys.stderr)
        if not pages:
            continue
        report_path, avg_wc, faq_count = write_report(vault_path, keyword, pages)
        append_summary(vault_path, keyword, report_path, avg_wc, faq_count, len(pages))
        print(f"  wrote {report_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
