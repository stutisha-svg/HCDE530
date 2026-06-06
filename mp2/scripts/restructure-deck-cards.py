"""Restructure View 2 deck cards: full-bleed art + scrim + text."""
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
ui = root / "ui.html"
text = ui.read_text(encoding="utf-8")

DECKS = ["Inspiration", "Connections", "Interfacing", "thread"]


def fix_mime(src: str) -> str:
    if src.startswith("data:image/png;base64,/9j/"):
        return src.replace("data:image/png;base64,", "data:image/jpeg;base64,", 1)
    return src


def restructure_button(text: str, deck: str) -> str:
    pattern = (
        rf'(<button[^>]*data-deck="{re.escape(deck)}"[^>]*>\s*)'
        rf'<div class="buddy-card__body">\s*'
        rf'<span class="deck-label[^"]*">\s*'
        rf'<span class="deck-indicator"><img src="([^"]+)"[^>]*></span>\s*'
        rf'([^<]+?)\s*</span>\s*'
        rf'<p class="buddy-card__deck-desc">([^<]*)</p>\s*'
        rf'</div>\s*</button>'
    )

    def repl(match: re.Match) -> str:
        open_btn, src, label, desc = match.groups()
        src = fix_mime(src)
        return (
            f"{open_btn}"
            f'<img class="buddy-card__deck-art" src="{src}" alt="" aria-hidden="true">\n'
            f'          <div class="buddy-card__deck-scrim" aria-hidden="true"></div>\n'
            f'          <div class="buddy-card__body">\n'
            f'            <span class="deck-label text-label">{label.strip()}</span>\n'
            f'            <p class="buddy-card__deck-desc">{desc}</p>\n'
            f"          </div>\n"
            f"        </button>"
        )

    text, n = re.subn(pattern, repl, text, count=1, flags=re.DOTALL)
    if n != 1:
        raise SystemExit(f"Could not restructure deck button: {deck}")
    return text


for deck in DECKS:
    text = restructure_button(text, deck)

# Fix MIME in DECK_INDICATORS small icons too
text = text.replace("data:image/png;base64,/9j/", "data:image/jpeg;base64,/9j/")

ui.write_text(text, encoding="utf-8")
print("Restructured deck cards in ui.html")
