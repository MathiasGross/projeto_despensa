from datetime import datetime, timedelta
import secrets
import sqlite3
import string
from src.models.despensa import Despensa
from src.models.solicitacao_adesao import SolicitacaoAdesao
from src.models.usuario import Usuario

CARACTERES_CODIGO = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"


def gerar_codigo_despensa(tamanho: int = 6) -> str:
    sufixo = "".join(secrets.choice(CARACTERES_CODIGO) for _ in range(tamanho))
    return f"DESP-{sufixo}"


class UserRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def criar_despensa(
        self,
        nome: str,
        dono_id: int | None = None,
        codigo_convite: str | None = None,
    ) -> Despensa:
        nome_limpo = nome.strip() if nome else ""
        if not nome_limpo:
            raise ValueError("O nome da despensa não pode ser vazio.")

        cursor = self.conn.cursor()

        if not codigo_convite:
            # Gera código único
            for _ in range(10):
                candidato = gerar_codigo_despensa()
                cursor.execute(
                    "SELECT id FROM despensas WHERE codigo_convite = ?", (candidato,)
                )
                if not cursor.fetchone():
                    codigo_convite = candidato
                    break
            if not codigo_convite:
                codigo_convite = f"DESP-{secrets.token_hex(4).upper()}"

        cursor.execute(
            """
            INSERT INTO despensas (nome, codigo_convite, dono_id)
            VALUES (?, ?, ?)
            """,
            (nome_limpo, codigo_convite, dono_id),
        )
        self.conn.commit()
        despensa_id = cursor.lastrowid
        return Despensa(
            id=despensa_id,
            nome=nome_limpo,
            codigo_convite=codigo_convite,
            dono_id=dono_id,
        )

    def definir_dono_despensa(self, despensa_id: int, dono_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE despensas SET dono_id = ? WHERE id = ?",
            (dono_id, despensa_id),
        )
        self.conn.commit()

    def buscar_despensa_por_id(self, despensa_id: int) -> Despensa | None:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, nome, codigo_convite, dono_id, criado_em FROM despensas WHERE id = ?",
            (despensa_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return Despensa(
            id=row["id"],
            nome=row["nome"],
            codigo_convite=row["codigo_convite"],
            dono_id=row["dono_id"],
            criado_em=row["criado_em"],
        )

    def buscar_despensa_por_codigo(self, codigo: str) -> Despensa | None:
        codigo_limpo = codigo.strip().upper() if codigo else ""
        if not codigo_limpo:
            return None
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, nome, codigo_convite, dono_id, criado_em FROM despensas WHERE codigo_convite = ?",
            (codigo_limpo,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return Despensa(
            id=row["id"],
            nome=row["nome"],
            codigo_convite=row["codigo_convite"],
            dono_id=row["dono_id"],
            criado_em=row["criado_em"],
        )

    def criar_usuario(
        self,
        despensa_id: int,
        nome: str,
        email: str,
        senha_hash: str = "",
        ativo: bool = True,
        google_id: str | None = None,
    ) -> Usuario:
        nome_limpo = nome.strip() if nome else ""
        email_limpo = email.strip().lower() if email else ""

        if not nome_limpo:
            raise ValueError("O nome do usuário não pode ser vazio.")
        if not email_limpo or "@" not in email_limpo:
            raise ValueError("E-mail inválido.")

        # Verifica se despensa existe
        if not self.buscar_despensa_por_id(despensa_id):
            raise ValueError(f"Despensa com ID {despensa_id} não encontrada.")

        # Verifica e-mail duplicado
        if self.buscar_usuario_por_email(email_limpo):
            raise ValueError(
                f"Já existe um usuário cadastrado com o e-mail '{email_limpo}'."
            )

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO usuarios (despensa_id, nome, email, senha_hash, ativo, google_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                despensa_id,
                nome_limpo,
                email_limpo,
                senha_hash,
                1 if ativo else 0,
                google_id,
            ),
        )
        self.conn.commit()
        usuario_id = cursor.lastrowid
        return Usuario(
            id=usuario_id,
            despensa_id=despensa_id,
            nome=nome_limpo,
            email=email_limpo,
            senha_hash=senha_hash,
            ativo=ativo,
            google_id=google_id,
        )

    def buscar_usuario_por_email(self, email: str) -> Usuario | None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, despensa_id, nome, email, senha_hash, ativo, google_id, criado_em
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
            ativo=bool(row["ativo"]),
            google_id=row["google_id"],
            criado_em=row["criado_em"],
        )

    def buscar_usuario_por_google_id(self, google_id: str) -> Usuario | None:
        if not google_id:
            return None
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, despensa_id, nome, email, senha_hash, ativo, google_id, criado_em
            FROM usuarios
            WHERE google_id = ?
            """,
            (google_id,),
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
            ativo=bool(row["ativo"]),
            google_id=row["google_id"],
            criado_em=row["criado_em"],
        )

    def buscar_usuario_por_id(self, usuario_id: int) -> Usuario | None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, despensa_id, nome, email, senha_hash, ativo, google_id, criado_em
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
            ativo=bool(row["ativo"]),
            google_id=row["google_id"],
            criado_em=row["criado_em"],
        )

    def ativar_usuario(self, usuario_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET ativo = 1 WHERE id = ?",
            (usuario_id,),
        )
        self.conn.commit()

    def vincular_google_id(self, usuario_id: int, google_id: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET google_id = ?, ativo = 1 WHERE id = ?",
            (google_id, usuario_id),
        )
        self.conn.commit()

    def atualizar_despensa_usuario(self, usuario_id: int, despensa_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET despensa_id = ? WHERE id = ?",
            (despensa_id, usuario_id),
        )
        self.conn.commit()

    def listar_usuarios_por_despensa(self, despensa_id: int) -> list[Usuario]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, despensa_id, nome, email, senha_hash, ativo, google_id, criado_em
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
                ativo=bool(row["ativo"]),
                google_id=row["google_id"],
                criado_em=row["criado_em"],
            )
            for row in rows
        ]

    # Códigos de Verificação (OTP)
    def salvar_codigo_verificacao(
        self,
        email: str,
        codigo: str,
        tipo: str = "cadastro",
        minutos_validade: int = 15,
    ) -> None:
        cursor = self.conn.cursor()
        email_limpo = email.strip().lower()

        # Invalida códigos anteriores não usados para este e-mail
        cursor.execute(
            "UPDATE codigos_verificacao SET usado = 1 WHERE email = ? AND tipo = ? AND usado = 0",
            (email_limpo, tipo),
        )

        expira_em = datetime.now() + timedelta(minutes=minutos_validade)
        cursor.execute(
            """
            INSERT INTO codigos_verificacao (email, codigo, tipo, expira_em, usado)
            VALUES (?, ?, ?, ?, 0)
            """,
            (email_limpo, codigo, tipo, expira_em.isoformat()),
        )
        self.conn.commit()

    def validar_codigo_verificacao(
        self, email: str, codigo: str, tipo: str = "cadastro"
    ) -> bool:
        cursor = self.conn.cursor()
        email_limpo = email.strip().lower()
        codigo_limpo = codigo.strip()

        cursor.execute(
            """
            SELECT id, codigo, expira_em, usado
            FROM codigos_verificacao
            WHERE email = ? AND tipo = ? AND usado = 0
            ORDER BY id DESC
            LIMIT 1
            """,
            (email_limpo, tipo),
        )
        row = cursor.fetchone()
        if not row:
            return False

        if row["codigo"] != codigo_limpo:
            return False

        expira_em_str = row["expira_em"]
        # Converte ISO string para datetime
        try:
            expira_em = datetime.fromisoformat(expira_em_str)
        except Exception:
            expira_em = datetime.now() - timedelta(seconds=1)

        if datetime.now() > expira_em:
            return False

        # Marca código como usado
        cursor.execute(
            "UPDATE codigos_verificacao SET usado = 1 WHERE id = ?",
            (row["id"],),
        )
        self.conn.commit()
        return True

    # Solicitações de Adesão à Despensa
    def criar_solicitacao_adesao(
        self, despensa_id: int, usuario_id: int
    ) -> SolicitacaoAdesao:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO solicitacoes_adesao (despensa_id, usuario_id, status)
            VALUES (?, ?, 'pendente')
            """,
            (despensa_id, usuario_id),
        )
        self.conn.commit()
        solicitacao_id = cursor.lastrowid
        return self.buscar_solicitacao_por_id(solicitacao_id)  # type: ignore

    def buscar_solicitacao_por_id(self, solicitacao_id: int) -> SolicitacaoAdesao | None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT s.id, s.despensa_id, s.usuario_id, s.status, s.criado_em, s.respondido_em,
                   u.nome as usuario_nome, u.email as usuario_email,
                   d.nome as despensa_nome
            FROM solicitacoes_adesao s
            JOIN usuarios u ON s.usuario_id = u.id
            JOIN despensas d ON s.despensa_id = d.id
            WHERE s.id = ?
            """,
            (solicitacao_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return SolicitacaoAdesao(
            id=row["id"],
            despensa_id=row["despensa_id"],
            usuario_id=row["usuario_id"],
            status=row["status"],
            criado_em=row["criado_em"],
            respondido_em=row["respondido_em"],
            usuario_nome=row["usuario_nome"],
            usuario_email=row["usuario_email"],
            despensa_nome=row["despensa_nome"],
        )

    def buscar_solicitacao_pendente(
        self, despensa_id: int, usuario_id: int
    ) -> SolicitacaoAdesao | None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT s.id, s.despensa_id, s.usuario_id, s.status, s.criado_em, s.respondido_em,
                   u.nome as usuario_nome, u.email as usuario_email,
                   d.nome as despensa_nome
            FROM solicitacoes_adesao s
            JOIN usuarios u ON s.usuario_id = u.id
            JOIN despensas d ON s.despensa_id = d.id
            WHERE s.despensa_id = ? AND s.usuario_id = ? AND s.status = 'pendente'
            ORDER BY s.id DESC LIMIT 1
            """,
            (despensa_id, usuario_id),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return SolicitacaoAdesao(
            id=row["id"],
            despensa_id=row["despensa_id"],
            usuario_id=row["usuario_id"],
            status=row["status"],
            criado_em=row["criado_em"],
            respondido_em=row["respondido_em"],
            usuario_nome=row["usuario_nome"],
            usuario_email=row["usuario_email"],
            despensa_nome=row["despensa_nome"],
        )

    def listar_solicitacoes_despensa(
        self, despensa_id: int, status: str = "pendente"
    ) -> list[SolicitacaoAdesao]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT s.id, s.despensa_id, s.usuario_id, s.status, s.criado_em, s.respondido_em,
                   u.nome as usuario_nome, u.email as usuario_email,
                   d.nome as despensa_nome
            FROM solicitacoes_adesao s
            JOIN usuarios u ON s.usuario_id = u.id
            JOIN despensas d ON s.despensa_id = d.id
            WHERE s.despensa_id = ? AND (? = 'todas' OR s.status = ?)
            ORDER BY s.id DESC
            """,
            (despensa_id, status, status),
        )
        rows = cursor.fetchall()
        return [
            SolicitacaoAdesao(
                id=row["id"],
                despensa_id=row["despensa_id"],
                usuario_id=row["usuario_id"],
                status=row["status"],
                criado_em=row["criado_em"],
                respondido_em=row["respondido_em"],
                usuario_nome=row["usuario_nome"],
                usuario_email=row["usuario_email"],
                despensa_nome=row["despensa_nome"],
            )
            for row in rows
        ]

    def listar_solicitacoes_usuario(
        self, usuario_id: int
    ) -> list[SolicitacaoAdesao]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT s.id, s.despensa_id, s.usuario_id, s.status, s.criado_em, s.respondido_em,
                   u.nome as usuario_nome, u.email as usuario_email,
                   d.nome as despensa_nome
            FROM solicitacoes_adesao s
            JOIN usuarios u ON s.usuario_id = u.id
            JOIN despensas d ON s.despensa_id = d.id
            WHERE s.usuario_id = ?
            ORDER BY s.id DESC
            """,
            (usuario_id,),
        )
        rows = cursor.fetchall()
        return [
            SolicitacaoAdesao(
                id=row["id"],
                despensa_id=row["despensa_id"],
                usuario_id=row["usuario_id"],
                status=row["status"],
                criado_em=row["criado_em"],
                respondido_em=row["respondido_em"],
                usuario_nome=row["usuario_nome"],
                usuario_email=row["usuario_email"],
                despensa_nome=row["despensa_nome"],
            )
            for row in rows
        ]

    def responder_solicitacao(self, solicitacao_id: int, novo_status: str) -> None:
        if novo_status not in ("aprovado", "recusado"):
            raise ValueError("Status deve ser 'aprovado' ou 'recusado'.")

        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE solicitacoes_adesao
            SET status = ?, respondido_em = ?
            WHERE id = ?
            """,
            (novo_status, datetime.now().isoformat(), solicitacao_id),
        )
        self.conn.commit()
