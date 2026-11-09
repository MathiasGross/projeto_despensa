import sqlite3
from fastapi import APIRouter, Depends, HTTPException, Response, status
from src.api.dependencies import get_current_user, get_db
from src.models.usuario import Usuario
from src.repositories.user_repository import UserRepository
from src.schemas.auth import (
    CadastroRespostaSchema,
    CadastroSchema,
    GoogleLoginSchema,
    LoginSchema,
    ReenviarCodigoSchema,
    TokenRespostaSchema,
    UsuarioRespostaSchema,
    VerificarCodigoSchema,
)
from src.security.crypto import gerar_hash_senha, verificar_senha
from src.security.tokens import criar_access_token
from src.services.email_service import enviar_email_codigo, gerar_codigo_otp
from src.services.google_auth_service import verificar_token_google

router = APIRouter(prefix="/auth", tags=["Autenticação"])


def _montar_resposta_token(
    usuario: Usuario,
    despensa_codigo: str | None,
    response: Response,
) -> dict:
    token = criar_access_token(
        {"sub": str(usuario.id), "despensa_id": usuario.despensa_id}
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 3600,
        path="/",
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "despensa_id": usuario.despensa_id,
            "nome": usuario.nome,
            "email": usuario.email,
            "ativo": usuario.ativo,
            "codigo_despensa": despensa_codigo,
            "criado_em": str(usuario.criado_em),
        },
    }


@router.post(
    "/cadastro",
    response_model=CadastroRespostaSchema,
    status_code=status.HTTP_201_CREATED,
)
def cadastro(
    dados: CadastroSchema,
    conn: sqlite3.Connection = Depends(get_db),
):
    user_repo = UserRepository(conn)
    email_limpo = dados.email.strip().lower()

    # 1. Verifica se já existe usuário
    existente = user_repo.buscar_usuario_por_email(email_limpo)
    if existente:
        if existente.ativo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe um usuário cadastrado com o e-mail '{email_limpo}'.",
            )
        # Se existe mas não está ativo, gera novo código e reenvia
        codigo = gerar_codigo_otp()
        user_repo.salvar_codigo_verificacao(email_limpo, codigo)
        enviar_email_codigo(email_limpo, existente.nome, codigo)
        return {
            "mensagem": "Cadastro já iniciado. Um novo código de verificação foi enviado para seu e-mail.",
            "email": email_limpo,
            "requer_verificacao": True,
            "codigo_dev": codigo,
        }

    # 2. Cria a despensa para o novo usuário
    despensa = user_repo.criar_despensa(dados.nome_despensa)

    # 3. Criptografa a senha com bcrypt
    senha_hash = gerar_hash_senha(dados.senha)

    # 4. Cria o usuário com ativo=False (pendente de validação do OTP)
    try:
        usuario = user_repo.criar_usuario(
            despensa_id=despensa.id,
            nome=dados.nome,
            email=email_limpo,
            senha_hash=senha_hash,
            ativo=False,
        )
        # Vincula como dono da despensa criada
        user_repo.definir_dono_despensa(despensa.id, usuario.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # 5. Gera e despacha código OTP de 6 dígitos
    codigo = gerar_codigo_otp()
    user_repo.salvar_codigo_verificacao(email_limpo, codigo)
    enviar_email_codigo(email_limpo, usuario.nome, codigo)

    return {
        "mensagem": "Código de verificação de 6 dígitos enviado para o seu e-mail.",
        "email": email_limpo,
        "requer_verificacao": True,
        "codigo_dev": codigo,
    }


@router.post("/verificar-codigo", response_model=TokenRespostaSchema)
def verificar_codigo(
    dados: VerificarCodigoSchema,
    response: Response,
    conn: sqlite3.Connection = Depends(get_db),
):
    user_repo = UserRepository(conn)
    email_limpo = dados.email.strip().lower()

    usuario = user_repo.buscar_usuario_por_email(email_limpo)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    valido = user_repo.validar_codigo_verificacao(email_limpo, dados.codigo)
    if not valido:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código de verificação inválido ou expirado. Verifique os números digitados.",
        )

    # Ativa usuário
    user_repo.ativar_usuario(usuario.id)
    usuario.ativo = True

    despensa = user_repo.buscar_despensa_por_id(usuario.despensa_id)
    codigo_despensa = despensa.codigo_convite if despensa else None

    return _montar_resposta_token(usuario, codigo_despensa, response)


@router.post("/reenviar-codigo")
def reenviar_codigo(
    dados: ReenviarCodigoSchema,
    conn: sqlite3.Connection = Depends(get_db),
):
    user_repo = UserRepository(conn)
    email_limpo = dados.email.strip().lower()

    usuario = user_repo.buscar_usuario_por_email(email_limpo)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma conta encontrada com este e-mail.",
        )

    if usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sua conta já foi verificada e está ativa. Você já pode fazer login.",
        )

    codigo = gerar_codigo_otp()
    user_repo.salvar_codigo_verificacao(email_limpo, codigo)
    enviar_email_codigo(email_limpo, usuario.nome, codigo)

    return {
        "mensagem": "Novo código de verificação enviado com sucesso para seu e-mail.",
        "codigo_dev": codigo,
    }


@router.post("/login", response_model=TokenRespostaSchema)
def login(
    dados: LoginSchema,
    response: Response,
    conn: sqlite3.Connection = Depends(get_db),
):
    user_repo = UserRepository(conn)
    usuario = user_repo.buscar_usuario_por_email(dados.email)

    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
        )

    if not usuario.ativo:
        # Reenvia código OTP automaticamente para facilitar o fluxo do usuário
        codigo = gerar_codigo_otp()
        user_repo.salvar_codigo_verificacao(usuario.email, codigo)
        enviar_email_codigo(usuario.email, usuario.nome, codigo)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta pendente de verificação. Enviamos um novo código para seu e-mail.",
        )

    despensa = user_repo.buscar_despensa_por_id(usuario.despensa_id)
    codigo_despensa = despensa.codigo_convite if despensa else None

    return _montar_resposta_token(usuario, codigo_despensa, response)


@router.post("/google", response_model=TokenRespostaSchema)
def login_google(
    dados: GoogleLoginSchema,
    response: Response,
    conn: sqlite3.Connection = Depends(get_db),
):
    try:
        dados_google = verificar_token_google(dados.id_token)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err),
        )

    email = dados_google["email"]
    nome = dados_google["name"]
    google_id = dados_google["sub"]

    user_repo = UserRepository(conn)
    usuario = user_repo.buscar_usuario_por_email(email)

    if usuario:
        # Usuário existente: ativa e vincula google_id se não estiver vinculado
        if not usuario.google_id:
            user_repo.vincular_google_id(usuario.id, google_id)
        if not usuario.ativo:
            user_repo.ativar_usuario(usuario.id)
            usuario.ativo = True
    else:
        # Novo usuário via Google: cria despensa e usuário já ativo!
        despensa = user_repo.criar_despensa(dados.nome_despensa)
        usuario = user_repo.criar_usuario(
            despensa_id=despensa.id,
            nome=nome,
            email=email,
            senha_hash="",
            ativo=True,
            google_id=google_id,
        )
        user_repo.definir_dono_despensa(despensa.id, usuario.id)

    despensa = user_repo.buscar_despensa_por_id(usuario.despensa_id)
    codigo_despensa = despensa.codigo_convite if despensa else None

    return _montar_resposta_token(usuario, codigo_despensa, response)


@router.get("/me", response_model=UsuarioRespostaSchema)
def me(
    usuario_atual: Usuario = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    user_repo = UserRepository(conn)
    despensa = user_repo.buscar_despensa_por_id(usuario_atual.despensa_id)
    codigo_despensa = despensa.codigo_convite if despensa else None

    return {
        "id": usuario_atual.id,
        "despensa_id": usuario_atual.despensa_id,
        "nome": usuario_atual.nome,
        "email": usuario_atual.email,
        "ativo": usuario_atual.ativo,
        "codigo_despensa": codigo_despensa,
        "criado_em": str(usuario_atual.criado_em),
    }
