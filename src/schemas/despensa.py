from pydantic import BaseModel, ConfigDict, Field


class SolicitarEntradaSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    codigo_convite: str = Field(..., min_length=4, max_length=30)


class MembroDespensaSchema(BaseModel):
    id: int
    nome: str
    email: str
    e_dono: bool = False


class DespensaDetalhesSchema(BaseModel):
    id: int
    nome: str
    codigo_convite: str | None = None
    e_dono: bool = False
    membros: list[MembroDespensaSchema] = []


class SolicitacaoAdesaoRespostaSchema(BaseModel):
    id: int
    despensa_id: int
    usuario_id: int
    usuario_nome: str | None = None
    usuario_email: str | None = None
    despensa_nome: str | None = None
    status: str
    criado_em: str | None = None
    respondido_em: str | None = None


class MensagemRespostaSchema(BaseModel):
    mensagem: str
    sucesso: bool = True
