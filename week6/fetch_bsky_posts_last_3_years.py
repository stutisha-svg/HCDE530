from __future__ import annotations

from datetime import datetime, timezone
import argparse
import getpass
import os
import random
import sys
import time

import pandas as pd
import requests


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch Bluesky posts and export flattened CSV attributes."
    )
    parser.add_argument("--query", default="*", help="Primary search query.")
    parser.add_argument(
        "--target-rows",
        type=int,
        default=5000,
        help="Target number of unique rows to save.",
    )
    parser.add_argument(
        "--max-pages-per-query",
        type=int,
        default=80,
        help="Max cursor pages to fetch for each query seed.",
    )
    parser.add_argument(
        "--pause-seconds",
        type=float,
        default=0.5,
        help="Pause between requests to reduce throttling.",
    )
    parser.add_argument(
        "--output",
        default="bsky_posts_last_3_years.csv",
        help="Output CSV for flattened post rows.",
    )
    parser.add_argument(
        "--attributes-output",
        default="bsky_post_attributes.csv",
        help="Output CSV listing all attribute names.",
    )
    parser.add_argument("--identifier", default="", help="Handle/email for login.")
    parser.add_argument("--app-password", default="", help="Bluesky app password.")
    return parser.parse_args()


def cutoff_three_years_utc() -> datetime:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    return now.replace(year=now.year - 3)


def get_credentials(args: argparse.Namespace) -> tuple[str, str]:
    identifier = args.identifier or os.getenv("BSKY_IDENTIFIER", "").strip()
    app_password = args.app_password or os.getenv("BSKY_APP_PASSWORD", "").strip()

    if not identifier:
        identifier = input("Bluesky identifier (handle/email): ").strip()
    if not app_password:
        app_password = getpass.getpass("Bluesky app password: ").strip()
    return identifier, app_password


def create_session_token(identifier: str, app_password: str) -> str:
    url = "https://bsky.social/xrpc/com.atproto.server.createSession"
    payload = {"identifier": identifier, "password": app_password}
    resp = requests.post(url, json=payload, timeout=30)
    if resp.status_code != 200:
        try:
            msg = resp.json()
        except Exception:
            msg = resp.text[:200]
        raise RuntimeError(f"Login failed ({resp.status_code}): {msg}")
    data = resp.json()
    token = data.get("accessJwt", "")
    if not token:
        raise RuntimeError("Login succeeded but no accessJwt returned.")
    return token


def parse_post_time(post: dict) -> datetime | None:
    ts = (post.get("record") or {}).get("createdAt") or post.get("indexedAt")
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def fetch_query_stream(
    session: requests.Session,
    query: str,
    max_pages: int,
    pause_seconds: float,
) -> tuple[list[dict], int]:
    base_url = "https://api.bsky.app/xrpc/app.bsky.feed.searchPosts"
    cursor = None
    posts: list[dict] = []
    pages = 0
    retry_count = 0
    seen_cursors: set[str] = set()

    while pages < max_pages:
        params = {"q": query, "sort": "latest", "limit": 100}
        if cursor:
            params["cursor"] = cursor

        resp = session.get(base_url, params=params, timeout=45)
        if resp.status_code != 200:
            retry_count += 1
            if resp.status_code in (403, 429) and retry_count <= 6:
                sleep_s = min(60, (2 ** retry_count) + random.random())
                print(
                    f"query='{query}' HTTP {resp.status_code}, retry {retry_count} in {sleep_s:.1f}s"
                )
                time.sleep(sleep_s)
                continue
            print(f"query='{query}' stopped on HTTP {resp.status_code}")
            break

        retry_count = 0
        data = resp.json()
        batch = data.get("posts", [])
        if not batch:
            break

        posts.extend(batch)
        pages += 1
        next_cursor = data.get("cursor")
        if not next_cursor or next_cursor in seen_cursors:
            break
        seen_cursors.add(next_cursor)
        cursor = next_cursor
        time.sleep(pause_seconds)

    return posts, pages


def main() -> None:
    args = parse_args()
    cutoff = cutoff_three_years_utc()
    identifier, app_password = get_credentials(args)

    try:
        token = create_session_token(identifier, app_password)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        print(
            "Use your Bluesky App Password (not account password) and full handle "
            "like 'name.bsky.social'."
        )
        sys.exit(1)

    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "bsky-post-export/1.0",
        }
    )

    query_seeds = [
        args.query,
        "news",
        "today",
        "tech",
        "art",
        "music",
        "science",
        "sports",
        "politics",
        "data",
        "the",
        "a",
        "i",
    ]

    total_fetched = 0
    total_pages = 0
    unique_posts: list[dict] = []
    seen_uris: set[str] = set()

    for query in query_seeds:
        if len(unique_posts) >= args.target_rows:
            break
        stream_posts, pages = fetch_query_stream(
            session=session,
            query=query,
            max_pages=args.max_pages_per_query,
            pause_seconds=args.pause_seconds,
        )
        total_pages += pages
        total_fetched += len(stream_posts)

        for post in stream_posts:
            dt = parse_post_time(post)
            if dt is not None and dt < cutoff:
                continue
            uri = post.get("uri", "")
            if uri and uri not in seen_uris:
                seen_uris.add(uri)
                unique_posts.append(post)
                if len(unique_posts) >= args.target_rows:
                    break
        print(
            f"query='{query}' pages={pages} total_unique={len(unique_posts)}"
        )

    df = pd.json_normalize(unique_posts[: args.target_rows], sep=".")
    df.to_csv(args.output, index=False, encoding="utf-8-sig")
    pd.DataFrame({"attribute": df.columns}).to_csv(
        args.attributes_output, index=False, encoding="utf-8-sig"
    )

    print(f"3-year cutoff (UTC): {cutoff.isoformat()}")
    print(f"Rows fetched (raw): {total_fetched}")
    print(f"Pages fetched: {total_pages}")
    print(f"Rows saved: {len(df)}")
    print(f"Attribute columns: {len(df.columns)}")
    print(f"Wrote: {args.output}")
    print(f"Wrote: {args.attributes_output}")


if __name__ == "__main__":
    main()
