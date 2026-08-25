import json
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE_URL = "https://fantasy.premierleague.com/api"
RAW_DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"


def get_bootstrap_static() -> dict:
    response = requests.get(f"{BASE_URL}/bootstrap-static/")
    response.raise_for_status()
    return response.json()


def save_raw_json(data: dict, name: str) -> Path:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    filepath = RAW_DATA_DIR / f"{name}_{timestamp}.json"
    filepath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return filepath


if __name__ == "__main__":
    data = get_bootstrap_static()
    saved_path = save_raw_json(data, "bootstrap_static")
    print(f"Zapisano do: {saved_path}")
    print("Liczba zawodnikow:", len(data["elements"]))