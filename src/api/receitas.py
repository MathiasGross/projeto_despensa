from fastapi import APIRouter, Depends
from src.api.dependencies import get_current_user, get_item_service
from src.models.usuario import Usuario
from src.schemas.recipe import SugestaoReceitasResposta
from src.services.ai_recipe_service import AIRecipeService
from src.services.item_service import ItemService

router = APIRouter(prefix="/receitas", tags=["Chef IA (Receitas Inteligentes)"])


def get_ai_service() -> AIRecipeService:
    return AIRecipeService()


@router.post("/sugerir", response_model=SugestaoReceitasResposta)
def sugerir_receitas(
    usuario_atual: Usuario = Depends(get_current_user),
    item_service: ItemService = Depends(get_item_service),
    ai_service: AIRecipeService = Depends(get_ai_service),
):
    # 1. Busca os produtos da despensa do usuário autenticado
    todos_itens = item_service.listar_todos(despensa_id=usuario_atual.despensa_id)

    # 2. Filtra apenas os que possuem estoque disponível (quantidade > 0)
    itens_em_estoque = [item for item in todos_itens if item.quantidade > 0]

    if not itens_em_estoque:
        return {
            "receitas": [],
            "total_ingredientes_utilizados": 0,
            "mensagem": "Sua despensa não possui itens com estoque disponível no momento. Abasteça alguns produtos primeiro!",
        }

    # 3. Extrai apenas os nomes dos ingredientes
    nomes_ingredientes = [item.nome for item in itens_em_estoque]

    # 4. Gera receitas seguras via IA
    resposta = ai_service.gerar_receitas(nomes_ingredientes)
    return resposta
