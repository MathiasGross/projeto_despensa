import sqlite3


def get_connection(db_path: str = "despensa.db") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS despensas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            despensa_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (despensa_id) REFERENCES despensas(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            despensa_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL DEFAULT 0,
            quantidade_minima INTEGER NOT NULL DEFAULT 1,
            local TEXT NOT NULL DEFAULT '',
            obs TEXT DEFAULT '',
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (despensa_id) REFERENCES despensas(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_itens_despensa ON itens(despensa_id);
        CREATE INDEX IF NOT EXISTS idx_usuarios_despensa ON usuarios(despensa_id);
        CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
    """)

    conn.commit()
