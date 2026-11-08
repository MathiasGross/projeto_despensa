import unittest
from src.database.connection import get_connection, init_db
from src.models.item import Item
from src.repositories.sqlite_item_repository import SqliteItemRepository
from src.repositories.user_repository import UserRepository
from src.services.item_service import ItemService


class TestSqliteRepository(unittest.TestCase):
    def setUp(self):
        # Usa banco SQLite em memória isolado para cada teste
        self.conn = get_connection(":memory:")
        init_db(self.conn)
        self.user_repo = UserRepository(self.conn)
        self.item_repo = SqliteItemRepository(self.conn)
        self.service = ItemService(self.item_repo)

        # Cria despensa padrão para os testes
        self.despensa = self.user_repo.criar_despensa("Casa Mathias")

    def tearDown(self):
        self.conn.close()

    def test_criar_e_buscar_despensa(self):
        buscada = self.user_repo.buscar_despensa_por_id(self.despensa.id)
        self.assertIsNotNone(buscada)
        self.assertEqual(buscada.nome, "Casa Mathias")

    def test_criar_usuarios_para_mesma_despensa(self):
        # Simula você e a outra pessoa vinculados à mesma despensa
        user1 = self.user_repo.criar_usuario(
            despensa_id=self.despensa.id,
            nome="Mathias",
            email="mathias@teste.com",
            senha_hash="hash_seguro_123",
        )
        user2 = self.user_repo.criar_usuario(
            despensa_id=self.despensa.id,
            nome="Parceira",
            email="parceira@teste.com",
            senha_hash="hash_seguro_456",
        )

        self.assertEqual(user1.despensa_id, self.despensa.id)
        self.assertEqual(user2.despensa_id, self.despensa.id)

        membros = self.user_repo.listar_usuarios_por_despensa(self.despensa.id)
        self.assertEqual(len(membros), 2)
        emails = [u.email for u in membros]
        self.assertIn("mathias@teste.com", emails)
        self.assertIn("parceira@teste.com", emails)

    def test_impedir_email_duplicado(self):
        self.user_repo.criar_usuario(
            despensa_id=self.despensa.id,
            nome="Mathias",
            email="duplicado@teste.com",
            senha_hash="hash1",
        )
        with self.assertRaises(ValueError):
            self.user_repo.criar_usuario(
                despensa_id=self.despensa.id,
                nome="Outro Mathias",
                email="duplicado@teste.com",
                senha_hash="hash2",
            )

    def test_adicionar_e_buscar_item_sqlite(self):
        item = Item(
            id=0,
            nome="Café",
            quantidade=2,
            local="Armário",
            quantidade_minima=1,
            obs="Extra forte",
            despensa_id=self.despensa.id,
        )
        salvo = self.item_repo.adicionar(item)
        self.assertGreater(salvo.id, 0)

        encontrado = self.item_repo.busca_por_id(salvo.id, despensa_id=self.despensa.id)
        self.assertIsNotNone(encontrado)
        self.assertEqual(encontrado.nome, "Café")
        self.assertEqual(encontrado.quantidade, 2)
        self.assertEqual(encontrado.obs, "Extra forte")

    def test_isolamento_entre_despensas(self):
        # Despensa 2 (outra família / outra casa)
        despensa2 = self.user_repo.criar_despensa("Casa dos Pais")

        # Cadastra arroz na despensa 1 e feijão na despensa 2
        item_d1 = Item(
            id=0, nome="Arroz", quantidade=5, local="Despensa", despensa_id=self.despensa.id
        )
        item_d2 = Item(
            id=0, nome="Feijão", quantidade=3, local="Despensa", despensa_id=despensa2.id
        )
        self.item_repo.adicionar(item_d1)
        self.item_repo.adicionar(item_d2)

        # Itens da despensa 1 só devem conter Arroz
        itens_d1 = self.item_repo.listar_por_despensa(self.despensa.id)
        self.assertEqual(len(itens_d1), 1)
        self.assertEqual(itens_d1[0].nome, "Arroz")

        # Itens da despensa 2 só devem conter Feijão
        itens_d2 = self.item_repo.listar_por_despensa(despensa2.id)
        self.assertEqual(len(itens_d2), 1)
        self.assertEqual(itens_d2[0].nome, "Feijão")

        # Despensa 1 não consegue buscar item da despensa 2 por ID
        item_alheio = self.item_repo.busca_por_id(item_d2.id, despensa_id=self.despensa.id)
        self.assertIsNone(item_alheio)

    def test_atualizar_quantidade_e_deletar_sqlite(self):
        item = Item(
            id=0, nome="Açúcar", quantidade=1, local="Armário", despensa_id=self.despensa.id
        )
        salvo = self.item_repo.adicionar(item)

        # Atualiza quantidade
        atualizado = self.item_repo.atualizar_quantidade(
            salvo.id, nova_quantidade=4, despensa_id=self.despensa.id
        )
        self.assertTrue(atualizado)

        buscado = self.item_repo.busca_por_id(salvo.id, despensa_id=self.despensa.id)
        self.assertEqual(buscado.quantidade, 4)

        # Deleta item
        deletado = self.item_repo.deletar_por_id(salvo.id, despensa_id=self.despensa.id)
        self.assertTrue(deletado)
        self.assertIsNone(self.item_repo.busca_por_id(salvo.id, despensa_id=self.despensa.id))

    def test_item_service_integrado_com_sqlite(self):
        # Cadastro via service no SQLite
        item = self.service.cadastrar_item(
            nome="Detergente",
            quantidade=1,
            local="Cozinha",
            quantidade_minima=3,
            despensa_id=self.despensa.id,
        )
        self.assertGreater(item.id, 0)

        # Movimentação de estoque reflete no banco
        self.service.adicionar_estoque(item.id, 2, despensa_id=self.despensa.id)
        item_no_banco = self.item_repo.busca_por_id(item.id, despensa_id=self.despensa.id)
        self.assertEqual(item_no_banco.quantidade, 3)

        # Geração de lista de compras e alertas com SQLite
        # No momento está com 3 e mínima 3 -> está abaixo ou no mínimo, então gera compra
        lista_compras = self.service.gerar_lista_compras(despensa_id=self.despensa.id)
        self.assertEqual(len(lista_compras), 1)
        self.assertEqual(lista_compras[0]["nome"], "Detergente")

        texto_zap = self.service.formatar_lista_compras_texto(despensa_id=self.despensa.id)
        self.assertIn("Detergente", texto_zap)
        self.assertIn("Lista de Compras - Despensa", texto_zap)


if __name__ == "__main__":
    unittest.main()
