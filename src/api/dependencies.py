import sqlite3
from typing import Generator
from fastapi import Cookie, Depends, Header, HTTPException, status
from src.database.connection import get_connection, init_db
from src.models.usuario import Usuario
from src.repositories.sqlite_item_repository import SqliteItemRepository
from src.repositories.user_repository import UserRepository
from src.security.tokens import decodificar_access_token
from src.services.item_service import ItemService

# Inicialização do banco
_DB_PATH = "despensa.db"


def configurar_db_path(path: str) -> None:
    global _DB_PATH
    _DB_PATH = path


def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = get_connection(_DB_PATH)
    init_db(conn)
    try:
        yield conn
    finally:
        conn.close()


def get_current_user(
    authorization: str | None = Header(default=None),
    access_token_cookie: str | None = Cookie(default=None, alias="access_token"),
    conn: sqlite3.Connection = Depends(get_db),
) -> Usuario:
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    elif access_token_cookie:
        token = access_token_cookie

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação necessária. Token ausente.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decodificar_access_token(token)
        usuario_id = int(payload["sub"])
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepository(conn)
    usuario = user_repo.buscar_usuario_por_id(usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado.",
        )

    return usuario


def get_item_service(conn: sqlite3.Connection = Depends(get_db)) -> ItemService:
    repo = SqliteItemRepository(conn)
    return ItemService(repo)
