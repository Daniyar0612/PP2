try:
    import psycopg2
    HAS_PG = True
except ImportError:
    HAS_PG = False

DB_CONFIG = {
    "dbname": "snake_db",
    "user": "postgres",
    "password": "your_password",
    "host": "localhost",
    "port": 5432,
}


def _connect():
    if not HAS_PG:
        return None
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception:
        return None


def init_db():
    conn = _connect()
    if not conn:
        return
    with conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id       SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions (
                id            SERIAL PRIMARY KEY,
                player_id     INTEGER REFERENCES players(id),
                score         INTEGER   NOT NULL,
                level_reached INTEGER   NOT NULL,
                played_at     TIMESTAMP DEFAULT NOW()
            )
        """)
    conn.close()


def get_or_create_player(username: str) -> int | None:
    conn = _connect()
    if not conn:
        return None
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM players WHERE username = %s", (username,))
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute("INSERT INTO players(username) VALUES(%s) RETURNING id",
                    (username,))
        return cur.fetchone()[0]


def save_session(player_id: int, score: int, level: int):
    if player_id is None:
        return
    conn = _connect()
    if not conn:
        return
    with conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO game_sessions(player_id, score, level_reached)
            VALUES (%s, %s, %s)
        """, (player_id, score, level))
    conn.close()


def get_personal_best(player_id: int) -> int:
    if player_id is None:
        return 0
    conn = _connect()
    if not conn:
        return 0
    cur = conn.cursor()
    cur.execute("""
        SELECT COALESCE(MAX(score), 0)
        FROM game_sessions
        WHERE player_id = %s
    """, (player_id,))
    best = cur.fetchone()[0]
    conn.close()
    return best


def get_leaderboard(limit: int = 10) -> list[tuple]:
    conn = _connect()
    if not conn:
        return []
    cur = conn.cursor()
    cur.execute("""
        SELECT p.username, gs.score, gs.level_reached,
               TO_CHAR(gs.played_at, 'YYYY-MM-DD')
        FROM game_sessions gs
        JOIN players p ON p.id = gs.player_id
        ORDER BY gs.score DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return [(i+1, *row) for i, row in enumerate(rows)]
