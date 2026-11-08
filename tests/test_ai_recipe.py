import os
import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from src.api.dependencies import configurar_db_path
from src.database.connection import get_connection, init_db
from src.main import app
from src.schemas.recipe import Receita
from src.services.ai_recipe_service import AIRecipeService

TEST_DB = "test_despensa_ai.db"


class TestAIRecipeService(unittest.TestCase):
    def test_gerar_receitas_sem_ingredientes(self):
        service = AIRecipeService(api_key="chave_ficticia")
        resposta = service.gerar_receitas([])
        self.assertEqual(len(resposta.receitas), 0)
        self.assertEqual(resposta.total_ingredientes_utilizados, 0)
        self.assertIn("Nenhum ingrediente", resposta.mensagem)

    def test_gerar_receitas_fallback_sem_api_key(self):
        service = AIRecipeService(api_key=None)
        resposta = service.gerar_receitas(["Arroz", "Feijão", "Ovo"])
        self.assertEqual(len(resposta.receitas), 1)
        self.assertEqual(resposta.total_ingredientes_utilizados, 3)
        self.assertIn("Refogado Prático", resposta.receitas[0].titulo)
        self.assertIn("assistente local", resposta.mensagem)

    @patch("google.genai.Client")
    def test_gerar_receitas_com_gemini_sucesso(self, mock_client_class):
        # Mock do retorno da API do Gemini
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.text = """
        [
            {
                "titulo": "Omelete de Arroz com Tomate",
                "tempo_minutos": 15,
                "porcoes": 1,
                "dificuldade": "Fácil",
                "descricao": "Uma deliciosa omelete aproveitando sobra de arroz e tomates frescos.",
                "ingredientes": [
                    {"nome": "Ovo", "quantidade_estimada": "2 unidades", "disponivel_em_casa": true},
                    {"nome": "Arroz", "quantidade_estimada": "1/2 xícara", "disponivel_em_casa": true},
                    {"nome": "Tomate", "quantidade_estimada": "1 unidade", "disponivel_em_casa": true}
                ],
                "passo_a_passo": [
                    "Bata os ovos em uma tigela.",
                    "Adicione o arroz e o tomate picado.",
                    "Despeje na frigideira quente e doure dos dois lados."
                ]
            }
        ]
        """
        mock_client.models.generate_content.return_value = mock_response

        service = AIRecipeService(api_key="chave_valida_teste")
        resposta = service.gerar_receitas(["Arroz", "Ovo", "Tomate"])

        self.assertEqual(len(resposta.receitas), 1)
        receita = resposta.receitas[0]
        self.assertEqual(receita.titulo, "Omelete de Arroz com Tomate")
        self.assertEqual(receita.tempo_minutos, 15)
        self.assertEqual(len(receita.ingredientes), 3)
        self.assertIn("Chef IA Gemini", resposta.mensagem)

    @patch("google.genai.Client")
    def test_gerar_receitas_erro_gemini_ativa_fallback(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("Quota exceeded")

        service = AIRecipeService(api_key="chave_valida_teste")
        resposta = service.gerar_receitas(["Macarrão", "Molho de Tomate"])

        # Não deve quebrar; ativa o fallback
        self.assertEqual(len(resposta.receitas), 1)
        self.assertIn("contingência", resposta.mensagem)


class TestReceitasEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configurar_db_path(TEST_DB)

    def setUp(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        conn = get_connection(TEST_DB)
        init_db(conn)
        conn.close()

        self.client = TestClient(app)

    def tearDown(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_endpoint_sem_autenticacao(self):
        resp = self.client.post("/receitas/sugerir")
        self.assertEqual(resp.status_code, 401)

    def test_endpoint_despensa_vazia(self):
        # Cadastro e login
        cad_resp = self.client.post(
            "/auth/cadastro",
            json={
                "nome": "User Sem Estoque",
                "email": "vazio@teste.com",
                "senha": "senhaValida123!",
                "nome_despensa": "Despensa Vazia",
            },
        )
        token = cad_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = self.client.post("/receitas/sugerir", headers=headers)
        self.assertEqual(resp.status_code, 200)
        dados = resp.json()
        self.assertEqual(len(dados["receitas"]), 0)
        self.assertIn("não possui itens com estoque disponível", dados["mensagem"])

    def test_endpoint_com_itens_em_estoque(self):
        # Cadastro e login
        cad_resp = self.client.post(
            "/auth/cadastro",
            json={
                "nome": "Chef User",
                "email": "chef@teste.com",
                "senha": "senhaValida123!",
                "nome_despensa": "Minha Cozinha",
            },
        )
        token = cad_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Cadastra 2 itens em estoque (> 0) e 1 zerado (== 0)
        self.client.post(
            "/itens",
            json={"nome": "Batata", "quantidade": 4, "quantidade_minima": 2, "local": "Fruteira"},
            headers=headers,
        )
        self.client.post(
            "/itens",
            json={"nome": "Cenoura", "quantidade": 2, "quantidade_minima": 1, "local": "Geladeira"},
            headers=headers,
        )
        self.client.post(
            "/itens",
            json={"nome": "Carne", "quantidade": 0, "quantidade_minima": 1, "local": "Freezer"},
            headers=headers,
        )

        resp = self.client.post("/receitas/sugerir", headers=headers)
        self.assertEqual(resp.status_code, 200)
        dados = resp.json()
        self.assertGreater(len(dados["receitas"]), 0)
        self.assertEqual(dados["total_ingredientes_utilizados"], 2)  # Apenas Batata e Cenoura (Carne está zerada)


if __name__ == "__main__":
    unittest.main()
