from datetime import datetime


class SolicitacaoAdesao:
    def __init__(
        self,
        id: int,
        despensa_id: int,
        usuario_id: int,
        status: str = "pendente",
        criado_em: datetime | str | None = None,
        respondido_em: datetime | str | None = None,
        usuario_nome: str | None = None,
        usuario_email: str | None = None,
        despensa_nome: str | None = None,
    ):
        self.id = id
        self.despensa_id = despensa_id
        self.usuario_id = usuario_id
        self.status = status
        self.criado_em = criado_em or datetime.now().isoformat()
        self.respondido_em = respondido_em
        self.usuario_nome = usuario_nome
        self.usuario_email = usuario_email
        self.despensa_nome = despensa_nome

    def __repr__(self):
        return f"SolicitacaoAdesao(id={self.id}, despensa_id={self.despensa_id}, usuario_id={self.usuario_id}, status='{self.status}')"
