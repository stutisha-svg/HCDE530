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
    for row in quotes:
        text = row["Quote"]
        n = count_words(text)
        word_counts.append(n)
        # One line per quote so you can scan counts alongside who said it.
        print(f"{n:3} words  |  {row['Character']}, {row['Novel']}")

    if not word_counts:
        print("No quotes found in CSV.")
        return

    total = len(word_counts)
    print()
    print("-- Summary " + "-" * 32)
    print(f"  Quotes          : {total}")
    print(f"  Shortest quote  : {min(word_counts)} words")
    print(f"  Longest quote   : {max(word_counts)} words")
    print(f"  Average length  : {sum(word_counts) / total:.1f} words")


if __name__ == "__main__":
    main()
