from pathlib import Path

root = Path(__file__).resolve().parents[1]
ui = root / "ui.html"
b64 = (root / "scripts" / "icon-b64.txt").read_text().strip()
src = f"data:image/png;base64,{b64}"

css = """
    .plugin-logo {
      display: block;
      width: 56px;
      height: auto;
      flex-shrink: 0;
    }

    .loading-screen__logo {
      width: 72px;
      height: auto;
    }

    .view-1__brand {
      display: flex;
      align-items: center;
      gap: var(--space-sm);
      margin-bottom: var(--space-xs);
    }
"""

html_loading = (
    f'    <img class="plugin-logo loading-screen__logo" src="{src}" '
    f'alt="" width="72" height="72" aria-hidden="true">\n'
)
html_view1 = f"""      <div class="view-1__brand">
        <img class="plugin-logo" src="{src}" alt="" width="56" height="56" aria-hidden="true">
      </div>

"""

text = ui.read_text(encoding="utf-8")

if ".plugin-logo" in text:
    print("Already patched")
    raise SystemExit(0)

if "    .loading-shapes {" not in text:
    raise SystemExit("CSS anchor missing")

text = text.replace("    .loading-shapes {", css + "    .loading-shapes {", 1)

old_loading = """  <div id="loading-screen" class="loading-screen" aria-hidden="true">
    <div class="loading-shapes">"""
new_loading = f"""  <div id="loading-screen" class="loading-screen" aria-hidden="true">
{html_loading.rstrip()}
    <div class="loading-shapes view--hidden">"""
text = text.replace(old_loading, new_loading, 1)

old_view1 = """    <div class="view-1__content">
      <h1 class="view-1__heading">What stayed with you today?</h1>"""
text = text.replace(
    old_view1,
    f"""    <div class="view-1__content">
{html_view1.rstrip()}
      <h1 class="view-1__heading">What stayed with you today?</h1>""",
    1,
)

ui.write_text(text, encoding="utf-8")
print("Patched ui.html with inlined plugin logo")
