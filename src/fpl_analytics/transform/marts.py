import duckdb
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "data" / "fpl.duckdb"


def build_mart_player_gameweek() -> None:
    con = duckdb.connect(str(DB_PATH))
    con.execute("""
        CREATE OR REPLACE TABLE mart_player_gameweek AS
        SELECT
            f.player_id,
            p.web_name,
            p.element_type,
            t_own.short_name AS team,
            f.round AS gameweek,
            f.total_points,
            f.was_home,
            t_opp.short_name AS opponent,
            f.minutes,
            f.starts,
            f.goals_scored,
            f.assists,
            f.clean_sheets,
            f.goals_conceded,
            f.bonus,
            f.bps,
            f.influence,
            f.creativity,
            f.threat,
            f.ict_index,
            f.expected_goals,
            f.expected_assists,
            f.expected_goal_involvements,
            f.expected_goals_conceded,
            f.value AS price_at_gameweek,
            f.selected,
            f.transfers_in,
            f.transfers_out,
            f.kickoff_time
        FROM fact_player_gameweek f
        JOIN stg_players p ON f.player_id = p.id
        JOIN stg_teams t_own ON p.team = t_own.id
        JOIN stg_teams t_opp ON f.opponent_team = t_opp.id
    """)
    con.close()


if __name__ == "__main__":
    build_mart_player_gameweek()
    con = duckdb.connect(str(DB_PATH))
    count = con.execute("SELECT COUNT(*) FROM mart_player_gameweek").fetchone()[0]
    con.close()
    print(f"Zbudowano mart_player_gameweek: {count} wierszy")