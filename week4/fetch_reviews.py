"""Fetch app reviews from the HCDE 530 Week 4 API and export category + helpful votes."""

import csv
import json
import urllib.parse
import urllib.request

API_URL = "https://hcde530-week4-api.onrender.com/reviews"  # docs: GET /reviews on the class API host
OUTPUT_CSV = "reviews_category_helpful.csv"


def fetch_all_reviews():
    rows = []
    offset = 0
    limit = 50
    while True:
        query = urllib.parse.urlencode({"offset": offset, "limit": limit})
        url = f"{API_URL}?{query}"
        req = urllib.request.Request(url, headers={"User-Agent": "HCDE530-week4-script"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.load(resp)
        reviews = payload.get("reviews", [])
        for review in reviews:
            rows.append(
                {
                    "category": review.get("category", ""),
                    "helpful_votes": review.get("helpful_votes", 0),
                }
            )
        total = payload.get("total", 0)
        returned = payload.get("returned", len(reviews))
        if offset + returned >= total or returned == 0:  # pagination: stop when all records are fetched
            break
        offset += returned
    return rows


def main():
    rows = fetch_all_reviews()
    for row in rows:
        print(f"{row['category']}: {row['helpful_votes']} helpful votes")
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["category", "helpful_votes"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote {len(rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
