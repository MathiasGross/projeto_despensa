import sqlite3
from fastapi import APIRouter, Depends, HTTPException, status
from src.api.dependencies import get_current_user, get_db
from src.models.usuario import Usuario
from src.repositories.user_repository import UserRepository
from src.schemas.despensa import (
    DespensaDetalhesSchema,
    MembroDespensaSchema,
    MensagemRespostaSchema,
    SolicitacaoAdesaoRespostaSchema,
    SolicitarEntradaSchema,
)

router = APIRouter(prefix="/despensas", tags=["Despensas & Compartilhamento"])


@router.get("/minha", response_model=DespensaDetalhesSchema)
def obter_minha_despensa(
    usuario_atual: Usuario = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    user_repo = UserRepository(conn)
    despensa = user_repo.buscar_despensa_por_id(usuario_atual.despensa_id)
    if not despensa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Despensa não encontrada.",
        )

    membros_db = user_repo.listar_usuarios_por_despensa(despensa.id)
    membros = [
        MembroDespensaSchema(
            id=m.id,
            nome=m.nome,
            email=m.email,
            e_dono=(m.id == despensa.dono_id),
        )
        for m in membros_db
    ]

    return {
        "id": despensa.id,
        "nome": despensa.nome,
        "codigo_convite": despensa.codigo_convite,
        "e_dono": (usuario_atual.id == despensa.dono_id),
        "membros": membros,
    }


@router.post("/solicitar-entrada", response_model=MensagemRespostaSchema)
def solicitar_entrada(
    dados: SolicitarEntradaSchema,
    usuario_atual: Usuario = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    user_repo = UserRepository(conn)
    codigo_limpo = dados.codigo_convite.strip().upper()

    despensa_alvo = user_repo.buscar_despensa_por_codigo(codigo_limpo)
    if not despensa_alvo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Código de despensa não encontrado. Verifique o código digitado com o criador da despensa.",
        )

    if despensa_alvo.id == usuario_atual.despensa_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você já faz parte desta despensa.",
        )

    solicitacao_existente = user_repo.buscar_solicitacao_pendente(
        despensa_id=despensa_alvo.id,
        usuario_id=usuario_atual.id,
    )
    if solicitacao_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Você já possui uma solicitação pendente para a despensa '{despensa_alvo.nome}'. Aguarde a aprovação do proprietário.",
        )

    user_repo.criar_solicitacao_adesao(
        despensa_id=despensa_alvo.id,
        usuario_id=usuario_atual.id,
    )

    return {
        "mensagem": f"Solicitação enviada para a despensa '{despensa_alvo.nome}'! O criador da despensa precisará confirmar sua entrada.",
        "sucesso": True,
    }


@router.get(
    "/solicitacoes",
    response_model=list[SolicitacaoAdesaoRespostaSchema],
)
def listar_solicitacoes_pendentes(
    usuario_atual: Usuario = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    """Lista as solicitações de novos membros que desejam entrar na despensa do usuário atual."""
    user_repo = UserRepository(conn)
    solicitacoes = user_repo.listar_solicitacoes_despensa(
        despensa_id=usuario_atual.despensa_id,
        status="pendente",
    )
    return [
        {
            "id": s.id,
            "despensa_id": s.despensa_id,
            "usuario_id": s.usuario_id,
            "usuario_nome": s.usuario_nome,
            "usuario_email": s.usuario_email,
            "despensa_nome": s.despensa_nome,
            "status": s.status,
            "criado_em": str(s.criado_em),
            "respondido_em": str(s.respondido_em) if s.respondido_em else None,
        }
        for s in solicitacoes
    ]


@router.post(
    "/solicitacoes/{solicitacao_id}/aprovar",
    response_model=MensagemRespostaSchema,
)
def aprovar_solicitacao(
    solicitacao_id: int,
    usuario_atual: Usuario = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    user_repo = UserRepository(conn)
    solicitacao = user_repo.buscar_solicitacao_por_id(solicitacao_id)

    if not solicitacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada.",
        )

    # Apenas membros da despensa dona podem aprovar
    if solicitacao.despensa_id != usuario_atual.despensa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para aprovar solicitações desta despensa.",
        )

    if solicitacao.status != "pendente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Esta solicitação já foi respondida com status '{solicitacao.status}'.",
        )

    # 1. Atualiza status da solicitação
    user_repo.responder_solicitacao(solicitacao_id, "aprovado")

    # 2. Migra o usuário solicitante para a despensa aprovada
    user_repo.atualizar_despensa_usuario(
        usuario_id=solicitacao.usuario_id,
        despensa_id=solicitacao.despensa_id,
    )

    return {
        "mensagem": f"Solicitação de {solicitacao.usuario_nome or 'usuário'} aprovada com sucesso! O novo membro já tem acesso aos itens da despensa.",
        "sucesso": True,
    }


@router.post(
    "/solicitacoes/{solicitacao_id}/recusar",
    response_model=MensagemRespostaSchema,
)
def recusar_solicitacao(
    solicitacao_id: int,
    usuario_atual: Usuario = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    user_repo = UserRepository(conn)
    solicitacao = user_repo.buscar_solicitacao_por_id(solicitacao_id)

    if not solicitacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitação não encontrada.",
        )

    if solicitacao.despensa_id != usuario_atual.despensa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para recusar solicitações desta despensa.",
        )

    if solicitacao.status != "pendente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Esta solicitação já foi respondida com status '{solicitacao.status}'.",
        )

    user_repo.responder_solicitacao(solicitacao_id, "recusado")

    return {
        "mensagem": "Solicitação recusada. O usuário não teve acesso liberado à despensa.",
        "sucesso": True,
    }


@router.get(
    "/minhas-solicitacoes",
    response_model=list[SolicitacaoAdesaoRespostaSchema],
)
def listar_minhas_solicitacoes(
    usuario_atual: Usuario = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    """Lista as solicitações que o próprio usuário enviou para outras despensas."""
    user_repo = UserRepository(conn)
    solicitacoes = user_repo.listar_solicitacoes_usuario(usuario_atual.id)
    return [
        {
            "id": s.id,
            "despensa_id": s.despensa_id,
            "usuario_id": s.usuario_id,
            "usuario_nome": s.usuario_nome,
            "usuario_email": s.usuario_email,
            "despensa_nome": s.despensa_nome,
            "status": s.status,
            "criado_em": str(s.criado_em),
            "respondido_em": str(s.respondido_em) if s.respondido_em else None,
        }
        for s in solicitacoes
    ]
