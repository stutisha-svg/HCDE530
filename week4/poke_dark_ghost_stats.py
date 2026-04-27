"""
Fetch 50+ dark/ghost Pokemon from PokeAPI (Gen 1-4), then export stats to CSV.

Source API docs: https://pokeapi.co
"""

from __future__ import annotations #annotations are used to type hint the code

import csv #csv module is used to read and write csv files
import json
import os #os module is used to interact with the operating system  
import sys #sys module is used to interact with the system
import time #time module is used to work with time
import urllib.parse #urllib.parse module is used to parse URLs
import urllib.request #urllib.request module is used to make HTTP requests
from pathlib import Path #pathlib module is used to work with file paths

#API base URL and env file path and output CSV file path and gen 4 max id and type names and request pause seconds
API_BASE = "https://pokeapi.co/api/v2"  # Base endpoint; we call /type/{name} and /pokemon/{id}.
ENV_PATH = Path(__file__).resolve().parent / ".env"
OUTPUT_CSV = Path(__file__).resolve().parent / "pokemon_dark_ghost_gen1_4.csv"
GEN4_MAX_ID = 493  # National Dex through Diamond/Pearl/Platinum era.
TYPE_NAMES = ("dark", "ghost")
REQUEST_PAUSE_SEC = 0.05

#load dotenv file and return a dictionary of key-value pairs
def load_dotenv(path: Path) -> dict[str, str]:
    out: dict[str, str] = {} #empty dictionary to store key-value pairs
    if not path.is_file():
        return out
    for raw in path.read_text(encoding="utf-8").splitlines():
        #split lines into key-value pairs
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line: #if line is empty, starts with #, or does not contain =, skip it
            continue
        key, _, val = line.partition("=") #partition the line into key, _, val
        out[key.strip()] = val.strip().strip('"').strip("'")
    return out

#return the value of the environment variable or the default value if the environment variable is not set
def env_var(name: str, file_env: dict[str, str], default: str = "") -> str:
    return (os.environ.get(name) or file_env.get(name) or default).strip()

#make an HTTP request to the URL and return the JSON response
def get_json(url: str, api_key: str) -> dict:
    # PokéAPI is public; this header simply links your .env API_KEY into requests.
    headers = {"User-Agent": "HCDE530-week4-pokeapi"}
    if api_key:
        headers["X-API-Key"] = api_key
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        # Returns parsed JSON objects, e.g.:
        # - /type/{name}: {"pokemon": [{"pokemon": {"name", "url"}, "slot": ...}, ...], ...}
        # - /pokemon/{id}: {"id","name","types","base_experience","height","weight","stats","species",...}
        return json.load(resp)


def pokemon_id_from_url(url: str) -> int | None:
    # Example URL: https://pokeapi.co/api/v2/pokemon/94/
    path = urllib.parse.urlparse(url).path.rstrip("/")
    tail = path.split("/")[-1]
    return int(tail) if tail.isdigit() else None


def species_id_from_pokemon_payload(payload: dict) -> int | None:
    species_url = str(payload.get("species", {}).get("url") or "")
    return pokemon_id_from_url(species_url)

#collect candidate payloads from the API
def collect_candidate_payloads(api_key: str) -> list[dict]:
    urls: dict[str, str] = {}
    for type_name in TYPE_NAMES:
        # Parameter used: type_name in /type/{type_name}, where type_name is "dark" or "ghost".
        payload = get_json(f"{API_BASE}/type/{type_name}", api_key) #get the payload from the API
        for item in payload.get("pokemon", []):
            poke = item.get("pokemon", {}) #get the pokemon from the payload
            url = str(poke.get("url") or "")
            if url:
                urls[url] = url #add the url to the dictionary
        time.sleep(REQUEST_PAUSE_SEC)

    out: list[dict] = []
    for idx, url in enumerate(sorted(urls.keys()), start=1):
        payload = get_json(url, api_key) #get the payload from the API
        sid = species_id_from_pokemon_payload(payload) #get the species id from the payload
        # Platinum-era filter by species id: include forms/variants of Gen 1-4 species.
        if sid and sid <= GEN4_MAX_ID:
            out.append(payload) #add the payload to the list
        if idx % 25 == 0:
            print(f"Scanned {idx}/{len(urls)} candidates...") #print the progress
        time.sleep(REQUEST_PAUSE_SEC)
    return out


#normalize the types
def normalize_types(types_block: list[dict]) -> str:
    sorted_types = sorted(types_block, key=lambda t: int(t.get("slot", 99))) #sort the types by the slot
    names = [str(t.get("type", {}).get("name") or "") for t in sorted_types]
    return "|".join([n for n in names if n])


def stats_map(stats_block: list[dict]) -> dict[str, int]:
    mapped = {str(s.get("stat", {}).get("name") or ""): int(s.get("base_stat") or 0) for s in stats_block}
    return {
        # hp: total hit points (how much damage a Pokemon can absorb before fainting).
        "hp": mapped.get("hp", 0),
        # attack: physical power used for contact/physical moves.
        "attack": mapped.get("attack", 0),
        # defense: resistance against incoming physical damage.
        "defense": mapped.get("defense", 0),
        # special_attack: power for special/energy-based moves.
        "special_attack": mapped.get("special-attack", 0),
        # special_defense: resistance against special/energy-based attacks.
        "special_defense": mapped.get("special-defense", 0),
        # speed: determines turn order; higher speed usually moves first.
        "speed": mapped.get("speed", 0),
    }


def print_ascii_banner(name: str) -> None:
    art = r"""
          _.--'""`-.
        ,'          `.
      ,'   .-""-.     \
     /    /  _   \     ;
    ;    |  ( )  |    /
    |     \  ^  /    /
    ;      `---'   .'
     \   DARK/GHOST /
      `.         ,'
        `-.___.-'
    """
    print(art)
    print(f"First Pokemon loaded: {name}")

#fetch the rows from the API
def fetch_rows(candidates: list[dict], target_count: int) -> list[dict[str, int | str]]:
    rows: list[dict[str, int | str]] = []
    printed_first = False
    total = min(len(candidates), max(target_count, 50)) #get the total number of candidates

    for idx, payload in enumerate(candidates[:total], start=1):
        row_stats = stats_map(payload.get("stats", []))
        species_id = species_id_from_pokemon_payload(payload) or 0
        row = {
            "id": int(payload.get("id") or 0),  # Pokemon form ID from /pokemon/{id}.
            "species_id": species_id,  # National species ID (used to keep Gen 1-4 species only).
            "name": str(payload.get("name") or ""),  # Pokemon/form name (e.g., "gengar-mega").
            "types": normalize_types(payload.get("types", [])),  # Primary/secondary type names joined by "|".
            "base_experience": int(payload.get("base_experience") or 0),  # Base EXP yielded when defeated.
            "height": int(payload.get("height") or 0),  # Height in decimeters.
            "weight": int(payload.get("weight") or 0),  # Weight in hectograms.
            **row_stats,
        }
        rows.append(row)

        if not printed_first:
            print_ascii_banner(row["name"])
            printed_first = True

        print(f"[{idx}/{total}] fetched {row['name']}")
        time.sleep(REQUEST_PAUSE_SEC)

    return rows

#write the rows to a CSV file
def write_csv(path: Path, rows: list[dict[str, int | str]]) -> None:
    fields = [
        "id",
        "species_id",
        "name",
        "types",
        "base_experience",
        "height",
        "weight",
        "hp",
        "attack",
        "defense",
        "special_attack",
        "special_defense",
        "speed",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

#main function
def main() -> int:
    file_env = load_dotenv(ENV_PATH) #load the environment variables from the .env file
    api_key = env_var("API_KEY", file_env, "")
    target_count = int(env_var("POKEMON_TARGET_COUNT", file_env, "55") or 55)

    candidates = collect_candidate_payloads(api_key) #collect the candidate payloads from the API
    if len(candidates) < 50:
        print(
            f"Only {len(candidates)} dark/ghost entries found with species_id <= {GEN4_MAX_ID}.",
            file=sys.stderr,
        )
        return 1
    #fetch the rows from the API
    rows = fetch_rows(candidates, target_count)
    write_csv(OUTPUT_CSV, rows) #write the rows to a CSV file
    print(f"\nWrote {len(rows)} rows to {OUTPUT_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
