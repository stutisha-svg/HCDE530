"""Read Dickens quotes from CSV, print a summary table, and write per-row results to CSV."""

import csv

INPUT_CSV = "dickens_quotes.csv"
OUTPUT_CSV = "dickens_word_counts.csv"


def count_words(text: str) -> int:
    # Same rule as demo_word_count.py: words = chunks separated by whitespace.
    return len(text.split())


def main() -> None:
    # read the quotes from the csv file
    quotes: list[dict[str, str]] = [] # list of dictionaries
    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            quotes.append(row)

    word_counts: list[int] = []
    # Each dict becomes one row in the output CSV (and one printed line).
    result_rows: list[dict[str, str | int]] = []
# print the header row
    print(f"{'Character':<28} {'Words':<6} {'Quote (first 60 chars)'}")
    print("-" * 95)
# loop through the quotes and count the number of words in each quote
    for row in quotes:
        text = row["Quote"]
        n = count_words(text)
        word_counts.append(n)
# if the quote is longer than 60 characters, add an ellipsis to the end
        if len(text) > 60:
            preview = text[:60] + "..."
        else:
            preview = text
# add the per-row results to the list
        # add the per-row results to the list
        result_rows.append(
            {
                "Character": row["Character"],
                "Novel": row["Novel"],
                "Word_count": n,
                "Quote_preview": preview,
            }
        )
        print(f"{row['Character']:<28} {n:<6} {preview}")
# write the per-row results to a new file for spreadsheets / grading.
    if not word_counts:
        print("No quotes found in CSV.")
        return

    # Write the same per-row results to a new file for spreadsheets / grading.
    fieldnames = ["Character", "Novel", "Word_count", "Quote_preview"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        for r in result_rows:
            writer.writerow(r)

    total = len(word_counts)
    print()
    print(f"Wrote {OUTPUT_CSV} ({total} rows).")
    print()
    print("-- Summary " + "-" * 32)
    print(f"  Total responses : {total}")
    print(f"  Shortest        : {min(word_counts)} words")
    print(f"  Longest         : {max(word_counts)} words")
    print(f"  Average         : {sum(word_counts) / total:.1f} words")


if __name__ == "__main__":
    main()
