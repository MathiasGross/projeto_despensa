from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CadastroSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nome: str = Field(..., min_length=2, max_length=100)
    email: EmailStr = Field(..., max_length=255)
    senha: str = Field(..., min_length=6, max_length=128)
    nome_despensa: str = Field(default="Nossa Despensa", min_length=2, max_length=100)


class CadastroRespostaSchema(BaseModel):
    mensagem: str
    email: str
    requer_verificacao: bool = True
    codigo_dev: str | None = None


class VerificarCodigoSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    codigo: str = Field(..., min_length=4, max_length=10)


class ReenviarCodigoSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr


class GoogleLoginSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id_token: str = Field(..., min_length=10)
    nome_despensa: str = Field(default="Nossa Despensa", min_length=2, max_length=100)


class LoginSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    senha: str = Field(..., min_length=1)


class UsuarioRespostaSchema(BaseModel):
    id: int
    despensa_id: int
    nome: str
    email: str
    ativo: bool = True
    codigo_despensa: str | None = None
    criado_em: str | None = None


class TokenRespostaSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioRespostaSchema
