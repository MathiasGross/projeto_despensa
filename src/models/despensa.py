from datetime import datetime


class Despensa:
    def __init__(self, id: int, nome: str, criado_em: datetime | str | None = None):
        self.id = id
        self.nome = nome
        self.criado_em = criado_em or datetime.now().isoformat()

    def __repr__(self):
        return f"Despensa(id={self.id}, nome='{self.nome}')"
