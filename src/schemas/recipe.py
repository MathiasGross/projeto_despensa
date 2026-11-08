from pydantic import BaseModel, ConfigDict, Field


class IngredienteReceita(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nome: str = Field(..., description="Nome do ingrediente")
    quantidade_estimada: str = Field(..., description="Quantidade estimada (ex: 2 xícaras, 1 colher)")
    disponivel_em_casa: bool = Field(
        default=True,
        description="Se o ingrediente já consta no estoque da despensa",
    )


class Receita(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    titulo: str = Field(..., description="Título atrativo da receita")
    tempo_minutos: int = Field(..., description="Tempo estimado de preparo em minutos")
    porcoes: int = Field(default=2, description="Número aproximado de porções que a receita rende")
    dificuldade: str = Field(default="Fácil", description="Fácil, Média ou Difícil")
    descricao: str = Field(..., description="Breve resumo sobre o prato")
    ingredientes: list[IngredienteReceita] = Field(..., description="Lista de ingredientes necessários")
    passo_a_passo: list[str] = Field(..., description="Instruções claras e ordenadas de preparo")


class SugestaoReceitasResposta(BaseModel):
    receitas: list[Receita]
    total_ingredientes_utilizados: int
    mensagem: str
