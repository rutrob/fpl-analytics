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


def build_player_gameweek_history_df(element_summaries: dict) -> pd.DataFrame:
    columns = [
        "element", "round", "fixture", "opponent_team", "was_home",
        "total_points", "minutes", "starts",
        "goals_scored", "assists", "clean_sheets", "goals_conceded",
        "bonus", "bps", "influence", "creativity", "threat", "ict_index",
        "expected_goals", "expected_assists", "expected_goal_involvements",
        "expected_goals_conceded",
        "value", "selected", "transfers_in", "transfers_out",
        "kickoff_time",
    ]

    all_rows = []
    for player_id, summary in element_summaries.items():
        history = summary.get("history", [])
        all_rows.extend(history)

    if not all_rows:
        raise ValueError("Brak danych history w element_summaries")

    df = pd.DataFrame(all_rows)
    df = df[columns]
    df = df.rename(columns={"element": "player_id"})

    float_columns = [
        "influence", "creativity", "threat", "ict_index",
        "expected_goals", "expected_assists",
        "expected_goal_involvements", "expected_goals_conceded",
    ]
    for col in float_columns:
        df[col] = df[col].astype(float)

    df["kickoff_time"] = pd.to_datetime(df["kickoff_time"])

    return df


def build_fixtures_df(raw: list) -> pd.DataFrame:
    df = pd.DataFrame(raw)
    columns = [
        "id", "event", "team_h", "team_a", "team_h_score", "team_a_score",
        "kickoff_time", "finished", "team_h_difficulty", "team_a_difficulty",
    ]
    df = df[columns]
    df = df.rename(columns={"id": "fixture_id", "event": "gameweek"})
    df["kickoff_time"] = pd.to_datetime(df["kickoff_time"])
    return df


def load_all_to_duckdb(
    players_df: pd.DataFrame,
    teams_df: pd.DataFrame,
    gameweek_history_df: pd.DataFrame,
    fixtures_df: pd.DataFrame,
) -> None:
    con = duckdb.connect(str(DB_PATH))
    con.execute("CREATE OR REPLACE TABLE stg_players AS SELECT * FROM players_df")
    con.execute("CREATE OR REPLACE TABLE stg_teams AS SELECT * FROM teams_df")
    con.execute("CREATE OR REPLACE TABLE fact_player_gameweek AS SELECT * FROM gameweek_history_df")
    con.execute("CREATE OR REPLACE TABLE stg_fixtures AS SELECT * FROM fixtures_df")
    con.close()


if __name__ == "__main__":
    bootstrap_raw = load_latest_raw_json("bootstrap_static")
    players_df = build_players_df(bootstrap_raw)
    teams_df = build_teams_df(bootstrap_raw)

    summaries_raw = load_latest_raw_json("element_summaries")
    gameweek_history_df = build_player_gameweek_history_df(summaries_raw)

    fixtures_raw = load_latest_raw_json("fixtures")
    fixtures_df = build_fixtures_df(fixtures_raw)

    load_all_to_duckdb(players_df, teams_df, gameweek_history_df, fixtures_df)

    print(
        f"Zaladowano {len(players_df)} zawodnikow, {len(teams_df)} druzyn, "
        f"{len(gameweek_history_df)} wierszy fact_player_gameweek, "
        f"{len(fixtures_df)} meczow"
    )