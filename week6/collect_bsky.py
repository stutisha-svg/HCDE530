"""
collect_bsky.py
---------------
Collects Bluesky posts via searchPosts across **risk-framed** and **general** AI
queries so analysis is less one-sided than doom-only retrieval.

Why your old runs showed ~99 raw then 0 kept:
- The previous viral thresholds (60 replies, 500 likes, 150 reposts) exclude
  almost all posts returned by search.

Defaults now:
- No engagement minimums (all configurable).
- Full flattened post objects → CSV (all fields the API returns per post).
- Optional --viral to restore strict thresholds.

Requirements:
    pip install requests pandas

Usage:
    python collect_bsky.py
    python collect_bsky.py --max-posts 200
    python collect_bsky.py --viral

Outputs:
    bsky_posts_collected.csv       — one row per unique post (URI); API fields flattened
    bsky_posts_collect_lineage.csv — one row per search hit (audit trail)
    bsky_ai_misinformation_theme_summary.csv — small optional aggregate by theme

Environment:
    BSKY_ACCESS_JWT — optional Bearer token if endpoints throttle you.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pandas as pd
import requests

# theme_name -> (topic_group, [queries])
THEMES: dict[str, tuple[str, list[str]]] = {
    "job_displacement": (
        "risk",
        [
            "AI replace jobs",
            "AI taking jobs",
            "automation unemployment",
            "robots stealing jobs",
            "AI will replace workers",
        ],
    ),
    "deepfakes": (
        "risk",
        [
            "deepfake AI",
            "AI fake video",
            "AI generated face",
            "synthetic media",
            "AI impersonation",
        ],
    ),
    "sentience_hype": (
        "risk",
        [
            "AI is sentient",
            "AI has feelings",
            "ChatGPT is conscious",
            "AI is alive",
            "artificial intelligence emotions",
        ],
    ),
    "agi_risk": (
        "risk",
        [
            "AGI existential risk",
            "superintelligence danger",
            "AI destroy humanity",
            "AI existential risk",
            "artificial general intelligence threat",
        ],
    ),
    "regulation_debate": (
        "risk",
        [
            "AI regulation debate",
            "AI government policy",
            "AI surveillance",
            "AI censorship debate",
            "stop AI",
        ],
    ),
    "health_ai": (
        "risk",
        [
            "AI medical diagnosis",
            "ChatGPT medical advice",
            "AI doctor",
            "AI health",
            "AI cancer research",
        ],
    ),
    "ai_work_productivity": (
        "general",
        [
            "ChatGPT tips",
            "AI productivity",
            "using AI at work",
            "prompt engineering tips",
            "copilot workflow",
        ],
    ),
    "ai_creative": (
        "general",
        [
            "AI art",
            "generative art",
            "Stable Diffusion",
            "AI music production",
            "AI writing tools",
        ],
    ),
    "ai_research_tech": (
        "general",
        [
            "open source LLM",
            "new AI model release",
            "machine learning paper",
            "Hugging Face model",
            "LLM benchmark",
        ],
    ),
    "ai_education": (
        "general",
        [
            "AI for students",
            "learning machine learning",
            "AI course online",
            "teaching with AI",
            "AI literacy",
        ],
    ),
    "ai_business": (
        "general",
        [
            "AI startup",
            "enterprise AI",
            "AI tools business",
            "AI customer support",
            "AI automation business",
        ],
    ),
    "policy_balanced": (
        "policy_neutral",
        [
            "AI policy news",
            "EU AI Act",
            "AI safety research",
            "responsible AI",
            "AI governance",
        ],
    ),
}

FALSE_CLAIM_PHRASES = [
    "ai is sentient",
    "ai has feelings",
    "ai is conscious",
    "ai is alive",
    "chatgpt feels",
    "chatgpt is aware",
    "ai can feel pain",
    "ai has emotions",
    "ai is self-aware",
    "ai will replace 90%",
    "ai will replace all jobs",
    "ai will take every job",
    "no jobs left because of ai",
    "ai will end employment",
    "automation will replace all workers",
    "ai cured cancer",
    "ai is better than any doctor",
    "chatgpt diagnosed my",
    "ai replaced my doctor",
    "doctors are useless now ai",
    "ai is smarter than all humans",
    "ai has achieved agi",
    "ai is now superintelligent",
    "chatgpt is god",
    "ai knows everything",
    "this video is real and ai made it",
    "ai proved this happened",
    "ai confirmed this is true",
]

EMOTION_WORDS = [
    "terrifying",
    "terrified",
    "horrifying",
    "horrified",
    "nightmare",
    "apocalypse",
    "apocalyptic",
    "doomed",
    "extinction",
    "end of humanity",
    "end of the world",
    "we're all going to die",
    "outrageous",
    "unacceptable",
    "disgusting",
    "shocking",
    "this is insane",
    "can't believe",
    "unbelievable",
    "wake up",
    "they don't want you to know",
    "urgent",
    "emergency",
    "crisis",
    "catastrophe",
    "catastrophic",
    "must stop ai",
    "ban ai now",
    "ai is out of control",
    "they're hiding",
    "cover up",
    "suppressed",
    "censored by ai",
]

TIME_WINDOWS = [
    ("2023-01-01T00:00:00Z", "2023-06-30T23:59:59Z"),
    ("2023-07-01T00:00:00Z", "2023-12-31T23:59:59Z"),
    ("2024-01-01T00:00:00Z", "2024-06-30T23:59:59Z"),
    ("2024-07-01T00:00:00Z", "2024-12-31T23:59:59Z"),
    ("2025-01-01T00:00:00Z", "2025-06-30T23:59:59Z"),
    ("2025-07-01T00:00:00Z", "2025-12-31T23:59:59Z"),
    ("2026-01-01T00:00:00Z", "2026-06-30T23:59:59Z"),
]

VIRAL_MIN_REPLIES = 60
VIRAL_MIN_LIKES = 500
VIRAL_MIN_REPOSTS = 150

API_PATH = "/xrpc/app.bsky.feed.searchPosts"
API_BASE_URLS = [
    "https://public.api.bsky.app",
    "https://api.bsky.app",
]


@dataclass
class FilterConfig:
    min_likes: int = 0
    min_replies: int = 0
    min_reposts: int = 0
    exclude_reposts: bool = True
    exclude_replies: bool = False
    lang_en_only: bool = True
    exclude_new_accounts_days: int = 0


def _session_headers() -> dict:
    h = {"Accept": "application/json", "User-Agent": "collect-bsky/3.0"}
    token = os.getenv("BSKY_ACCESS_JWT", "").strip()
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def query_overlap_score(text: str, query: str) -> int:
    if not text or not query:
        return 0
    tl = text.lower()
    ql = query.lower()
    score = 0
    if ql in tl:
        score += 12
    for tok in re.findall(r"[a-z0-9]+", ql):
        if len(tok) < 2:
            continue
        if re.search(rf"\b{re.escape(tok)}\b", tl):
            score += 3
        elif tok in tl:
            score += 1
    return score


def wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n <= 0:
        return (0.0, 0.0)
    p = successes / n
    denom = 1 + z**2 / n
    center = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


def score_post(text: str, primary_query: str) -> dict[str, Any]:
    lowered = text.lower()
    qlower = primary_query.lower()
    matched = [p for p in FALSE_CLAIM_PHRASES if p in lowered]
    false_claim_phrase = bool(matched)
    false_claim_beyond_query = (
        any(p not in qlower for p in matched) if matched else False
    )
    emotional_score = sum(1 for word in EMOTION_WORDS if word in lowered)
    high_emotion = emotional_score >= 2
    heuristic_alarmist_or_false_claim = false_claim_phrase or high_emotion
    heuristic_alarmist_or_content_claim = false_claim_beyond_query or high_emotion
    return {
        "false_claim_phrase": false_claim_phrase,
        "false_claim_beyond_query": false_claim_beyond_query,
        "emotional_score": emotional_score,
        "high_emotion": high_emotion,
        "heuristic_alarmist_or_false_claim": heuristic_alarmist_or_false_claim,
        "heuristic_alarmist_or_content_claim": heuristic_alarmist_or_content_claim,
        "false_claim": false_claim_phrase,
        "misinfo_adjacent": heuristic_alarmist_or_false_claim,
    }


def fetch_posts(
    session: requests.Session,
    query: str,
    since: str,
    until: str,
    max_posts: int,
    lang: str,
) -> list[dict]:
    posts: list[dict] = []
    cursor = None

    while len(posts) < max_posts:
        params: dict[str, Any] = {
            "q": query,
            "limit": 100,
            "sort": "latest",
            "since": since,
            "until": until,
        }
        if lang:
            params["lang"] = lang
        if cursor:
            params["cursor"] = cursor

        data = None
        last_status = None
        for base in API_BASE_URLS:
            url = base + API_PATH
            try:
                resp = session.get(url, params=params, timeout=20)
                last_status = resp.status_code
                if resp.status_code == 429:
                    print("    Rate limited — waiting 30s...")
                    time.sleep(30)
                    resp = session.get(url, params=params, timeout=20)
                    last_status = resp.status_code
                if resp.status_code == 200:
                    data = resp.json()
                    break
                if resp.status_code in (403, 502, 503):
                    print(f"    {base} returned {resp.status_code}, trying next host...")
                    continue
                print(f"    API error {resp.status_code}: {resp.text[:200]}")
                break
            except requests.exceptions.RequestException as e:
                print(f"    Network error ({base}): {e}")
                continue

        if data is None:
            if last_status:
                print(f"    All hosts failed (last status {last_status})")
            break

        batch = data.get("posts", [])
        if not batch:
            break
        posts.extend(batch)
        cursor = data.get("cursor")
        if not cursor:
            break
        time.sleep(0.45)

    return posts


def passes_filters(post: dict, cfg: FilterConfig) -> bool:
    record = post.get("record") or {}
    if cfg.exclude_reposts and record.get("$type") == "app.bsky.feed.repost":
        return False
    if cfg.exclude_replies and record.get("reply"):
        return False

    text = (record.get("text") or "").strip()
    if not text:
        return False

    langs = record.get("langs") or []
    if cfg.lang_en_only and langs and "en" not in langs:
        return False

    likes = int(post.get("likeCount") or 0)
    reposts = int(post.get("repostCount") or 0)
    replies = int(post.get("replyCount") or 0)
    if likes < cfg.min_likes:
        return False
    if replies < cfg.min_replies:
        return False
    if reposts < cfg.min_reposts:
        return False

    if cfg.exclude_new_accounts_days > 0:
        author = post.get("author") or {}
        ac = author.get("createdAt")
        pc = record.get("createdAt")
        if ac and pc:
            try:
                ad = datetime.fromisoformat(ac.replace("Z", "+00:00"))
                pd_dt = datetime.fromisoformat(pc.replace("Z", "+00:00"))
                if (pd_dt - ad).days < cfg.exclude_new_accounts_days:
                    return False
            except (ValueError, TypeError):
                pass

    return True


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Collect Bluesky posts to CSV (full API shape).")
    p.add_argument("--max-posts", type=int, default=300, help="Max posts per query per window.")
    p.add_argument(
        "--viral",
        action="store_true",
        help="Strict viral filters (old script): high replies/likes/reposts.",
    )
    p.add_argument("--min-likes", type=int, default=None)
    p.add_argument("--min-replies", type=int, default=None)
    p.add_argument("--min-reposts", type=int, default=None)
    p.add_argument("--exclude-replies", action="store_true")
    p.add_argument("--include-non-english", action="store_true")
    p.add_argument("--no-exclude-reposts", action="store_true")
    p.add_argument("--exclude-new-days", type=int, default=0)
    p.add_argument("--out", default="bsky_posts_collected.csv")
    p.add_argument("--lineage-out", default="bsky_posts_collect_lineage.csv")
    p.add_argument("--summary-out", default="bsky_ai_misinformation_theme_summary.csv")
    p.add_argument("--skip-summary", action="store_true")
    return p.parse_args()


def build_filter_config(args: argparse.Namespace) -> FilterConfig:
    if args.viral:
        return FilterConfig(
            min_likes=VIRAL_MIN_LIKES,
            min_replies=VIRAL_MIN_REPLIES,
            min_reposts=VIRAL_MIN_REPOSTS,
            exclude_reposts=not args.no_exclude_reposts,
            exclude_replies=args.exclude_replies,
            lang_en_only=not args.include_non_english,
            exclude_new_accounts_days=args.exclude_new_days,
        )
    return FilterConfig(
        min_likes=args.min_likes if args.min_likes is not None else 0,
        min_replies=args.min_replies if args.min_replies is not None else 0,
        min_reposts=args.min_reposts if args.min_reposts is not None else 0,
        exclude_reposts=not args.no_exclude_reposts,
        exclude_replies=args.exclude_replies,
        lang_en_only=not args.include_non_english,
        exclude_new_accounts_days=args.exclude_new_days,
    )


def theme_summary_from_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "collect_primary_theme" not in df.columns:
        return pd.DataFrame()
    col = "heuristic_alarmist_or_false_claim"
    if col not in df.columns:
        return pd.DataFrame()
    rows = []
    for theme, g in df.groupby("collect_primary_theme", sort=True):
        n = len(g)
        alarm = int(g[col].sum())
        lo, hi = wilson_ci(alarm, n)
        rows.append(
            {
                "theme": theme,
                "n_posts": n,
                "rate_heuristic_alarmist_or_false_claim": alarm / n if n else 0.0,
                "ci95_low": lo,
                "ci95_high": hi,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    args = parse_args()
    cfg = build_filter_config(args)
    session = requests.Session()
    session.headers.update(_session_headers())

    hits: list[tuple[dict, dict[str, Any]]] = []
    total_raw = 0

    for theme, (topic_group, queries) in THEMES.items():
        for query in queries:
            for since, until in TIME_WINDOWS:
                print(f"\n[{topic_group}] {theme} | {query!r} | {since[:10]} → {until[:10]}")
                posts = fetch_posts(
                    session,
                    query,
                    since,
                    until,
                    max_posts=args.max_posts,
                    lang="en" if cfg.lang_en_only else "",
                )
                total_raw += len(posts)
                kept = 0
                for post in posts:
                    if not passes_filters(post, cfg):
                        continue
                    meta = {
                        "collect_theme": theme,
                        "collect_topic_group": topic_group,
                        "collect_query": query,
                        "collect_since": since,
                        "collect_until": until,
                    }
                    hits.append((post, meta))
                    kept += 1
                print(f"  raw={len(posts)} kept_after_filters={kept}")
                time.sleep(0.85)

    print(f"\n{'='*60}\nTotal raw API posts seen: {total_raw}\nTotal kept hits: {len(hits)}")

    if not hits:
        print("No rows to save. If you used --viral, run again without it.")
        return

    lineage_rows = []
    for post, meta in hits:
        lineage_rows.append(
            {
                "uri": post.get("uri"),
                "cid": post.get("cid"),
                **meta,
            }
        )
    pd.DataFrame(lineage_rows).to_csv(
        args.lineage_out, index=False, encoding="utf-8-sig"
    )
    print(f"Saved lineage: {args.lineage_out} ({len(lineage_rows)} rows)")

    by_uri: dict[str, list[tuple[dict, dict]]] = {}
    for post, meta in hits:
        u = post.get("uri") or ""
        if not u:
            continue
        by_uri.setdefault(u, []).append((post, meta))

    wide_rows: list[dict[str, Any]] = []
    for _uri, group in by_uri.items():
        post0 = group[0][0]
        record = post0.get("record") or {}
        text = (record.get("text") or "")

        best_meta = None
        best_key = None
        themes_set: set[str] = set()
        groups_set: set[str] = set()
        queries_list: list[str] = []

        for _post, meta in group:
            themes_set.add(meta["collect_theme"])
            groups_set.add(meta["collect_topic_group"])
            queries_list.append(meta["collect_query"])
            s = query_overlap_score(text, meta["collect_query"])
            key = (-s, meta["collect_theme"], meta["collect_query"])
            if best_key is None or key < best_key:
                best_key = key
                best_meta = meta

        assert best_meta is not None
        primary_query = best_meta["collect_query"]
        scores = score_post(text, primary_query)

        flat = pd.json_normalize(post0, sep=".").to_dict(orient="records")[0]
        flat["collect_primary_theme"] = best_meta["collect_theme"]
        flat["collect_primary_topic_group"] = best_meta["collect_topic_group"]
        flat["collect_primary_query"] = primary_query
        flat["collect_all_themes"] = ";".join(sorted(themes_set))
        flat["collect_all_topic_groups"] = ";".join(sorted(groups_set))
        flat["collect_n_search_hits"] = len(group)
        flat["collect_all_queries"] = json.dumps(queries_list, ensure_ascii=False)
        for k, v in scores.items():
            flat[k] = v
        wide_rows.append(flat)

    df_wide = pd.DataFrame(wide_rows)
    df_wide.to_csv(args.out, index=False, encoding="utf-8-sig")
    print(
        f"Saved posts (wide): {args.out} ({len(df_wide)} unique URIs, {len(df_wide.columns)} columns)"
    )

    if not args.skip_summary:
        summ = theme_summary_from_df(df_wide)
        summ.to_csv(args.summary_out, index=False, encoding="utf-8-sig")
        print(f"Saved summary: {args.summary_out}")

    print("\nDone. Analyze with the wide CSV; lineage explains multi-query matches.")


if __name__ == "__main__":
    main()
