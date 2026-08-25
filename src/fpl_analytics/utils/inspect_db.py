import duckdb
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[3] / "data" / "fpl.duckdb"

if __name__ == "__main__":
    con = duckdb.connect(str(DB_PATH))
    print(con.execute("SELECT * FROM stg_players LIMIT 5").df())
    print(con.execute("SELECT * FROM stg_teams LIMIT 5").df())
    con.close()