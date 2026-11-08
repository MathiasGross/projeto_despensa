import os
from datetime import datetime, timedelta, timezone
from typing import Any
import jwt

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "despensa_secret_key_super_segura_para_desenvolvimento_123456789")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 dias de sessão


def criar_access_token(dados: dict[str, Any], expira_minutos: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    payload = dados.copy()
    agora = datetime.now(timezone.utc)
    expiracao = agora + timedelta(minutes=expira_minutos)
    payload.update({
        "exp": expiracao,
        "iat": agora,
        "nbf": agora,
    })
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decodificar_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "iat", "sub"]},
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expirado.")
    except jwt.PyJWTError as e:
        raise ValueError(f"Token inválido: {str(e)}")
