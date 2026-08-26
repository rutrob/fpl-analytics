import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

if __name__ == "__main__":
    files = sorted(RAW_DATA_DIR.glob("element_summaries_*.json"))
    if not files:
        raise FileNotFoundError(f"Nic nie znaleziono w {RAW_DATA_DIR}")

    data = json.loads(files[-1].read_text(encoding="utf-8"))

    first_id = list(data.keys())[0]
    print("Klucze gorne:", data[first_id].keys())
    print("Liczba gameweekow w history:", len(data[first_id]["history"]))
    print("Przyklad wpisu z history:")
    print(json.dumps(data[first_id]["history"][0], indent=2, ensure_ascii=False))