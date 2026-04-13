import csv
import html

# A script to count words in each response from demo_responses.csv, print a terminal
# summary, and write a static Dashboard.html you can open in a browser (no server).

# --- Load the CSV into a list of row dictionaries ---------------------------------
# Each row becomes a dict keyed by column name (participant_id, role, response).
filename = "demo_responses.csv"
responses = []

with open(filename, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Append every row so we can loop again later (lists + loops practice).
        responses.append(row)


def count_words(response):
    """Count the number of words in a response string.

    Takes a string, splits it on whitespace, and returns the word count.
    Used to measure response length across all participants.
    """
    return len(response.split())


def write_dashboard_html(rows, word_counts, path="Dashboard.html"):
    """Build a self-contained static HTML dashboard and write it to disk.

    `rows` is a list of dicts with keys: participant, role, count, preview, response_full.
    We escape all user-provided text so characters like < or & do not break the page.
    """
    # Summary numbers shared with the terminal block below.
    total = len(word_counts)
    shortest = min(word_counts)
    longest = max(word_counts)
    average = sum(word_counts) / total

    # Build one <tr>...</tr> per participant (string concatenation in a loop).
    table_rows_html = []
    for r in rows:
        safe_id = html.escape(r["participant"])
        safe_role = html.escape(r["role"])
        safe_preview = html.escape(r["preview"])
        safe_full = html.escape(r["response_full"])
        count = r["count"]
        # <details> gives a no-JavaScript expand/collapse for long quotes.
        response_cell = (
            f'<details class="response-details">'
            f"<summary>{safe_preview}</summary>"
            f'<p class="response-full">{safe_full}</p>'
            f"</details>"
        )
        table_rows_html.append(
            "<tr>"
            f'<td class="mono">{safe_id}</td>'
            f"<td>{safe_role}</td>"
            f'<td class="num">{count}</td>'
            f"<td>{response_cell}</td>"
            "</tr>"
        )
    rows_joined = "\n".join(table_rows_html)

    # Triple-quoted f-string: the page is one template filled with our computed values.
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Response word counts — HCDE530 demo</title>
  <style>
    :root {{
      --bg: #0f1419;
      --panel: #1a2332;
      --muted: #8b9cb3;
      --text: #e8eef7;
      --accent: #5ec8ff;
      --accent-soft: rgba(94, 200, 255, 0.12);
      --border: #2a3648;
      --radius: 12px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
      background: radial-gradient(1200px 600px at 10% -10%, #1b2a44 0%, var(--bg) 55%);
      color: var(--text);
      line-height: 1.5;
      min-height: 100vh;
    }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1.25rem 3rem; }}
    header {{
      margin-bottom: 2rem;
      border-bottom: 1px solid var(--border);
      padding-bottom: 1.25rem;
    }}
    header h1 {{ font-size: 1.5rem; font-weight: 650; margin: 0 0 0.35rem; letter-spacing: -0.02em; }}
    header p {{ margin: 0; color: var(--muted); max-width: 52rem; font-size: 0.95rem; }}
    .source {{ margin-top: 0.75rem; font-size: 0.85rem; color: var(--muted); }}
    .source code {{ color: var(--accent); background: var(--accent-soft); padding: 0.1rem 0.35rem; border-radius: 6px; }}

    .kpis {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 1rem;
      margin-bottom: 2rem;
    }}
    .kpi {{
      background: linear-gradient(160deg, #1e2d45, var(--panel));
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1rem 1.15rem;
    }}
    .kpi .label {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }}
    .kpi .value {{ font-size: 1.65rem; font-weight: 700; margin-top: 0.2rem; color: var(--text); }}
    .kpi .unit {{ font-size: 0.85rem; color: var(--muted); font-weight: 500; }}

    .panel {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
      box-shadow: 0 18px 50px rgba(0,0,0,0.35);
    }}
    .panel-head {{
      padding: 1rem 1.25rem;
      border-bottom: 1px solid var(--border);
      display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between; gap: 0.5rem;
    }}
    .panel-head h2 {{ margin: 0; font-size: 1.05rem; }}
    .panel-head span {{ color: var(--muted); font-size: 0.85rem; }}

    table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
    th, td {{ padding: 0.75rem 1rem; text-align: left; vertical-align: top; border-bottom: 1px solid var(--border); }}
    th {{ background: rgba(0,0,0,0.2); color: var(--muted); font-weight: 600; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; }}
    tr:hover td {{ background: rgba(94, 200, 255, 0.04); }}
    .mono {{ font-variant-numeric: tabular-nums; font-family: ui-monospace, Consolas, monospace; white-space: nowrap; }}
    .num {{ font-variant-numeric: tabular-nums; text-align: right; width: 4.5rem; color: var(--accent); font-weight: 600; }}

    .response-details summary {{
      cursor: pointer;
      color: var(--text);
      list-style-position: outside;
    }}
    .response-full {{
      margin: 0.6rem 0 0;
      padding: 0.75rem 0.9rem;
      background: rgba(0,0,0,0.25);
      border-radius: 8px;
      border-left: 3px solid var(--accent);
      color: #dbe5f3;
      font-size: 0.88rem;
    }}
    footer {{
      margin-top: 2rem;
      font-size: 0.8rem;
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>Demo dashboard — word counts per response</h1>
      <p>
        Synthetic UX-role quotes for class. Words = split on whitespace (same rule as the Python script).
        Open this file directly in your browser — no server required.
      </p>
      <p class="source">Data: <code>{html.escape(filename)}</code> · Generated by <code>demo_word_count.py</code></p>
    </header>

    <section class="kpis" aria-label="Summary statistics">
      <div class="kpi"><div class="label">Total responses</div><div class="value">{total}</div></div>
      <div class="kpi"><div class="label">Shortest</div><div class="value">{shortest}</div><div class="unit">words</div></div>
      <div class="kpi"><div class="label">Longest</div><div class="value">{longest}</div><div class="unit">words</div></div>
      <div class="kpi"><div class="label">Average</div><div class="value">{average:.1f}</div><div class="unit">words</div></div>
    </section>

    <section class="panel" aria-label="All responses">
      <div class="panel-head">
        <h2>Responses</h2>
        <span>Click a row summary to expand the full quote</span>
      </div>
      <table>
        <thead>
          <tr><th>ID</th><th>Role</th><th>Words</th><th>Response</th></tr>
        </thead>
        <tbody>
{rows_joined}
        </tbody>
      </table>
    </section>

    <footer>
      HCDE530 week demo · static HTML · regenerate by running <code>python demo_word_count.py</code>
    </footer>
  </div>
</body>
</html>
"""

    with open(path, "w", encoding="utf-8", newline="\n") as out:
        out.write(doc)


# --- Build per-row summaries (used for both terminal print and HTML) --------------
print(f"{'ID':<6} {'Role':<22} {'Words':<6} {'Response (first 60 chars)'}")
print("-" * 75)

word_counts = []
# Each entry mirrors what we show in the dashboard table (keeps terminal + web in sync).
table_rows = []

for row in responses:
    participant = row["participant_id"]
    role = row["role"]
    response = row["response"]

    # Reuse the same word-count rule everywhere (single source of truth).
    count = count_words(response)
    word_counts.append(count)

    # Conditional: only add ellipsis when the text is longer than 60 characters.
    if len(response) > 60:
        preview = response[:60] + "..."
    else:
        preview = response

    table_rows.append(
        {
            "participant": participant,
            "role": role,
            "count": count,
            "preview": preview,
            "response_full": response,
        }
    )

    print(f"{participant:<6} {role:<22} {count:<6} {preview}")

# --- Terminal summary (same numbers as the KPI cards on the dashboard) -----------
print()
# ASCII-only line so Windows terminals using cp1252 do not raise UnicodeEncodeError.
print("-- Summary " + "-" * 40)
print(f"  Total responses : {len(word_counts)}")
print(f"  Shortest        : {min(word_counts)} words")
print(f"  Longest         : {max(word_counts)} words")
print(f"  Average         : {sum(word_counts) / len(word_counts):.1f} words")

# --- Write the browser dashboard -------------------------------------------------
write_dashboard_html(table_rows, word_counts, "Dashboard.html")
print()
print("Wrote Dashboard.html - open it in your browser (double-click or drag into a tab).")
