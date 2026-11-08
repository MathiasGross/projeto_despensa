from datetime import datetime


class Despensa:
    def __init__(
        self,
        id: int,
        nome: str,
        codigo_convite: str | None = None,
        dono_id: int | None = None,
        criado_em: datetime | str | None = None,
    ):
        self.id = id
        self.nome = nome
        self.codigo_convite = codigo_convite
        self.dono_id = dono_id
        self.criado_em = criado_em or datetime.now().isoformat()

    def __repr__(self):
        return f"Despensa(id={self.id}, nome='{self.nome}', codigo='{self.codigo_convite}')"
