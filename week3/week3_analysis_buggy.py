import csv
from collections import defaultdict
from pathlib import Path

# Function to load survey rows from a CSV file
def load_survey_rows(filename: str) -> list[dict[str, str]]:
    """Load a survey CSV from disk and return all rows as dictionaries.

    Each dictionary maps column names to string values. The file is read
    with UTF-8 encoding. Expects a header row compatible with csv.DictReader.
    """
    path = Path(__file__).resolve().parent / filename
    rows: list[dict[str, str]] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

# Function to check if experience_years is numeric
def experience_is_numeric(row: dict[str, str]) -> bool: 
    """Return True if ``experience_years`` can be parsed as a base-10 integer.

    Leading and trailing whitespace are ignored. Returns False for empty
    strings, words like ``fifteen``, or any other value that int() rejects.
    """
    try:
        int(row["experience_years"].strip())
        return True
    except ValueError:
        return False

# Function to count responses by role
def count_responses_by_role(rows: list[dict[str, str]]) -> dict[str, int]:
    """Count how many rows fall under each normalized role label.

    Role strings are stripped and passed through :meth:`str.title` so
    variants such as ``ux researcher`` and ``UX Researcher`` share one key.
    """
    role_counts: dict[str, int] = {}
    for row in rows:
        role = row["role"].strip().title()
        if role in role_counts:
            role_counts[role] += 1
        else:
            role_counts[role] = 1
    return role_counts

# Function to rank tools by reviews
def rank_tools_by_reviews(
    rows: list[dict[str, str]],
) -> list[tuple[str, float, int]]:
    """Rank survey tools by average satisfaction score across all reviews.

    Each CSV row is treated as one review of the tool named in
    ``primary_tool``, with ``satisfaction_score`` as that review's numeric
    rating (typically 1–5). Tools that differ only by letter case are grouped
    together; the display name is the first spelling encountered for that
    tool. Rows with a missing tool name, a missing score, or a score that
    cannot be parsed as an integer are omitted.

    Args:
        rows: Survey rows (e.g. from :func:`load_survey_rows`), each mapping
            column names to string values.

    Returns:
        A list of ``(tool_label, mean_score, review_count)``, sorted by
        highest mean score first, then by most reviews, then alphabetically
        by tool label (case-insensitive).
    """
    # Initialize dictionaries to store scores and tool labels
    scores_by_key: dict[str, list[int]] = defaultdict(list)
    label_for_key: dict[str, str] = {}

# Process each row to calculate scores and tool labels
    for row in rows:
        tool = (row.get("primary_tool") or "").strip()
        if not tool:
            continue
        score_raw = (row.get("satisfaction_score") or "").strip()
        if not score_raw:
            continue
        try:
            score = int(score_raw)
        except ValueError:
            continue
        key = tool.casefold()
        if key not in label_for_key:
            label_for_key[key] = tool
        scores_by_key[key].append(score)

# Calculate the mean score for each tool and store the results
    ranked: list[tuple[str, float, int]] = []
    for key, scores in scores_by_key.items():
        mean_score = sum(scores) / len(scores)
        ranked.append((label_for_key[key], mean_score, len(scores)))

    ranked.sort(key=lambda x: (-x[1], -x[2], x[0].casefold()))
    return ranked

# Main function to run the analysis
def main() -> None:
    filename = "week3_survey_messy.csv"
    rows = load_survey_rows(filename)

# Count responses by role
    role_counts = count_responses_by_role(rows)
    print("Responses by role:")
    for role, count in sorted(role_counts.items()):
        print(f"  {role}: {count}")

# Calculate the average years of experience (only rows with numeric experience_years)
    total_experience = 0
    n_with_numeric_experience = 0
    for row in rows:
        if not experience_is_numeric(row):
            continue
        total_experience += int(row["experience_years"].strip())
        n_with_numeric_experience += 1

# Calculate the average years of experience (only rows with numeric experience_years)
    avg_experience = (
        total_experience / n_with_numeric_experience
        if n_with_numeric_experience
        else 0.0
    )
    print(f"\nAverage years of experience: {avg_experience:.1f}")

# Calculate the top 5 satisfaction scores
    scored_rows: list[tuple[str, int]] = []
    for row in rows:
        if row["satisfaction_score"].strip():
            scored_rows.append(
                (row["participant_name"], int(row["satisfaction_score"]))
            )
# Calculate the top 5 satisfaction scores

    scored_rows.sort(key=lambda x: x[1])
    top5 = scored_rows[:5]

    print("\nTop 5 satisfaction scores:")
    for name, score in top5:
        print(f"  {name}: {score}")

# Rank tools by reviews
    tool_rankings = rank_tools_by_reviews(rows)
    print("\nTools ranked by average satisfaction (reviews):")
    for tool, mean_score, n in tool_rankings:
        print(f"  {tool}: {mean_score:.2f} avg over {n} review(s)")


if __name__ == "__main__":
    main()
