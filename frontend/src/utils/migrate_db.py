import sqlite3
from pathlib import Path

DB_PATH = Path("data/stocks.db")

def add_column_if_not_exists(conn, table, column, coltype):
    # Check if column exists
    cur = conn.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cur.fetchall()]
    if column not in columns:
        print(f"Adding column '{column}' to '{table}'...")
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")

def migrate():
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}. Nothing to migrate.")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        # USERS table
        add_column_if_not_exists(conn, "users", "investment_goal", "TEXT DEFAULT 'growth'")
        add_column_if_not_exists(conn, "users", "portfolio_value", "REAL DEFAULT 0.0")
        add_column_if_not_exists(conn, "users", "cash_balance", "REAL DEFAULT 10000.0")
        add_column_if_not_exists(conn, "users", "preferred_sectors", "TEXT DEFAULT '[]'")
        add_column_if_not_exists(conn, "users", "blacklisted_stocks", "TEXT DEFAULT '[]'")
        add_column_if_not_exists(conn, "users", "last_active", "TIMESTAMP")
        # Set default for existing rows if needed
        conn.execute("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE last_active IS NULL")
        # Add more columns/tables as needed

        # PORTFOLIO table
        add_column_if_not_exists(conn, "portfolio", "target_price", "REAL")
        add_column_if_not_exists(conn, "portfolio", "stop_loss", "REAL")
        add_column_if_not_exists(conn, "portfolio", "notes", "TEXT")
        add_column_if_not_exists(conn, "portfolio", "position_size", "REAL DEFAULT 0.0")

        # SIGNALS table
        add_column_if_not_exists(conn, "signals", "expected_return", "REAL")
        add_column_if_not_exists(conn, "signals", "risk_level", "TEXT")
        add_column_if_not_exists(conn, "signals", "supporting_indicators", "TEXT")
        add_column_if_not_exists(conn, "signals", "timeframe", "TEXT")

        conn.commit()
        print("Migration complete!")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
