from src.api.auth import router as auth_router
from src.api.compras import router as compras_router
from src.api.itens import router as itens_router
from src.api.receitas import router as receitas_router

__all__ = ["auth_router", "itens_router", "compras_router", "receitas_router"]
