import sqlite3
from fastapi import APIRouter, Depends, HTTPException, Response, status
from src.api.dependencies import get_current_user, get_db
from src.models.usuario import Usuario
from src.repositories.user_repository import UserRepository
from src.schemas.auth import CadastroSchema, LoginSchema, TokenRespostaSchema, UsuarioRespostaSchema
from src.security.crypto import gerar_hash_senha, verificar_senha
from src.security.tokens import criar_access_token

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/cadastro", response_model=TokenRespostaSchema, status_code=status.HTTP_201_CREATED)
def cadastro(dados: CadastroSchema, response: Response, conn: sqlite3.Connection = Depends(get_db)):
    user_repo = UserRepository(conn)

    # 1. Cria a despensa para o novo usuário
    despensa = user_repo.criar_despensa(dados.nome_despensa)

    # 2. Criptografa a senha com bcrypt
    senha_hash = gerar_hash_senha(dados.senha)

    # 3. Cria o usuário vinculado à despensa
    try:
        usuario = user_repo.criar_usuario(
            despensa_id=despensa.id,
            nome=dados.nome,
            email=dados.email,
            senha_hash=senha_hash,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # 4. Gera o token JWT
    token = criar_access_token({"sub": str(usuario.id), "despensa_id": usuario.despensa_id})

    # 5. Define cookie seguro para navegadores
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # Em produção com HTTPS, mudar para True
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
            "criado_em": usuario.criado_em,
        },
    }


@router.post("/login", response_model=TokenRespostaSchema)
def login(dados: LoginSchema, response: Response, conn: sqlite3.Connection = Depends(get_db)):
    user_repo = UserRepository(conn)
    usuario = user_repo.buscar_usuario_por_email(dados.email)

    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
        )

    token = criar_access_token({"sub": str(usuario.id), "despensa_id": usuario.despensa_id})

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
            "criado_em": usuario.criado_em,
        },
    }


@router.get("/me", response_model=UsuarioRespostaSchema)
def me(usuario_atual: Usuario = Depends(get_current_user)):
    return {
        "id": usuario_atual.id,
        "despensa_id": usuario_atual.despensa_id,
        "nome": usuario_atual.nome,
        "email": usuario_atual.email,
        "criado_em": usuario_atual.criado_em,
    }
