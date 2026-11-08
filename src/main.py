from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.auth import router as auth_router
from src.api.compras import router as compras_router
from src.api.itens import router as itens_router
from src.database.connection import get_connection, init_db

ENV = os.getenv("ENVIRONMENT", "development").lower()
IS_PROD = ENV == "production"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa banco SQLite na inicialização
    conn = get_connection("despensa.db")
    init_db(conn)
    conn.close()
    yield


app = FastAPI(
    title="Despensa Doméstica Inteligente API",
    description="API para controle de despensa doméstica, estoque compartilhado e lista de compras inteligente.",
    version="1.0.0",
    docs_url=None if IS_PROD else "/docs",
    redoc_url=None if IS_PROD else "/redoc",
    openapi_url=None if IS_PROD else "/openapi.json",
    lifespan=lifespan,
)

# Configuração de CORS para permitir acesso do app mobile (Expo) e browsers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção estrita, restrinja para os domínios do app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão das rotas
app.include_router(auth_router)
app.include_router(itens_router)
app.include_router(compras_router)


@app.get("/", tags=["Status"])
def root():
    return {
        "status": "online",
        "sistema": "Despensa Doméstica Inteligente API",
        "versao": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
