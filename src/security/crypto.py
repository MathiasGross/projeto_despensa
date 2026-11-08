import bcrypt


def gerar_hash_senha(senha: str) -> str:
    """Gera hash seguro com bcrypt e cost factor (rounds) = 12."""
    senha_bytes = senha.encode("utf-8")
    sal = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(senha_bytes, sal).decode("utf-8")


def verificar_senha(senha_plana: str, senha_hasheada: str) -> bool:
    """Valida a senha contra o hash de forma resistente a timing attacks."""
    try:
        return bcrypt.checkpw(
            senha_plana.encode("utf-8"),
            senha_hasheada.encode("utf-8"),
        )
    except Exception:
        return False
