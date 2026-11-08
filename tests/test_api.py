import os
import unittest
from fastapi.testclient import TestClient
from src.api.dependencies import configurar_db_path
from src.database.connection import get_connection, init_db
from src.main import app
from src.services.email_service import ULTIMOS_CODIGOS_DEV

TEST_DB = "test_despensa_api.db"


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configurar_db_path(TEST_DB)

    def setUp(self):
        # Reinicia o banco de testes antes de cada caso de teste
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        conn = get_connection(TEST_DB)
        init_db(conn)
        conn.close()

        self.client = TestClient(app)

    def tearDown(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def _cadastrar_e_obter_token(
        self,
        nome: str = "Mathias",
        email: str = "mathias@exemplo.com",
        senha: str = "senhaSegura123!",
        nome_despensa: str = "Casa",
    ) -> str:
        # 1. Cadastro inicial
        self.client.post(
            "/auth/cadastro",
            json={
                "nome": nome,
                "email": email,
                "senha": senha,
                "nome_despensa": nome_despensa,
            },
        )
        # 2. Obter código gerado
        codigo = ULTIMOS_CODIGOS_DEV[email.lower()]
        # 3. Validar código e obter token
        resp_val = self.client.post(
            "/auth/verificar-codigo",
            json={"email": email, "codigo": codigo},
        )
        return resp_val.json()["access_token"]

    def test_status_root(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "online")

    def test_cadastro_e_login_sucesso(self):
        # 1. Cadastro envia OTP
        dados_cadastro = {
            "nome": "Mathias",
            "email": "mathias@exemplo.com",
            "senha": "senhaSegura123!",
            "nome_despensa": "Casa Mathias",
        }
        resp = self.client.post("/auth/cadastro", json=dados_cadastro)
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertTrue(data["requer_verificacao"])
        self.assertEqual(data["email"], "mathias@exemplo.com")

        # 2. Tentativa de login antes de verificar o código deve falhar (403)
        resp_login_inativo = self.client.post(
            "/auth/login",
            json={"email": "mathias@exemplo.com", "senha": "senhaSegura123!"},
        )
        self.assertEqual(resp_login_inativo.status_code, 403)

        # 3. Verificação do código OTP
        codigo = ULTIMOS_CODIGOS_DEV["mathias@exemplo.com"]
        resp_val = self.client.post(
            "/auth/verificar-codigo",
            json={"email": "mathias@exemplo.com", "codigo": codigo},
        )
        self.assertEqual(resp_val.status_code, 200)
        dados_val = resp_val.json()
        self.assertIn("access_token", dados_val)
        self.assertEqual(dados_val["usuario"]["nome"], "Mathias")
        self.assertTrue(dados_val["usuario"]["ativo"])
        self.assertIsNotNone(dados_val["usuario"]["codigo_despensa"])

        # 4. Login após validação tem sucesso
        dados_login = {
            "email": "mathias@exemplo.com",
            "senha": "senhaSegura123!",
        }
        resp_login = self.client.post("/auth/login", json=dados_login)
        self.assertEqual(resp_login.status_code, 200)
        self.assertIn("access_token", resp_login.json())

    def test_login_senha_incorreta(self):
        self._cadastrar_e_obter_token(email="user@exemplo.com", senha="senhaValida123!")
        resp = self.client.post(
            "/auth/login",
            json={"email": "user@exemplo.com", "senha": "senhaErrada"},
        )
        self.assertEqual(resp.status_code, 401)

    def test_rotas_protegidas_sem_token(self):
        resp = self.client.get("/itens")
        self.assertEqual(resp.status_code, 401)

        resp_compras = self.client.get("/compras")
        self.assertEqual(resp_compras.status_code, 401)

    def test_crud_itens_e_movimentacao_estoque(self):
        # Cadastro e obtenção do token validado via OTP
        token = self._cadastrar_e_obter_token(email="m@exemplo.com")
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Cadastrar item
        item_data = {
            "nome": "Arroz",
            "quantidade": 2,
            "quantidade_minima": 3,
            "local": "Armário",
            "obs": "Tipo 1",
        }
        resp_item = self.client.post("/itens", json=item_data, headers=headers)
        self.assertEqual(resp_item.status_code, 201)
        item_id = resp_item.json()["id"]

        # 2. Listar itens
        resp_lista = self.client.get("/itens", headers=headers)
        self.assertEqual(resp_lista.status_code, 200)
        self.assertEqual(len(resp_lista.json()), 1)
        self.assertEqual(resp_lista.json()[0]["nome"], "Arroz")

        # 3. Adicionar quantidade (2 + 3 = 5)
        resp_add = self.client.patch(
            f"/itens/{item_id}/adicionar", json={"quantidade": 3}, headers=headers
        )
        self.assertEqual(resp_add.status_code, 200)
        self.assertEqual(resp_add.json()["quantidade"], 5)

        # 4. Remover quantidade (5 - 4 = 1)
        resp_rem = self.client.patch(
            f"/itens/{item_id}/remover", json={"quantidade": 4}, headers=headers
        )
        self.assertEqual(resp_rem.status_code, 200)
        self.assertEqual(resp_rem.json()["quantidade"], 1)

        # 5. Lista de compras deve conter o item pois quantidade (1) < mínima (3)
        resp_compras = self.client.get("/compras", headers=headers)
        self.assertEqual(resp_compras.status_code, 200)
        compras_data = resp_compras.json()
        self.assertEqual(compras_data["total_itens"], 1)
        self.assertEqual(compras_data["itens"][0]["quantidade_sugerida"], 2)
        self.assertIn("Lista de Compras - Despensa", compras_data["texto_whatsapp"])
        self.assertIn("Arroz", compras_data["texto_whatsapp"])

        # 6. Alertas
        resp_alertas = self.client.get("/alertas", headers=headers)
        self.assertEqual(resp_alertas.status_code, 200)
        self.assertEqual(resp_alertas.json()["total_alertas"], 1)

        # 7. Deletar item
        resp_del = self.client.delete(f"/itens/{item_id}", headers=headers)
        self.assertEqual(resp_del.status_code, 204)

        # Verifica que a lista agora está vazia
        resp_lista_vazia = self.client.get("/itens", headers=headers)
        self.assertEqual(len(resp_lista_vazia.json()), 0)

    def test_isolamento_entre_duas_despensas(self):
        # Usuário 1 na Despensa A
        token1 = self._cadastrar_e_obter_token(
            nome="User 1",
            email="user1@teste.com",
            nome_despensa="Despensa A",
        )

        # Usuário 2 na Despensa B
        token2 = self._cadastrar_e_obter_token(
            nome="User 2",
            email="user2@teste.com",
            nome_despensa="Despensa B",
        )

        # Usuário 1 cadastra Café
        self.client.post(
            "/itens",
            json={"nome": "Café", "quantidade": 1, "quantidade_minima": 1, "local": "Armário"},
            headers={"Authorization": f"Bearer {token1}"},
        )

        # Usuário 2 cadastra Leite
        self.client.post(
            "/itens",
            json={"nome": "Leite", "quantidade": 2, "quantidade_minima": 2, "local": "Geladeira"},
            headers={"Authorization": f"Bearer {token2}"},
        )

        # Usuário 1 só vê Café
        itens_u1 = self.client.get("/itens", headers={"Authorization": f"Bearer {token1}"}).json()
        self.assertEqual(len(itens_u1), 1)
        self.assertEqual(itens_u1[0]["nome"], "Café")

        # Usuário 2 só vê Leite
        itens_u2 = self.client.get("/itens", headers={"Authorization": f"Bearer {token2}"}).json()
        self.assertEqual(len(itens_u2), 1)
        self.assertEqual(itens_u2[0]["nome"], "Leite")


if __name__ == "__main__":
    unittest.main()
