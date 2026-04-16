"""Count how many times each role appears in responses.csv (case-insensitive groups)."""

import csv
from collections import Counter
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent / "responses.csv"


def main() -> None:
    counts: Counter[str] = Counter()
    label_for_key: dict[str, str] = {}

    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "role" not in reader.fieldnames:
            raise SystemExit("CSV must have a header row with a 'role' column.")

        for row in reader:
            role = (row.get("role") or "").strip()
            if not role:
                continue
            key = role.casefold()
            if key not in label_for_key:
                label_for_key[key] = role
            counts[key] += 1

    for key, n in counts.most_common():
        print(f"{label_for_key[key]}: {n}")


if __name__ == "__main__":
    main()
