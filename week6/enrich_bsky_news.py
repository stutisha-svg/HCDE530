"""
enrich_bsky_news.py
-------------------
Enriches an existing Bluesky CSV (default: bsky_posts_collected.csv) with
posts from a curated allowlist of news-outlet handles, filtered to those
that mention AI / generative-AI / LLM keywords.

Why this exists:
- The query-based collector returns whatever matches its search terms, so
  posts from specific publishers are sparse and not directly comparable.
- This script pulls every recent post from a hand-picked list of news
  accounts via app.bsky.feed.getAuthorFeed, then keeps the ones that
  mention an AI-related keyword. The result enables outlet-level
  stylistic / certainty / framing analysis (Section 4d).

Endpoint (public XRPC, no auth required for public posts):
- /xrpc/app.bsky.feed.getAuthorFeed

Usage:
    python enrich_bsky_news.py
    python enrich_bsky_news.py --dry-run
    python enrich_bsky_news.py --since 2023-01-01 --max-pages 60
    python enrich_bsky_news.py --in bsky_posts_collected.csv --out bsky_posts_collected.csv

Outputs:
- Appends new rows to --out (default = --in). Uses the existing
  bsky_posts_collected.backup.csv as the one-shot pre-append snapshot
  (created by enrich_bsky_threads.py on its first run, or here if missing).
- Writes bsky_news_enrichment_lineage.csv with one row per outlet:
  api_calls, posts_seen, ai_keyword_hits, dedup_hits_kept, oldest_post_date.

Environment:
    BSKY_ACCESS_JWT — optional bearer token; not required for public posts
                      but raises rate-limit ceiling.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import requests

API_BASE_URLS = [
    "https://public.api.bsky.app",
    "https://api.bsky.app",
]
AUTHOR_FEED_PATH = "/xrpc/app.bsky.feed.getAuthorFeed"

PAGE_LIMIT = 100  # XRPC max per page for getAuthorFeed
DEFAULT_MAX_PAGES = 60  # safety cap per outlet (~6000 posts)
DEFAULT_SINCE_ISO = "2023-01-01T00:00:00Z"
REQUEST_SLEEP_S = 0.4
RATE_LIMIT_SLEEP_S = 30


# Curated allowlist of news handles. Grouped for downstream coloring.
NEWS_OUTLETS: list[tuple[str, str]] = [
    # ---- National / general ------------------------------------------------
    ("propublica.org",          "national"),
    ("theatlantic.com",         "national"),
    ("washingtonpost.com",      "national"),
    ("nytimes.com",             "national"),
    ("fortune.com",             "national"),
    ("bloomberg.com",           "national"),
    ("reuters.com",             "national"),
    ("apnews.com",              "national"),
    ("npr.org",                 "national"),
    ("politico.com",            "national"),
    ("axios.com",               "national"),
    ("theguardian.com",         "national"),
    ("ft.com",                  "national"),
    ("economist.com",           "national"),
    ("businessinsider.com",     "national"),
    ("cnbc.com",                "national"),
    ("newyorker.com",           "national"),
    ("thehill.com",             "national"),
    ("usatoday.com",            "national"),
    ("latimes.com",             "national"),
    # ---- Tech-specialty (typically most active on AI) ----------------------
    ("theverge.com",            "tech"),
    ("arstechnica.com",         "tech"),
    ("techcrunch.com",          "tech"),
    ("wired.com",               "tech"),
    ("404media.co",             "tech"),
    ("theinformation.com",      "tech"),
    ("platformer.news",         "tech"),
    ("semafor.com",             "tech"),
    ("niemanlab.org",           "tech"),
    ("technologyreview.com",    "tech"),
    ("futurism.com",            "tech"),
    ("restofworld.org",         "tech"),
    ("rest-of-world.bsky.social", "tech"),
    # ---- Public-interest / investigative ----------------------------------
    ("themarkup.org",           "investigative"),
    ("propublicaguild.org",     "investigative"),
    ("pogo.org",                "investigative"),
    # ---- Local / regional public radio / TV --------------------------------
    ("kqed.org",                "local"),
    ("wbur.org",                "local"),
    ("wnyc.org",                "local"),
    ("wbez.org",                "local"),
    ("texastribune.org",        "local"),
    ("baltimoresun.com",        "local"),
    ("seattletimes.com",        "local"),
    ("sfchronicle.com",         "local"),
    ("chicagotribune.com",      "local"),
    ("bostonglobe.com",         "local"),
]


AI_KEYWORD_REGEX = re.compile(
    r"\b("
    r"AI|A\.I\.|artificial intelligence|"
    r"LLM|LLMs|large language model|language model|"
    r"chatbot|chatbots|"
    r"ChatGPT|GPT-?\d+|GPT|"
    r"Claude|Gemini|Sora|Midjourney|Stable Diffusion|DALL[- ]?E|"
    r"OpenAI|Anthropic|Meta AI|DeepMind|Mistral|Cohere|xAI|"
    r"Llama\s?\d?|Llama-?\d|"
    r"deepfake|deepfakes|generative AI|gen ?AI|"
    r"machine learning|neural network|"
    r"AGI|superintelligence|"
    r"synthetic media|AI[- ]generated"
    r")\b",
    flags=re.IGNORECASE,
)


@dataclass
class OutletStats:
    handle: str
    group: str
    api_calls: int = 0
    posts_seen: int = 0
    ai_keyword_hits: int = 0
    dedup_hits_kept: int = 0
    pages_fetched: int = 0
    oldest_post_date: str = ""
    newest_post_date: str = ""
    note: str = ""


def session_headers() -> dict[str, str]:
    h = {"Accept": "application/json", "User-Agent": "enrich-bsky-news/1.0"}
    token = os.getenv("BSKY_ACCESS_JWT", "").strip()
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def call_xrpc(
    session: requests.Session,
    path: str,
    params: dict[str, Any],
) -> tuple[dict[str, Any] | None, int]:
    """GET an XRPC endpoint with host failover + 429 backoff.

    Returns (json_or_none, http_status_or_0_for_network_error).
    """
    for base in API_BASE_URLS:
        url = base + path
        try:
            resp = session.get(url, params=params, timeout=25)
        except requests.exceptions.RequestException as e:
            print(f"    Network error ({base}): {e}")
            continue
        if resp.status_code == 429:
            print(f"    Rate limited — sleeping {RATE_LIMIT_SLEEP_S}s")
            time.sleep(RATE_LIMIT_SLEEP_S)
            try:
                resp = session.get(url, params=params, timeout=25)
            except requests.exceptions.RequestException:
                continue
        if resp.status_code == 200:
            return resp.json(), 200
        if resp.status_code in (400, 401, 404):
            # Account not found / no access — don't retry on the other host.
            return None, resp.status_code
        if resp.status_code in (403, 502, 503):
            print(f"    {base} returned {resp.status_code}, trying next host")
            continue
        print(f"    API error {resp.status_code}: {resp.text[:200]}")
        return None, resp.status_code
    return None, 0


def fetch_author_feed(
    session: requests.Session,
    handle: str,
    since_dt: datetime,
    max_pages: int,
    stats: OutletStats,
) -> list[dict[str, Any]]:
    """Page through getAuthorFeed for one handle, stopping at since_dt or max_pages."""
    posts: list[dict[str, Any]] = []
    cursor: str | None = None

    for page in range(max_pages):
        params: dict[str, Any] = {
            "actor": handle,
            "limit": PAGE_LIMIT,
            "filter": "posts_no_replies",  # outlet posts, not their replies
        }
        if cursor:
            params["cursor"] = cursor

        data, status = call_xrpc(session, AUTHOR_FEED_PATH, params)
        stats.api_calls += 1

        if data is None:
            if status in (400, 401, 404):
                stats.note = f"http_{status}"
            elif status == 0:
                stats.note = "network_error"
            else:
                stats.note = f"http_{status}"
            break

        feed = data.get("feed") or []
        if not feed:
            break

        stats.pages_fetched += 1
        page_oldest: datetime | None = None

        for item in feed:
            post = item.get("post") if isinstance(item, dict) else None
            if not isinstance(post, dict):
                continue

            # Only keep posts authored by this handle (skip reposts from others).
            author_handle = (post.get("author", {}) or {}).get("handle", "")
            if author_handle.lower() != handle.lower():
                continue

            indexed_at = post.get("indexedAt") or ""
            try:
                pdt = datetime.fromisoformat(indexed_at.replace("Z", "+00:00"))
            except Exception:
                pdt = None

            if pdt is None:
                continue
            page_oldest = min(page_oldest, pdt) if page_oldest else pdt

            if pdt < since_dt:
                # We've walked past our window — record stats and bail.
                if not stats.oldest_post_date:
                    stats.oldest_post_date = indexed_at
                stats.posts_seen += 1
                continue

            posts.append(post)
            stats.posts_seen += 1
            if not stats.newest_post_date:
                stats.newest_post_date = indexed_at
            stats.oldest_post_date = indexed_at  # updated each iter; ends at smallest

        cursor = data.get("cursor")
        if not cursor:
            break
        if page_oldest is not None and page_oldest < since_dt:
            break
        time.sleep(REQUEST_SLEEP_S)

    return posts


def post_mentions_ai(post: dict[str, Any]) -> bool:
    text = ((post.get("record") or {}).get("text") or "")
    if not isinstance(text, str):
        return False
    return bool(AI_KEYWORD_REGEX.search(text))


def flatten(post: dict[str, Any], outlet: str) -> dict[str, Any]:
    """Flatten one post payload to match collect_bsky.py's schema."""
    flat = pd.json_normalize(post, sep=".").to_dict(orient="records")[0]
    flat["collect_primary_theme"] = "_news_enrichment"
    flat["collect_primary_topic_group"] = "_news_enrichment"
    flat["collect_primary_query"] = ""
    flat["collect_all_themes"] = f"_news_enrichment;{outlet}"
    flat["collect_all_topic_groups"] = "_news_enrichment"
    flat["collect_all_queries"] = ""
    flat["collect_n_search_hits"] = 1
    return flat


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--in", dest="in_path", default="bsky_posts_collected.csv")
    p.add_argument("--out", dest="out_path", default=None,
                   help="Defaults to --in (append mode).")
    p.add_argument("--since", default=DEFAULT_SINCE_ISO,
                   help="ISO date — stop walking each feed once posts go older.")
    p.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES,
                   help=f"Safety cap on pages per outlet (default {DEFAULT_MAX_PAGES}, "
                        f"{PAGE_LIMIT}/page).")
    p.add_argument("--outlets", default=None,
                   help="Comma-separated handle list to restrict the run (debug).")
    p.add_argument("--dry-run", action="store_true",
                   help="Fetch + report only; do not write to CSV.")
    args = p.parse_args()

    in_path = args.in_path
    out_path = args.out_path or in_path

    if not os.path.exists(in_path):
        raise SystemExit(f"Input CSV not found: {in_path}")

    print(f"Reading {in_path}...")
    existing = pd.read_csv(in_path, low_memory=False)
    existing_uris = set(existing.get("uri", pd.Series(dtype=str)).dropna().astype(str))
    print(f"  rows: {len(existing):,}  unique uris: {len(existing_uris):,}")

    since_dt = datetime.fromisoformat(args.since.replace("Z", "+00:00"))
    if since_dt.tzinfo is None:
        since_dt = since_dt.replace(tzinfo=timezone.utc)

    outlets = NEWS_OUTLETS
    if args.outlets:
        wanted = {o.strip().lower() for o in args.outlets.split(",") if o.strip()}
        outlets = [(h, g) for (h, g) in NEWS_OUTLETS if h.lower() in wanted]
        if not outlets:
            raise SystemExit("No --outlets matched the allowlist.")
    print(f"\nOutlets to fetch ({len(outlets)}): "
          f"{', '.join(h for h, _ in outlets[:6])}"
          f"{' ...' if len(outlets) > 6 else ''}")
    print(f"Since: {since_dt.isoformat()}  max_pages/outlet: {args.max_pages}")

    session = requests.Session()
    session.headers.update(session_headers())

    new_rows: list[dict[str, Any]] = []
    all_stats: list[OutletStats] = []

    for i, (handle, group) in enumerate(outlets, 1):
        s = OutletStats(handle=handle, group=group)
        print(f"\n[{i}/{len(outlets)}] @{handle}  ({group})")
        try:
            raw_posts = fetch_author_feed(session, handle, since_dt, args.max_pages, s)
        except Exception as e:
            print(f"    Unexpected error: {e}")
            s.note = f"exception: {type(e).__name__}"
            all_stats.append(s)
            continue

        for post in raw_posts:
            if not post_mentions_ai(post):
                continue
            s.ai_keyword_hits += 1
            u = str(post.get("uri", ""))
            if not u or u in existing_uris:
                continue
            new_rows.append(flatten(post, handle))
            existing_uris.add(u)
            s.dedup_hits_kept += 1

        all_stats.append(s)
        print(f"    pages={s.pages_fetched} api_calls={s.api_calls} "
              f"seen={s.posts_seen} ai_hits={s.ai_keyword_hits} "
              f"kept_new={s.dedup_hits_kept} "
              f"{('NOTE=' + s.note) if s.note else ''}")
        time.sleep(REQUEST_SLEEP_S)

    print("\n" + "=" * 60)
    total_calls = sum(s.api_calls for s in all_stats)
    total_seen = sum(s.posts_seen for s in all_stats)
    total_hits = sum(s.ai_keyword_hits for s in all_stats)
    print(f"Total API calls: {total_calls}")
    print(f"Total posts walked: {total_seen:,}")
    print(f"Total AI-keyword hits: {total_hits:,}")
    print(f"New unique rows to append: {len(new_rows):,}")

    lineage_df = pd.DataFrame([s.__dict__ for s in all_stats])
    if not args.dry_run:
        lineage_df.to_csv("bsky_news_enrichment_lineage.csv",
                          index=False, encoding="utf-8-sig")
        print("Wrote bsky_news_enrichment_lineage.csv")

    if args.dry_run:
        print("\n--dry-run: not writing to CSV.")
        return

    if not new_rows:
        print("Nothing new to append. Done.")
        return

    backup_path = in_path.replace(".csv", ".backup.csv")
    if not os.path.exists(backup_path):
        print(f"Backing up {in_path} -> {backup_path}")
        shutil.copy2(in_path, backup_path)

    new_df = pd.DataFrame(new_rows)
    combined = pd.concat(
        [existing.drop(columns=["_engagement"], errors="ignore"), new_df],
        ignore_index=True, sort=False,
    )
    print(f"Writing {out_path}  ({len(combined):,} total rows, "
          f"{len(combined.columns):,} columns)")
    combined.to_csv(out_path, index=False, encoding="utf-8-sig")
    print("Done.")


if __name__ == "__main__":
    main()
