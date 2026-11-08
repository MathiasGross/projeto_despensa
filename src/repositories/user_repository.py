import sqlite3
from src.models.despensa import Despensa
from src.models.usuario import Usuario


class UserRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def criar_despensa(self, nome: str) -> Despensa:
        nome_limpo = nome.strip() if nome else ""
        if not nome_limpo:
            raise ValueError("O nome da despensa não pode ser vazio.")

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO despensas (nome) VALUES (?)", (nome_limpo,))
        self.conn.commit()
        despensa_id = cursor.lastrowid
        return Despensa(id=despensa_id, nome=nome_limpo)

    def buscar_despensa_por_id(self, despensa_id: int) -> Despensa | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome, criado_em FROM despensas WHERE id = ?", (despensa_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return Despensa(id=row["id"], nome=row["nome"], criado_em=row["criado_em"])

    def criar_usuario(
        self, despensa_id: int, nome: str, email: str, senha_hash: str
    ) -> Usuario:
        nome_limpo = nome.strip() if nome else ""
        email_limpo = email.strip().lower() if email else ""

        if not nome_limpo:
            raise ValueError("O nome do usuário não pode ser vazio.")
        if not email_limpo or "@" not in email_limpo:
            raise ValueError("E-mail inválido.")
        if not senha_hash:
            raise ValueError("A senha não pode ser vazia.")

        # Verifica se despensa existe
        if not self.buscar_despensa_por_id(despensa_id):
            raise ValueError(f"Despensa com ID {despensa_id} não encontrada.")

        # Verifica e-mail duplicado
        if self.buscar_usuario_por_email(email_limpo):
            raise ValueError(f"Já existe um usuário cadastrado com o e-mail '{email_limpo}'.")

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO usuarios (despensa_id, nome, email, senha_hash)
            VALUES (?, ?, ?, ?)
            """,
            (despensa_id, nome_limpo, email_limpo, senha_hash),
        )
        self.conn.commit()
        usuario_id = cursor.lastrowid
        return Usuario(
            id=usuario_id,
            despensa_id=despensa_id,
            nome=nome_limpo,
            email=email_limpo,
            senha_hash=senha_hash,
        )

    def buscar_usuario_por_email(self, email: str) -> Usuario | None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, despensa_id, nome, email, senha_hash, criado_em
            FROM usuarios
            WHERE email = ?
            """,
            (email.strip().lower(),),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return Usuario(
            id=row["id"],
            despensa_id=row["despensa_id"],
            nome=row["nome"],
            email=row["email"],
            senha_hash=row["senha_hash"],
            criado_em=row["criado_em"],
        )

    def buscar_usuario_por_id(self, usuario_id: int) -> Usuario | None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, despensa_id, nome, email, senha_hash, criado_em
            FROM usuarios
            WHERE id = ?
            """,
            (usuario_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return Usuario(
            id=row["id"],
            despensa_id=row["despensa_id"],
            nome=row["nome"],
            email=row["email"],
            senha_hash=row["senha_hash"],
            criado_em=row["criado_em"],
        )

    def listar_usuarios_por_despensa(self, despensa_id: int) -> list[Usuario]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, despensa_id, nome, email, senha_hash, criado_em
            FROM usuarios
            WHERE despensa_id = ?
            ORDER BY nome ASC
            """,
            (despensa_id,),
        )
        rows = cursor.fetchall()
        return [
            Usuario(
                id=row["id"],
                despensa_id=row["despensa_id"],
                nome=row["nome"],
                email=row["email"],
                senha_hash=row["senha_hash"],
                criado_em=row["criado_em"],
            )
            for row in rows
        ]
