from fastapi import APIRouter, Depends
from src.api.dependencies import get_current_user, get_item_service
from src.models.usuario import Usuario
from src.schemas.item import AlertasRespostaSchema, ListaComprasRespostaSchema
from src.services.item_service import ItemService

router = APIRouter(tags=["Lista de Compras e Alertas"])


@router.get("/compras", response_model=ListaComprasRespostaSchema)
def obter_lista_compras(
    usuario_atual: Usuario = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    itens = service.gerar_lista_compras(despensa_id=usuario_atual.despensa_id)
    texto = service.formatar_lista_compras_texto(
        itens_compras=itens, despensa_id=usuario_atual.despensa_id
    )

    return {
        "itens": itens,
        "total_itens": len(itens),
        "texto_whatsapp": texto,
    }


@router.get("/alertas", response_model=AlertasRespostaSchema)
def obter_alertas(
    usuario_atual: Usuario = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    alertas = service.obter_alertas(despensa_id=usuario_atual.despensa_id)

    def to_dict(item):
        return {
            "id": item.id,
            "despensa_id": item.despensa_id,
            "nome": item.nome,
            "quantidade": item.quantidade,
            "quantidade_minima": item.quantidade_minima,
            "local": item.local,
            "obs": item.obs,
        }

    return {
        "zerados": [to_dict(i) for i in alertas["zerados"]],
        "acabando": [to_dict(i) for i in alertas["acabando"]],
        "total_alertas": alertas["total_alertas"],
    }
