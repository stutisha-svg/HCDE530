"""Read Dickens quotes from CSV and report word counts per quote plus summary stats."""

import csv

FILENAME = "dickens_quotes.csv"


def count_words(text: str) -> int:
    # Same rule as demo_word_count.py: words = chunks separated by whitespace.
    return len(text.split())


def main() -> None:
    quotes: list[dict[str, str]] = []
    with open(FILENAME, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            quotes.append(row)

    word_counts: list[int] = []
    # Header row for the per-quote table (character, count, first 60 chars of quote).
    print(f"{'Character':<28} {'Words':<6} {'Quote (first 60 chars)'}")
    print("-" * 95)

    for row in quotes:
        text = row["Quote"]
        n = count_words(text)
        word_counts.append(n)

        if len(text) > 60:
            preview = text[:60] + "..."
        else:
            preview = text

        print(f"{row['Character']:<28} {n:<6} {preview}")

    if not word_counts:
        print("No quotes found in CSV.")
        return

    total = len(word_counts)
    print()
    print("-- Summary " + "-" * 32)
    print(f"  Total responses : {total}")
    print(f"  Shortest        : {min(word_counts)} words")
    print(f"  Longest         : {max(word_counts)} words")
    print(f"  Average         : {sum(word_counts) / total:.1f} words")


if __name__ == "__main__":
    main()
