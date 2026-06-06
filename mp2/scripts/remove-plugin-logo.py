from pathlib import Path
import re

ui = Path(__file__).resolve().parents[1] / "ui.html"
text = ui.read_text(encoding="utf-8")

# Remove logo CSS block
text = re.sub(
    r"\n\n    \.plugin-logo \{.*?\n    \.view-1__brand \{.*?\n    \}",
    "",
    text,
    count=1,
    flags=re.DOTALL,
)

# Restore loading screen
text = re.sub(
    r'  <div id="loading-screen" class="loading-screen" aria-hidden="true">\n'
    r'    <img class="plugin-logo loading-screen__logo" src="data:image/png;base64,[^"]+" alt="" width="72" height="72" aria-hidden="true">\n'
    r'    <div class="loading-shapes view--hidden">',
    '  <div id="loading-screen" class="loading-screen" aria-hidden="true">\n'
    '    <div class="loading-shapes">',
    text,
    count=1,
)

# Remove View 1 brand block
text = re.sub(
    r'\n      <div class="view-1__brand">\n'
    r'        <img class="plugin-logo" src="data:image/png;base64,[^"]+" alt="" width="56" height="56" aria-hidden="true">\n'
    r'      </div>',
    "",
    text,
    count=1,
)

if ".plugin-logo" in text:
    raise SystemExit("Failed to remove all plugin-logo references")

ui.write_text(text, encoding="utf-8")
print("Removed inlined plugin logo from ui.html")
