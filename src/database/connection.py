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
            codigo_convite TEXT UNIQUE,
            dono_id INTEGER,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            despensa_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            ativo BOOLEAN NOT NULL DEFAULT 1,
            google_id TEXT,
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

        CREATE TABLE IF NOT EXISTS codigos_verificacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            codigo TEXT NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'cadastro',
            expira_em TIMESTAMP NOT NULL,
            usado BOOLEAN NOT NULL DEFAULT 0,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS solicitacoes_adesao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            despensa_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pendente',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            respondido_em TIMESTAMP,
            FOREIGN KEY (despensa_id) REFERENCES despensas(id) ON DELETE CASCADE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_itens_despensa ON itens(despensa_id);
        CREATE INDEX IF NOT EXISTS idx_usuarios_despensa ON usuarios(despensa_id);
        CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
        CREATE INDEX IF NOT EXISTS idx_despensas_codigo ON despensas(codigo_convite);
        CREATE INDEX IF NOT EXISTS idx_codigos_email ON codigos_verificacao(email);
        CREATE INDEX IF NOT EXISTS idx_solicitacoes_despensa ON solicitacoes_adesao(despensa_id);
        CREATE INDEX IF NOT EXISTS idx_solicitacoes_usuario ON solicitacoes_adesao(usuario_id);
    """)

    # Migrações seguras para tabelas existentes
    _migrar_colunas_se_necessario(conn)

    conn.commit()


def _migrar_colunas_se_necessario(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()

    # Colunas em despensas
    cursor.execute("PRAGMA table_info(despensas);")
    cols_despensa = {row["name"] for row in cursor.fetchall()}
    if "codigo_convite" not in cols_despensa:
        cursor.execute("ALTER TABLE despensas ADD COLUMN codigo_convite TEXT UNIQUE;")
    if "dono_id" not in cols_despensa:
        cursor.execute("ALTER TABLE despensas ADD COLUMN dono_id INTEGER;")

    # Colunas em usuarios
    cursor.execute("PRAGMA table_info(usuarios);")
    cols_usuarios = {row["name"] for row in cursor.fetchall()}
    if "ativo" not in cols_usuarios:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT 1;")
    if "google_id" not in cols_usuarios:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN google_id TEXT;")

