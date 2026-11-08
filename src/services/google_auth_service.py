import logging
import os
from google.auth.transport import requests
from google.oauth2 import id_token

logger = logging.getLogger("google_auth")


def verificar_token_google(token: str) -> dict:
    """
    Verifica a autenticidade de um ID Token emitido pelo Google Identity Services / OAuth2.
    Retorna o dicionário com os dados do usuário (email, name, sub/google_id, picture).

    Para testes ou ambiente sem internet/chaves reais configuradas, suporta tokens de desenvolvimento:
    'mock-google-token:email@exemplo.com:Nome Completo:google-id-123'
    """
    token_limpo = token.strip() if token else ""
    if not token_limpo:
        raise ValueError("Token do Google ausente ou vazio.")

    # Suporte para testes e ambiente de desenvolvimento simulado
    if token_limpo.startswith("mock-google-token"):
        partes = token_limpo.split(":")
        email = partes[1] if len(partes) > 1 else "google_user@exemplo.com"
        nome = partes[2] if len(partes) > 2 else "Usuário Google Teste"
        sub = partes[3] if len(partes) > 3 else "mock-google-sub-999"
        return {
            "email": email.lower(),
            "name": nome,
            "sub": sub,
            "picture": None,
        }

    client_id = os.getenv("GOOGLE_CLIENT_ID")

    try:
        # Verifica a assinatura criptográfica com os certificados públicos do Google
        request = requests.Request()
        idinfo = id_token.verify_oauth2_token(
            token_limpo,
            request,
            audience=client_id if client_id else None,
        )

        email = idinfo.get("email")
        if not email:
            raise ValueError("O token do Google não contém um endereço de e-mail.")

        return {
            "email": email.lower(),
            "name": idinfo.get("name", "Usuário Google"),
            "sub": idinfo.get("sub"),
            "picture": idinfo.get("picture"),
        }
    except Exception as exc:
        logger.error(f"Falha na validação do token Google: {exc}")
        raise ValueError(f"Token do Google inválido ou expirado: {exc}")
