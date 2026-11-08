from pydantic import BaseModel, ConfigDict, Field


class ItemCriacaoSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nome: str = Field(..., min_length=1, max_length=100)
    quantidade: int = Field(default=0, ge=0)
    quantidade_minima: int = Field(default=1, ge=0)
    local: str = Field(default="", max_length=100)
    obs: str = Field(default="", max_length=255)


class MovimentacaoEstoqueSchema(BaseModel):
    quantidade: int = Field(..., gt=0, description="Quantidade a ser movimentada (deve ser maior que 0)")


class ItemRespostaSchema(BaseModel):
    id: int
    despensa_id: int
    nome: str
    quantidade: int
    quantidade_minima: int
    local: str
    obs: str


class ItemCompraSchema(BaseModel):
    item_id: int
    nome: str
    quantidade_atual: int
    quantidade_minima: int
    quantidade_sugerida: int
    local: str
    obs: str


class ListaComprasRespostaSchema(BaseModel):
    itens: list[ItemCompraSchema]
    total_itens: int
    texto_whatsapp: str


class AlertasRespostaSchema(BaseModel):
    zerados: list[ItemRespostaSchema]
    acabando: list[ItemRespostaSchema]
    total_alertas: int
