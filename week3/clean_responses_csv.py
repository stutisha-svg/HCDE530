"""
Read a responses CSV, drop rows with an empty text field, uppercase the role
column, and write clean_responses.csv in this folder (week3).

Looks for input as repsonses.csv (common filename typo) or responses.csv in
the same directory as this script.

The assignment text often refers to an empty 'rows' field; this script uses
a column named 'rows' if present, otherwise 'response'.
"""

import csv
from pathlib import Path

WEEK3_DIR = Path(__file__).resolve().parent
OUTPUT_CSV = WEEK3_DIR / "clean_responses.csv"


def _resolve_input_csv() -> Path:
    for name in ("repsonses.csv", "responses.csv"):
        path = WEEK3_DIR / name
        if path.is_file():
            return path
    raise SystemExit(
        f"No input file found. Place 'repsonses.csv' or 'responses.csv' in {WEEK3_DIR}"
    )


def _empty_check_column(fieldnames: list[str]) -> str:
    if "rows" in fieldnames:
        return "rows"
    if "response" in fieldnames:
        return "response"
    raise SystemExit(
        "CSV must include a 'rows' or 'response' column for the empty-row check."
    )


def main() -> None:
    input_csv = _resolve_input_csv()
    with input_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise SystemExit("Missing header row in CSV.")
        fieldnames = list(reader.fieldnames)
        if "role" not in fieldnames:
            raise SystemExit("CSV must include a 'role' column.")

        check_col = _empty_check_column(fieldnames)
        cleaned: list[dict[str, str]] = []

        for row in reader:
            text = (row.get(check_col) or "").strip()
            if not text:
                continue
            out = dict(row)
            out["role"] = (out.get("role") or "").strip().upper()
            cleaned.append(out)

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned)

    print(f"Read {input_csv.name}, wrote {len(cleaned)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
