import csv

# Load the survey data from a CSV file
filename = "week3_survey_messy.csv"
rows = []

with open(filename, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)


def experience_is_numeric(row: dict) -> bool:
    try:
        int(row["experience_years"].strip())
        return True
    except ValueError:
        return False


# Count responses by role
# Normalize role names so "ux researcher" and "UX Researcher" are counted together
role_counts = {}

for row in rows:
    role = row["role"].strip().title()
    if role in role_counts:
        role_counts[role] += 1
    else:
        role_counts[role] = 1

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

avg_experience = (
    total_experience / n_with_numeric_experience if n_with_numeric_experience else 0.0
)
print(f"\nAverage years of experience: {avg_experience:.1f}")

# Find the top 5 highest satisfaction scores
scored_rows = []
for row in rows:
    if row["satisfaction_score"].strip():
        scored_rows.append((row["participant_name"], int(row["satisfaction_score"])))

scored_rows.sort(key=lambda x: x[1])
top5 = scored_rows[:5]

print("\nTop 5 satisfaction scores:")
for name, score in top5:
    print(f"  {name}: {score}")
