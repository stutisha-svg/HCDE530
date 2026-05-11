"""Slim ``bsky_posts_collected.csv`` in place.

Keep set:
  1. Columns the four analyses + the two enrichment scripts actually use.
  2. Columns whose non-null fraction is >= 10% in the current file
     (kept as future-work reserve even if no chart references them yet).

Drop everything else (JSON-flattened embed leaves that are >90% NaN).

The write is atomic: rows go to ``<csv>.tmp`` and then ``os.replace`` swaps it
over the original file. The script is idempotent -- running it again on the
already-slimmed CSV is a no-op (or near-no-op).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd

CSV = Path("bsky_posts_collected.csv")
POPULATION_THRESHOLD_PCT = 10.0

ANALYSIS_COLS = [
    "uri", "cid", "indexedAt",
    "reply.parent.uri", "reply.root.uri", "embed.record.uri",
    "record.text", "record.createdAt",
    "likeCount", "repostCount", "replyCount", "quoteCount",
    "author.handle", "author.did", "author.displayName",
    "collect_primary_theme", "collect_all_themes",
]


def main() -> int:
    if not CSV.exists():
        print(f"!! {CSV} not found in {Path.cwd()}", file=sys.stderr)
        return 1

    size_before = CSV.stat().st_size
    print(f"Loading {CSV} ({size_before / 1024 / 1024:,.1f} MB)...")
    df = pd.read_csv(CSV, low_memory=False)
    print(f"  rows: {len(df):,}  cols: {len(df.columns)}")

    non_null_pct = (df.notna().mean() * 100).sort_values(ascending=False)

    analysis_keep = [c for c in ANALYSIS_COLS if c in df.columns]
    missing_analysis = [c for c in ANALYSIS_COLS if c not in df.columns]
    if missing_analysis:
        print(f"\n  (analysis cols not found in CSV, skipping): {missing_analysis}")

    populated_keep = [c for c, p in non_null_pct.items() if p >= POPULATION_THRESHOLD_PCT]

    keep_set = set(analysis_keep) | set(populated_keep)
    keep = [c for c in df.columns if c in keep_set]
    drop = [c for c in df.columns if c not in keep_set]

    print(f"\nKeeping {len(keep)} columns "
          f"(analysis-used: {len(analysis_keep)}, "
          f">= {POPULATION_THRESHOLD_PCT:.0f}% populated: {len(populated_keep)}, "
          f"union: {len(keep)}).")
    for c in keep:
        tag = " (analysis)" if c in ANALYSIS_COLS else ""
        print(f"  keep  {non_null_pct[c]:5.1f}%  {c}{tag}")

    print(f"\nDropping {len(drop)} columns (< {POPULATION_THRESHOLD_PCT:.0f}% populated "
          f"and not referenced in the analyses).")
    for c in drop[:15]:
        print(f"  drop  {non_null_pct[c]:5.2f}%  {c}")
    if len(drop) > 15:
        print(f"  ... and {len(drop) - 15} more")

    if not drop:
        print("\nNothing to drop. CSV already slim.")
        return 0

    slim = df[keep]

    tmp_path = CSV.with_suffix(CSV.suffix + ".tmp")
    print(f"\nWriting slim CSV to {tmp_path} ...")
    slim.to_csv(tmp_path, index=False)
    os.replace(tmp_path, CSV)

    size_after = CSV.stat().st_size
    print(f"Wrote {CSV} ({size_after / 1024 / 1024:,.1f} MB, "
          f"{size_after / size_before * 100:.1f}% of original).")
    print(f"Final shape: {len(slim):,} rows x {len(slim.columns)} cols.")

    head = pd.read_csv(CSV, low_memory=False, nrows=3)
    assert len(head.columns) == len(slim.columns), "verify: column count mismatch"
    print(f"Verified: re-read header has {len(head.columns)} columns.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
