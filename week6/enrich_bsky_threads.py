"""
enrich_bsky_threads.py
----------------------
Enriches an existing Bluesky CSV (default: bsky_posts_collected.csv) by pulling
the full reply tree and all quote-posts for the top-N viral posts.

Why this exists:
- The query-based collector captures only posts that match search terms, so a
  viral root post's replies/quotes rarely end up in the CSV. That makes any
  propagation analysis (e.g. Section 4b Sankey) look sparse.
- This script fixes that by calling app.bsky.feed.getPostThread and
  app.bsky.feed.getQuotes for the top-N viral roots and appending every new
  post it finds, using the same flattened column schema as collect_bsky.py.

Endpoints (public XRPC, no auth required for public posts):
- /xrpc/app.bsky.feed.getPostThread
- /xrpc/app.bsky.feed.getQuotes

Usage:
    python enrich_bsky_threads.py
    python enrich_bsky_threads.py --top 5 --dry-run
    python enrich_bsky_threads.py --in bsky_posts_collected.csv --out bsky_posts_collected.csv

Outputs:
- Appends new rows to --out (default = --in). Makes a one-shot
  bsky_posts_collected.backup.csv before the first append.
- Writes bsky_enrichment_lineage.csv with one row per viral source, listing
  how many replies/quotes were fetched, kept, and skipped.

Environment:
    BSKY_ACCESS_JWT — optional bearer token; not required for public posts.
"""

from __future__ import annotations

import argparse
import os
import shutil
import time
from dataclasses import dataclass
from typing import Any

import pandas as pd
import requests

API_BASE_URLS = [
    "https://public.api.bsky.app",
    "https://api.bsky.app",
]
THREAD_PATH = "/xrpc/app.bsky.feed.getPostThread"
QUOTES_PATH = "/xrpc/app.bsky.feed.getQuotes"

DEFAULT_THREAD_DEPTH = 10  # how deep to walk reply tree
DEFAULT_QUOTES_LIMIT = 100  # API max per page
REQUEST_SLEEP_S = 0.4  # polite pacing between calls
RATE_LIMIT_SLEEP_S = 30  # back off on 429


@dataclass
class FetchStats:
    viral_uri: str
    viral_handle: str
    viral_engagement: int
    replies_fetched: int = 0
    replies_kept: int = 0
    quotes_fetched: int = 0
    quotes_kept: int = 0
    api_calls: int = 0


def session_headers() -> dict[str, str]:
    h = {"Accept": "application/json", "User-Agent": "enrich-bsky-threads/1.0"}
    token = os.getenv("BSKY_ACCESS_JWT", "").strip()
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def call_xrpc(
    session: requests.Session,
    path: str,
    params: dict[str, Any],
) -> dict[str, Any] | None:
    """GET an XRPC endpoint with host failover + 429 backoff."""
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
            return resp.json()
        if resp.status_code in (403, 502, 503):
            print(f"    {base} returned {resp.status_code}, trying next host")
            continue
        print(f"    API error {resp.status_code}: {resp.text[:200]}")
        return None
    return None


def walk_thread(node: dict[str, Any], collected: list[dict[str, Any]]) -> None:
    """Depth-first collect every `post` payload from a getPostThread response."""
    if not isinstance(node, dict):
        return
    ntype = node.get("$type", "")
    if "notFound" in ntype or "blocked" in ntype:
        return
    post = node.get("post")
    if isinstance(post, dict):
        collected.append(post)
    for reply in node.get("replies") or []:
        walk_thread(reply, collected)


def fetch_replies(session: requests.Session, uri: str) -> tuple[list[dict], int]:
    """Return (list of post dicts excluding the root, number of API calls)."""
    data = call_xrpc(
        session, THREAD_PATH, {"uri": uri, "depth": DEFAULT_THREAD_DEPTH}
    )
    if data is None or "thread" not in data:
        return [], 1
    collected: list[dict] = []
    walk_thread(data["thread"], collected)
    # drop the root post itself
    out = [p for p in collected if p.get("uri") != uri]
    return out, 1


def fetch_quotes(session: requests.Session, uri: str) -> tuple[list[dict], int]:
    """Page through getQuotes and return (all quote-post dicts, calls made)."""
    all_posts: list[dict] = []
    cursor: str | None = None
    calls = 0
    while True:
        params: dict[str, Any] = {"uri": uri, "limit": DEFAULT_QUOTES_LIMIT}
        if cursor:
            params["cursor"] = cursor
        data = call_xrpc(session, QUOTES_PATH, params)
        calls += 1
        if data is None:
            break
        batch = data.get("posts") or []
        all_posts.extend(batch)
        cursor = data.get("cursor")
        if not cursor or not batch:
            break
        time.sleep(REQUEST_SLEEP_S)
    return all_posts, calls


def flatten(
    post: dict[str, Any], viral_uri: str, kind: str
) -> dict[str, Any]:
    """Flatten one post payload to a row matching collect_bsky.py's schema."""
    flat = pd.json_normalize(post, sep=".").to_dict(orient="records")[0]
    flat["collect_primary_theme"] = "_enrichment"
    flat["collect_primary_topic_group"] = "_enrichment"
    flat["collect_primary_query"] = ""
    flat["collect_all_themes"] = f"_enrichment;{kind};{viral_uri}"
    flat["collect_all_topic_groups"] = "_enrichment"
    flat["collect_all_queries"] = ""
    flat["collect_n_search_hits"] = 1
    return flat


def pick_top_viral_roots(df: pd.DataFrame, top_n: int) -> pd.DataFrame:
    for c in ("likeCount", "repostCount", "replyCount", "quoteCount"):
        if c not in df.columns:
            df[c] = 0
    df["_engagement"] = (
        df[["likeCount", "repostCount", "replyCount", "quoteCount"]]
        .fillna(0).astype(float).sum(axis=1)
    )
    parent_col = "record.reply.parent.uri"
    is_root = df[parent_col].isna() if parent_col in df.columns else pd.Series([True] * len(df))
    return df[is_root].nlargest(top_n, "_engagement").copy()


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--in", dest="in_path", default="bsky_posts_collected.csv")
    p.add_argument("--out", dest="out_path", default=None,
                   help="Defaults to --in (append mode).")
    p.add_argument("--top", type=int, default=20,
                   help="Number of viral root posts to enrich (default 20).")
    p.add_argument("--dry-run", action="store_true",
                   help="Fetch + report only; do not write to CSV.")
    p.add_argument("--no-quotes", action="store_true",
                   help="Skip getQuotes; only fetch replies.")
    p.add_argument("--no-replies", action="store_true",
                   help="Skip getPostThread; only fetch quotes.")
    args = p.parse_args()

    in_path = args.in_path
    out_path = args.out_path or in_path

    if not os.path.exists(in_path):
        raise SystemExit(f"Input CSV not found: {in_path}")

    print(f"Reading {in_path}...")
    existing = pd.read_csv(in_path, low_memory=False)
    existing_uris = set(existing.get("uri", pd.Series(dtype=str)).dropna().astype(str))
    print(f"  rows: {len(existing):,}  unique uris: {len(existing_uris):,}")

    virals = pick_top_viral_roots(existing, args.top)
    print(f"\nTop {len(virals)} viral root posts to enrich:")
    for _, r in virals.iterrows():
        handle = str(r.get("author.handle", ""))
        preview = str(r.get("record.text", ""))[:60].replace("\n", " ")
        print(f"  eng={int(r['_engagement']):>6} @{handle:<28} {preview!r}")

    session = requests.Session()
    session.headers.update(session_headers())

    new_rows: list[dict[str, Any]] = []
    stats: list[FetchStats] = []
    total_calls = 0

    for i, (_, viral) in enumerate(virals.iterrows(), 1):
        uri = str(viral.get("uri", ""))
        if not uri:
            continue
        s = FetchStats(
            viral_uri=uri,
            viral_handle=str(viral.get("author.handle", "")),
            viral_engagement=int(viral["_engagement"]),
        )
        print(f"\n[{i}/{len(virals)}] @{s.viral_handle}  eng={s.viral_engagement:,}")

        if not args.no_replies:
            replies, calls = fetch_replies(session, uri)
            total_calls += calls
            s.api_calls += calls
            s.replies_fetched = len(replies)
            for post in replies:
                u = str(post.get("uri", ""))
                if not u or u in existing_uris:
                    continue
                new_rows.append(flatten(post, uri, "reply"))
                existing_uris.add(u)
                s.replies_kept += 1
            print(f"    replies: fetched={s.replies_fetched} new={s.replies_kept}")
            time.sleep(REQUEST_SLEEP_S)

        if not args.no_quotes:
            quotes, calls = fetch_quotes(session, uri)
            total_calls += calls
            s.api_calls += calls
            s.quotes_fetched = len(quotes)
            for post in quotes:
                u = str(post.get("uri", ""))
                if not u or u in existing_uris:
                    continue
                new_rows.append(flatten(post, uri, "quote"))
                existing_uris.add(u)
                s.quotes_kept += 1
            print(f"    quotes:  fetched={s.quotes_fetched} new={s.quotes_kept}")
            time.sleep(REQUEST_SLEEP_S)

        stats.append(s)

    print("\n" + "=" * 60)
    print(f"Total API calls: {total_calls}")
    print(f"New rows ready to append: {len(new_rows):,}")

    lineage = pd.DataFrame([s.__dict__ for s in stats])
    if not args.dry_run:
        lineage.to_csv("bsky_enrichment_lineage.csv", index=False, encoding="utf-8-sig")
        print("Wrote bsky_enrichment_lineage.csv")

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
    combined = pd.concat([existing.drop(columns=["_engagement"], errors="ignore"), new_df],
                         ignore_index=True, sort=False)
    print(f"Writing {out_path}  ({len(combined):,} total rows, "
          f"{len(combined.columns):,} columns)")
    combined.to_csv(out_path, index=False, encoding="utf-8-sig")
    print("Done.")


if __name__ == "__main__":
    main()
