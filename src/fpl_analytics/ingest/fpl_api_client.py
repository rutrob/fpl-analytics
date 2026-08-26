import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE_URL = "https://fantasy.premierleague.com/api"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def get_bootstrap_static() -> dict:
    response = requests.get(f"{BASE_URL}/bootstrap-static/")
    response.raise_for_status()
    return response.json()


def get_element_summary(player_id: int) -> dict:
    response = requests.get(f"{BASE_URL}/element-summary/{player_id}/")
    response.raise_for_status()
    return response.json()


def get_fixtures() -> list:
    response = requests.get(f"{BASE_URL}/fixtures/")
    response.raise_for_status()
    return response.json()


def save_raw_json(data, name: str) -> Path:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    filepath = RAW_DATA_DIR / f"{name}_{timestamp}.json"
    filepath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return filepath


def fetch_all_element_summaries(player_ids: list[int], delay: float = 0.3) -> dict:
    all_summaries = {}
    for i, player_id in enumerate(player_ids, start=1):
        all_summaries[player_id] = get_element_summary(player_id)
        if i % 50 == 0:
            print(f"Pobrano {i}/{len(player_ids)} zawodnikow")
        time.sleep(delay)
    return all_summaries


if __name__ == "__main__":
    bootstrap = get_bootstrap_static()
    save_raw_json(bootstrap, "bootstrap_static")
    player_ids = [p["id"] for p in bootstrap["elements"]]
    print(f"Znaleziono {len(player_ids)} zawodnikow")

    fixtures = get_fixtures()
    save_raw_json(fixtures, "fixtures")
    print(f"Pobrano {len(fixtures)} meczow")

    # summaries = fetch_all_element_summaries(player_ids)
    summaries = fetch_all_element_summaries(player_ids[:5])
    save_raw_json(summaries, "element_summaries")
    print(f"Pobrano historie dla {len(summaries)} zawodnikow")