from pathlib import Path

root = Path(__file__).resolve().parents[1]
ui = root / "ui.html"
b64_path = root / "scripts" / "loading-gif-b64.txt"

if not b64_path.exists():
    gif = root / "loading.gif"
    if not gif.exists():
        raise SystemExit("loading.gif not found")
    import base64

    b64_path.write_text(base64.b64encode(gif.read_bytes()).decode("ascii"), encoding="utf-8")

b64 = b64_path.read_text(encoding="utf-8").strip()
src = f"data:image/gif;base64,{b64}"

text = ui.read_text(encoding="utf-8")
old = 'src="loading.gif"'
if old not in text:
    if "data:image/gif;base64," in text and "loading-gif" in text:
        print("Already inlined")
        raise SystemExit(0)
    raise SystemExit("anchor not found in ui.html")

ui.write_text(text.replace(old, f'src="{src}"', 1), encoding="utf-8")
print("Inlined loading GIF into ui.html")
