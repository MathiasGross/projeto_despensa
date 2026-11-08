import unittest
from src.repositories.item_repository import ItemRepository
from src.services.item_service import ItemService


class TestItemService(unittest.TestCase):
    def setUp(self):
        self.repository = ItemRepository()
        self.service = ItemService(self.repository)

    def test_cadastrar_item_com_sucesso(self):
        item = self.service.cadastrar_item(
            nome="Arroz",
            quantidade=5,
            local="Despensa",
            quantidade_minima=2,
            obs="Integral",
        )
        self.assertEqual(item.id, 1)
        self.assertEqual(item.nome, "Arroz")
        self.assertEqual(item.quantidade, 5)
        self.assertEqual(item.quantidade_minima, 2)
        self.assertEqual(item.local, "Despensa")
        self.assertEqual(item.obs, "Integral")
        self.assertEqual(len(self.service.listar_todos()), 1)

    def test_cadastrar_item_com_id_incremental(self):
        item1 = self.service.cadastrar_item(nome="Arroz", quantidade=2, local="Armário")
        item2 = self.service.cadastrar_item(nome="Feijão", quantidade=1, local="Armário")
        self.assertEqual(item1.id, 1)
        self.assertEqual(item2.id, 2)

    def test_cadastrar_item_validacoes(self):
        with self.assertRaises(ValueError):
            self.service.cadastrar_item(nome="   ", quantidade=1, local="Despensa")

        with self.assertRaises(ValueError):
            self.service.cadastrar_item(nome="Café", quantidade=-1, local="Despensa")

        with self.assertRaises(ValueError):
            self.service.cadastrar_item(
                nome="Café", quantidade=1, local="Despensa", quantidade_minima=-2
            )

    def test_buscar_por_id_existente_e_inexistente(self):
        item = self.service.cadastrar_item(nome="Açúcar", quantidade=3, local="Despensa")
        encontrado = self.service.buscar_por_id(item.id)
        self.assertEqual(encontrado.nome, "Açúcar")

        with self.assertRaises(ValueError):
            self.service.buscar_por_id(999)

    def test_deletar_item_com_sucesso_e_inexistente(self):
        item = self.service.cadastrar_item(nome="Sal", quantidade=1, local="Cozinha")
        self.assertTrue(self.service.deletar_item(item.id))
        self.assertEqual(len(self.service.listar_todos()), 0)

        with self.assertRaises(ValueError):
            self.service.deletar_item(999)

    def test_movimentacao_de_estoque(self):
        item = self.service.cadastrar_item(nome="Leite", quantidade=4, local="Geladeira")

        self.service.adicionar_estoque(item.id, 2)
        self.assertEqual(item.quantidade, 6)

        self.service.remover_estoque(item.id, 3)
        self.assertEqual(item.quantidade, 3)

    def test_obter_alertas(self):
        # 1 item zerado (quantidade 0, mínima 2)
        self.service.cadastrar_item(nome="Café", quantidade=0, local="Armário", quantidade_minima=2)
        # 1 item acabando (quantidade 1, mínima 3)
        self.service.cadastrar_item(nome="Azeite", quantidade=1, local="Despensa", quantidade_minima=3)
        # 1 item normal (quantidade 5, mínima 2)
        self.service.cadastrar_item(nome="Arroz", quantidade=5, local="Despensa", quantidade_minima=2)

        alertas = self.service.obter_alertas()
        self.assertEqual(len(alertas["zerados"]), 1)
        self.assertEqual(alertas["zerados"][0].nome, "Café")

        self.assertEqual(len(alertas["acabando"]), 1)
        self.assertEqual(alertas["acabando"][0].nome, "Azeite")

        self.assertEqual(alertas["total_alertas"], 2)

    def test_gerar_lista_compras(self):
        # Item 1: precisa comprar 3 (atual 0, mínima 3)
        self.service.cadastrar_item(nome="Sabão", quantidade=0, local="Lavanderia", quantidade_minima=3)
        # Item 2: precisa comprar 2 (atual 1, mínima 3)
        self.service.cadastrar_item(nome="Detergente", quantidade=1, local="Cozinha", quantidade_minima=3)
        # Item 3: no limite da mínima (atual 2, mínima 2) -> sugere 1
        self.service.cadastrar_item(nome="Sal", quantidade=2, local="Cozinha", quantidade_minima=2)
        # Item 4: abastecido (atual 5, mínima 2) -> não deve entrar na lista
        self.service.cadastrar_item(nome="Arroz", quantidade=5, local="Despensa", quantidade_minima=2)

        lista = self.service.gerar_lista_compras()
        self.assertEqual(len(lista), 3)

        nomes_na_lista = [i["nome"] for i in lista]
        self.assertIn("Sabão", nomes_na_lista)
        self.assertIn("Detergente", nomes_na_lista)
        self.assertIn("Sal", nomes_na_lista)
        self.assertNotIn("Arroz", nomes_na_lista)

        item_sabao = next(i for i in lista if i["nome"] == "Sabão")
        self.assertEqual(item_sabao["quantidade_sugerida"], 3)

        item_detergente = next(i for i in lista if i["nome"] == "Detergente")
        self.assertEqual(item_detergente["quantidade_sugerida"], 2)

        item_sal = next(i for i in lista if i["nome"] == "Sal")
        self.assertEqual(item_sal["quantidade_sugerida"], 1)

    def test_formatar_lista_compras_texto_vazia(self):
        texto = self.service.formatar_lista_compras_texto()
        self.assertIn("Tudo abastecido", texto)

    def test_formatar_lista_compras_texto_com_itens(self):
        self.service.cadastrar_item(
            nome="Café",
            quantidade=0,
            local="Armário",
            quantidade_minima=2,
            obs="Em pó",
        )
        texto = self.service.formatar_lista_compras_texto()
        self.assertIn("Lista de Compras - Despensa", texto)
        self.assertIn("Café", texto)
        self.assertIn("(Em pó)", texto)
        self.assertIn("Comprar: 2", texto)
        self.assertIn("Total de itens para comprar: 1", texto)


if __name__ == "__main__":
    unittest.main()
