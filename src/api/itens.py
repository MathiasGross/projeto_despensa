from fastapi import APIRouter, Depends, HTTPException, status
from src.api.dependencies import get_current_user, get_item_service
from src.models.usuario import Usuario
from src.schemas.item import (
    ItemCriacaoSchema,
    ItemRespostaSchema,
    MovimentacaoEstoqueSchema,
)
from src.services.item_service import ItemService

router = APIRouter(prefix="/itens", tags=["Inventário e Estoque"])


@router.get("", response_model=list[ItemRespostaSchema])
def listar_itens(
    usuario_atual: Usuario = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    itens = service.listar_todos(despensa_id=usuario_atual.despensa_id)
    return [
        {
            "id": i.id,
            "despensa_id": i.despensa_id,
            "nome": i.nome,
            "quantidade": i.quantidade,
            "quantidade_minima": i.quantidade_minima,
            "local": i.local,
            "obs": i.obs,
        }
        for i in itens
    ]


@router.post("", response_model=ItemRespostaSchema, status_code=status.HTTP_201_CREATED)
def cadastrar_item(
    dados: ItemCriacaoSchema,
    usuario_atual: Usuario = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    try:
        item = service.cadastrar_item(
            nome=dados.nome,
            quantidade=dados.quantidade,
            local=dados.local,
            quantidade_minima=dados.quantidade_minima,
            obs=dados.obs,
            despensa_id=usuario_atual.despensa_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {
        "id": item.id,
        "despensa_id": item.despensa_id,
        "nome": item.nome,
        "quantidade": item.quantidade,
        "quantidade_minima": item.quantidade_minima,
        "local": item.local,
        "obs": item.obs,
    }


@router.get("/{item_id}", response_model=ItemRespostaSchema)
def buscar_item(
    item_id: int,
    usuario_atual: Usuario = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    try:
        item = service.buscar_por_id(item_id, despensa_id=usuario_atual.despensa_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return {
        "id": item.id,
        "despensa_id": item.despensa_id,
        "nome": item.nome,
        "quantidade": item.quantidade,
        "quantidade_minima": item.quantidade_minima,
        "local": item.local,
        "obs": item.obs,
    }


@router.patch("/{item_id}/adicionar", response_model=ItemRespostaSchema)
def adicionar_quantidade(
    item_id: int,
    dados: MovimentacaoEstoqueSchema,
    usuario_atual: Usuario = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    try:
        item = service.adicionar_estoque(
            item_id, dados.quantidade, despensa_id=usuario_atual.despensa_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {
        "id": item.id,
        "despensa_id": item.despensa_id,
        "nome": item.nome,
        "quantidade": item.quantidade,
        "quantidade_minima": item.quantidade_minima,
        "local": item.local,
        "obs": item.obs,
    }


@router.patch("/{item_id}/remover", response_model=ItemRespostaSchema)
def remover_quantidade(
    item_id: int,
    dados: MovimentacaoEstoqueSchema,
    usuario_atual: Usuario = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    try:
        item = service.remover_estoque(
            item_id, dados.quantidade, despensa_id=usuario_atual.despensa_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {
        "id": item.id,
        "despensa_id": item.despensa_id,
        "nome": item.nome,
        "quantidade": item.quantidade,
        "quantidade_minima": item.quantidade_minima,
        "local": item.local,
        "obs": item.obs,
    }


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_item(
    item_id: int,
    usuario_atual: Usuario = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    try:
        service.deletar_item(item_id, despensa_id=usuario_atual.despensa_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
