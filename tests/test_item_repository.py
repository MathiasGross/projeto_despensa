import unittest
from src.models.item import Item
from src.repositories.item_repository import ItemRepository

class TestItemRepository(unittest.TestCase):

    def test_adicionar_item_com_sucesso(self):
        repositorio = ItemRepository()
        produto = Item(id=1, nome="Arroz", quantidade=5, local="Despensa")

        repositorio.adicionar(produto)
        self.assertEqual(len(repositorio.listar_todos()), 1)
        self.assertEqual(repositorio.listar_todos()[0], produto)

    
    def test_buscar_por_id(self):
        
        produto = Item(id=1, nome="Feijão", quantidade=2, local="Armário")
        repositorio = ItemRepository()

        repositorio.adicionar(produto)
        item_encontrado = repositorio.busca_por_id(1)

        self.assertEqual(item_encontrado, produto)
        self.assertEqual(item_encontrado.nome, 'Feijão')

    def test_buscar_por_id_inexistente(self):

        repositorio = ItemRepository()

        resultado = repositorio.busca_por_id(99)

        self.assertIsNone(resultado)

    def test_deletar_por_id_com_sucesso(self):

        repositorio = ItemRepository()
        produto = Item(id=1, nome="Feijão", quantidade=2, local="Armário")
        repositorio.adicionar(produto)

        resultado = repositorio.deletar_por_id(1)

        self.assertTrue(resultado)
        self.assertEqual(len(repositorio.listar_todos()), 0)
        self.assertIsNone(repositorio.busca_por_id(1))

    def test_deletar_por_id_inexistente(self):

        repositorio = ItemRepository()
        produto = Item(id=1, nome="Feijão", quantidade=2, local="Armário")
        repositorio.adicionar(produto)

        resultado = repositorio.deletar_por_id(99)

        self.assertFalse(resultado)
        self.assertEqual(len(repositorio.listar_todos()), 1)







    if __name__ == "__main__":
        unittest.main()