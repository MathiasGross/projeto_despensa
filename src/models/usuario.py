from datetime import datetime


class Usuario:
    def __init__(
        self,
        id: int,
        despensa_id: int,
        nome: str,
        email: str,
        senha_hash: str,
        criado_em: datetime | str | None = None,
    ):
        self.id = id
        self.despensa_id = despensa_id
        self.nome = nome
        self.email = email
        self.senha_hash = senha_hash
        self.criado_em = criado_em or datetime.now().isoformat()

    def __repr__(self):
        return f"Usuario(id={self.id}, email='{self.email}', despensa_id={self.despensa_id})"
