import json
from pathlib import Path

import duckdb
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DB_PATH = PROJECT_ROOT / "data" / "fpl.duckdb"


def load_latest_raw_json(prefix: str) -> dict:
    files = sorted(DATA_RAW_DIR.glob(f"{prefix}_*.json"))
    if not files:
        raise FileNotFoundError(f"Brak plikow pasujacych do {prefix}_*.json w {DATA_RAW_DIR}")
    latest = files[-1]
    return json.loads(latest.read_text(encoding="utf-8"))


def build_players_df(raw: dict) -> pd.DataFrame:
    df = pd.DataFrame(raw["elements"])
    columns = [
        "id", "first_name", "second_name", "web_name", "team",
        "element_type", "now_cost", "total_points", "form",
        "points_per_game", "selected_by_percent", "minutes",
        "goals_scored", "assists", "clean_sheets", "bonus",
        "expected_goals", "expected_assists",
    ]
    return df[columns]


def build_teams_df(raw: dict) -> pd.DataFrame:
    df = pd.DataFrame(raw["teams"])
    columns = ["id", "name", "short_name", "strength"]
    return df[columns]


def load_to_duckdb(players_df: pd.DataFrame, teams_df: pd.DataFrame) -> None:
    con = duckdb.connect(str(DB_PATH))
    con.execute("CREATE OR REPLACE TABLE stg_players AS SELECT * FROM players_df")
    con.execute("CREATE OR REPLACE TABLE stg_teams AS SELECT * FROM teams_df")
    con.close()


if __name__ == "__main__":
    raw = load_latest_raw_json("bootstrap_static")
    players_df = build_players_df(raw)
    teams_df = build_teams_df(raw)
    load_to_duckdb(players_df, teams_df)
    print(f"Zaladowano {len(players_df)} zawodnikow i {len(teams_df)} druzyn do {DB_PATH}")