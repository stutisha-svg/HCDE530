"""
Fetch reviews from the HCDE 530 Week 4 API, filter and summarize, write one CSV.

Filter: verified purchase AND rating >= 4 (change the logic in filter_reviews() if you like).
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_REVIEWS = "https://hcde530-week4-api.onrender.com/reviews"
OUTPUT_CSV = "week4_analysis.csv"


def fetch_all_reviews() -> list[dict]:
    out: list[dict] = []
    offset = 0
    limit = 50
    while True:
        url = f"{API_REVIEWS}?{urlencode({'offset': offset, 'limit': limit})}"
        req = Request(url, headers={"User-Agent": "HCDE530-week4-analyze"})
        with urlopen(req, timeout=60) as resp:
            payload = json.load(resp)
        reviews = payload.get("reviews", [])
        out.extend(reviews)
        total = int(payload.get("total", 0))
        returned = int(payload.get("returned", len(reviews)))
        if offset + returned >= total or returned == 0:
            break
        offset += returned
    return out


def filter_reviews(reviews: list[dict]) -> list[dict]:
    def keep(r: dict) -> bool:
        return bool(r.get("verified_purchase")) and int(r.get("rating") or 0) >= 4

    return [r for r in reviews if keep(r)]


def main() -> None:
    reviews = fetch_all_reviews()
    filtered = filter_reviews(reviews)
    counts = Counter(str(r.get("category") or "") for r in filtered)
    hi = max(filtered, key=lambda r: int(r.get("helpful_votes") or 0)) if filtered else None
    lo = min(filtered, key=lambda r: int(r.get("helpful_votes") or 0)) if filtered else None

    rows: list[dict[str, str | int]] = [
        {
            "metric": "total_reviews_fetched",
            "value": len(reviews),
            "category": "",
            "review_id": "",
            "app": "",
        },
        {
            "metric": "reviews_after_filter",
            "value": len(filtered),
            "category": "",
            "review_id": "",
            "app": "verified_purchase and rating>=4",
        },
    ]

    if hi is not None and lo is not None:
        rows.append(
            {
                "metric": "max_helpful_votes",
                "value": int(hi.get("helpful_votes") or 0),
                "category": str(hi.get("category") or ""),
                "review_id": str(hi.get("id") or ""),
                "app": str(hi.get("app") or ""),
            }
        )
        rows.append(
            {
                "metric": "min_helpful_votes",
                "value": int(lo.get("helpful_votes") or 0),
                "category": str(lo.get("category") or ""),
                "review_id": str(lo.get("id") or ""),
                "app": str(lo.get("app") or ""),
            }
        )

    for category in sorted(counts.keys()):
        rows.append(
            {
                "metric": "category_count",
                "value": counts[category],
                "category": category,
                "review_id": "",
                "app": "",
            }
        )

    fieldnames = ["metric", "value", "category", "review_id", "app"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"Fetched {len(reviews)} reviews.")
    print(f"After filter (verified + rating>=4): {len(filtered)} reviews.")
    if hi is not None and lo is not None:
        print(
            f"Highest helpful_votes in filtered set: {hi.get('helpful_votes')} "
            f"(id={hi.get('id')}, app={hi.get('app')})"
        )
        print(
            f"Lowest helpful_votes in filtered set: {lo.get('helpful_votes')} "
            f"(id={lo.get('id')}, app={lo.get('app')})"
        )
    print("Category counts (filtered):")
    for c, n in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {c}: {n}")
    print(f"\nWrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
