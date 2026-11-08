import os
import unittest
from fastapi.testclient import TestClient
from src.api.dependencies import configurar_db_path
from src.database.connection import get_connection, init_db
from src.main import app
from src.services.email_service import ULTIMOS_CODIGOS_DEV

TEST_DB = "test_auth_advanced.db"


class TestAuthAdvanced(unittest.TestCase):
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

    def test_fluxo_otp_cadastro_completo(self):
        # 1. Cadastro inicial
        resp_cad = self.client.post(
            "/auth/cadastro",
            json={
                "nome": "Carla Silva",
                "email": "carla@exemplo.com",
                "senha": "senhaSegura123!",
                "nome_despensa": "Casa Carla",
            },
        )
        self.assertEqual(resp_cad.status_code, 201)
        self.assertTrue(resp_cad.json()["requer_verificacao"])
        self.assertEqual(resp_cad.json()["email"], "carla@exemplo.com")

        # Código deve estar registrado
        codigo_enviado = ULTIMOS_CODIGOS_DEV.get("carla@exemplo.com")
        self.assertIsNotNone(codigo_enviado)
        self.assertEqual(len(codigo_enviado), 6)

        # 2. Login antes de ativar deve ser bloqueado com 403
        resp_bloq = self.client.post(
            "/auth/login",
            json={"email": "carla@exemplo.com", "senha": "senhaSegura123!"},
        )
        self.assertEqual(resp_bloq.status_code, 403)
        self.assertIn("pendente de verificação", resp_bloq.json()["detail"])

        # 3. Validar com código errado deve falhar com 400
        resp_erro = self.client.post(
            "/auth/verificar-codigo",
            json={"email": "carla@exemplo.com", "codigo": "000000"},
        )
        self.assertEqual(resp_erro.status_code, 400)

        # 4. Validar com código correto mais recente deve ativar e retornar token
        codigo_mais_recente = ULTIMOS_CODIGOS_DEV.get("carla@exemplo.com")
        resp_ok = self.client.post(
            "/auth/verificar-codigo",
            json={"email": "carla@exemplo.com", "codigo": codigo_mais_recente},
        )
        self.assertEqual(resp_ok.status_code, 200)
        dados = resp_ok.json()
        self.assertIn("access_token", dados)
        self.assertTrue(dados["usuario"]["ativo"])
        self.assertTrue(dados["usuario"]["codigo_despensa"].startswith("DESP-"))

        # 5. Tentativa de validar novamente o mesmo código deve falhar (código já usado)
        resp_reuso = self.client.post(
            "/auth/verificar-codigo",
            json={"email": "carla@exemplo.com", "codigo": codigo_mais_recente},
        )
        self.assertEqual(resp_reuso.status_code, 400)

    def test_reenvio_codigo_otp(self):
        self.client.post(
            "/auth/cadastro",
            json={
                "nome": "Pedro",
                "email": "pedro@exemplo.com",
                "senha": "senhaValida123!",
                "nome_despensa": "Casa Pedro",
            },
        )
        cod1 = ULTIMOS_CODIGOS_DEV["pedro@exemplo.com"]

        # Reenviar código
        resp_reenvio = self.client.post(
            "/auth/reenviar-codigo",
            json={"email": "pedro@exemplo.com"},
        )
        self.assertEqual(resp_reenvio.status_code, 200)
        cod2 = ULTIMOS_CODIGOS_DEV["pedro@exemplo.com"]

        # Novo código é válido
        resp_val = self.client.post(
            "/auth/verificar-codigo",
            json={"email": "pedro@exemplo.com", "codigo": cod2},
        )
        self.assertEqual(resp_val.status_code, 200)

    def test_login_com_google(self):
        # 1. Login com Google cria novo usuário e despensa imediatamente ativa
        token_google = "mock-google-token:lucas@gmail.com:Lucas Mendes:google-sub-7788"
        resp = self.client.post(
            "/auth/google",
            json={"id_token": token_google, "nome_despensa": "Família Mendes"},
        )
        self.assertEqual(resp.status_code, 200)
        dados = resp.json()
        self.assertIn("access_token", dados)
        self.assertEqual(dados["usuario"]["email"], "lucas@gmail.com")
        self.assertEqual(dados["usuario"]["nome"], "Lucas Mendes")
        self.assertTrue(dados["usuario"]["ativo"])
        self.assertTrue(dados["usuario"]["codigo_despensa"].startswith("DESP-"))

        # 2. Re-login com o mesmo Google ID reaproveita a mesma conta
        resp2 = self.client.post(
            "/auth/google",
            json={"id_token": token_google},
        )
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.json()["usuario"]["id"], dados["usuario"]["id"])

    def test_compartilhamento_despensa_com_solicitacao_e_aprovacao(self):
        # Proprietária: Mariana (Despensa A)
        self.client.post(
            "/auth/cadastro",
            json={
                "nome": "Mariana",
                "email": "mariana@exemplo.com",
                "senha": "senhaSegura123!",
                "nome_despensa": "Casa da Mariana",
            },
        )
        cod_mariana = ULTIMOS_CODIGOS_DEV["mariana@exemplo.com"]
        token_mariana = self.client.post(
            "/auth/verificar-codigo",
            json={"email": "mariana@exemplo.com", "codigo": cod_mariana},
        ).json()["access_token"]
        headers_mariana = {"Authorization": f"Bearer {token_mariana}"}

        # Obter código da despensa de Mariana
        info_despensa_mariana = self.client.get(
            "/despensas/minha", headers=headers_mariana
        ).json()
        codigo_convite_mariana = info_despensa_mariana["codigo_convite"]
        self.assertTrue(info_despensa_mariana["e_dono"])
        self.assertTrue(codigo_convite_mariana.startswith("DESP-"))

        # Mariana adiciona um item à despensa dela
        self.client.post(
            "/itens",
            json={
                "nome": "Manteiga",
                "quantidade": 2,
                "quantidade_minima": 1,
                "local": "Geladeira",
            },
            headers=headers_mariana,
        )

        # Usuário Convidado: Roberto (Cria conta com despensa própria provisória)
        self.client.post(
            "/auth/cadastro",
            json={
                "nome": "Roberto",
                "email": "roberto@exemplo.com",
                "senha": "senhaSegura123!",
                "nome_despensa": "Apartamento Roberto",
            },
        )
        cod_roberto = ULTIMOS_CODIGOS_DEV["roberto@exemplo.com"]
        token_roberto = self.client.post(
            "/auth/verificar-codigo",
            json={"email": "roberto@exemplo.com", "codigo": cod_roberto},
        ).json()["access_token"]
        headers_roberto = {"Authorization": f"Bearer {token_roberto}"}

        # 1. Roberto tenta código inexistente -> 404
        resp_invalido = self.client.post(
            "/despensas/solicitar-entrada",
            json={"codigo_convite": "DESP-INEXISTENTE"},
            headers=headers_roberto,
        )
        self.assertEqual(resp_invalido.status_code, 404)

        # 2. Roberto solicita entrada com o código correto da Mariana
        resp_solicitacao = self.client.post(
            "/despensas/solicitar-entrada",
            json={"codigo_convite": codigo_convite_mariana},
            headers=headers_roberto,
        )
        self.assertEqual(resp_solicitacao.status_code, 200)
        self.assertTrue(resp_solicitacao.json()["sucesso"])

        # 3. Roberto NÃO deve ter acesso aos itens de Mariana ainda! (apenas pendente)
        itens_roberto_antes = self.client.get(
            "/itens", headers=headers_roberto
        ).json()
        self.assertEqual(len(itens_roberto_antes), 0)

        # 4. Mariana lista solicitações pendentes e vê Roberto
        solicitacoes_pendentes = self.client.get(
            "/despensas/solicitacoes", headers=headers_mariana
        ).json()
        self.assertEqual(len(solicitacoes_pendentes), 1)
        self.assertEqual(solicitacoes_pendentes[0]["usuario_nome"], "Roberto")
        self.assertEqual(solicitacoes_pendentes[0]["usuario_email"], "roberto@exemplo.com")
        solicitacao_id = solicitacoes_pendentes[0]["id"]

        # 5. Mariana APROVA a solicitação
        resp_aprov = self.client.post(
            f"/despensas/solicitacoes/{solicitacao_id}/aprovar",
            headers=headers_mariana,
        )
        self.assertEqual(resp_aprov.status_code, 200)

        # 6. Agora Roberto tem acesso imediato à despensa de Mariana e vê a Manteiga!
        itens_roberto_depois = self.client.get(
            "/itens", headers=headers_roberto
        ).json()
        self.assertEqual(len(itens_roberto_depois), 1)
        self.assertEqual(itens_roberto_depois[0]["nome"], "Manteiga")

    def test_compartilhamento_despensa_recusa(self):
        # Proprietário
        self.client.post(
            "/auth/cadastro",
            json={
                "nome": "Alice",
                "email": "alice@exemplo.com",
                "senha": "senhaValida123!",
                "nome_despensa": "Casa Alice",
            },
        )
        token_alice = self.client.post(
            "/auth/verificar-codigo",
            json={
                "email": "alice@exemplo.com",
                "codigo": ULTIMOS_CODIGOS_DEV["alice@exemplo.com"],
            },
        ).json()["access_token"]
        headers_alice = {"Authorization": f"Bearer {token_alice}"}
        codigo_alice = self.client.get("/despensas/minha", headers=headers_alice).json()[
            "codigo_convite"
        ]

        # Intruso ou alguém que digitou o código errado
        self.client.post(
            "/auth/cadastro",
            json={
                "nome": "Estranho",
                "email": "estranho@exemplo.com",
                "senha": "senhaValida123!",
                "nome_despensa": "Casa Desconhecida",
            },
        )
        token_estranho = self.client.post(
            "/auth/verificar-codigo",
            json={
                "email": "estranho@exemplo.com",
                "codigo": ULTIMOS_CODIGOS_DEV["estranho@exemplo.com"],
            },
        ).json()["access_token"]
        headers_estranho = {"Authorization": f"Bearer {token_estranho}"}

        # Solicita entrada
        self.client.post(
            "/despensas/solicitar-entrada",
            json={"codigo_convite": codigo_alice},
            headers=headers_estranho,
        )

        # Alice vê a solicitação e RECUSA!
        solicitacoes = self.client.get(
            "/despensas/solicitacoes", headers=headers_alice
        ).json()
        solicitacao_id = solicitacoes[0]["id"]

        resp_recusa = self.client.post(
            f"/despensas/solicitacoes/{solicitacao_id}/recusar",
            headers=headers_alice,
        )
        self.assertEqual(resp_recusa.status_code, 200)

        # Estranho consulta suas solicitações e vê que foi recusada
        minhas = self.client.get(
            "/despensas/minhas-solicitacoes", headers=headers_estranho
        ).json()
        self.assertEqual(minhas[0]["status"], "recusado")


if __name__ == "__main__":
    unittest.main()
