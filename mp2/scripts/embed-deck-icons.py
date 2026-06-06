"""Inline deck icon PNGs into ui.html (Figma plugin UI cannot load local files)."""
import base64
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
ui = root / "ui.html"
decks_dir = root / "assets" / "decks"

DECK_FILES = {
    "Inspiration": "inspiration.png",
    "Connections": "connections.png",
    "Interfacing": "interfacing.png",
    "thread": "thread.png",
}


def data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def indicator_markup(src: str) -> str:
    return (
        '<span class="deck-indicator">'
        f'<img src="{src}" alt="" aria-hidden="true">'
        "</span>"
    )


def replace_grid_indicator(text: str, deck: str, markup: str) -> str:
    pattern = (
        rf'(<button[^>]*data-deck="{re.escape(deck)}"[^>]*>[\s\S]*?)'
        rf'<span class="deck-indicator">\s*<svg[\s\S]*?</svg>\s*</span>'
    )
    text, n = re.subn(pattern, rf"\1{markup}", text, count=1)
    if n != 1:
        raise SystemExit(f"deck grid indicator not found for {deck}")
    return text


def main() -> None:
    text = ui.read_text(encoding="utf-8")
    src_by_deck = {deck: data_uri(decks_dir / filename) for deck, filename in DECK_FILES.items()}

    deck_indicators_block = "    const DECK_INDICATORS = {\n"
    for deck in DECK_FILES:
        markup = indicator_markup(src_by_deck[deck]).replace('"', '\\"')
        deck_indicators_block += f'      {deck}: "{markup}",\n'
    deck_indicators_block += "    };"

    text, count = re.subn(
        r"    const DECK_INDICATORS = \{[\s\S]*?\n    \};",
        deck_indicators_block,
        text,
        count=1,
    )
    if count != 1:
        raise SystemExit("DECK_INDICATORS block not found")

    for deck, src in src_by_deck.items():
        text = replace_grid_indicator(text, deck, indicator_markup(src))

    ui.write_text(text, encoding="utf-8")
    print("Embedded deck icons into ui.html")


if __name__ == "__main__":
    main()
