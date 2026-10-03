import unittest
from src.models.item import Item

class TestItem(unittest.TestCase):
    def test_criacao_item_com_sucesso(self):
        item = Item(id=1, nome="Arroz", quantidade=5, local="Despensa", quantidade_minima=2, obs="Tipo 1")
        self.assertEqual(item.id,1)
        self.assertEqual(item.nome, "Arroz")
        self.assertEqual(item.quantidade, 5)
        self.assertEqual(item.local, "Despensa")
        self.assertEqual(item.quantidade_minima, 2)
        self.assertEqual(item.obs, "Tipo 1")

    def test_adicionar_quantidade_sucesso(self):
        
        item = Item(id=1, nome="Arroz", quantidade=5, local="Despensa")
        
        item.adicionar_quantidade(3)
        
        self.assertEqual(item.quantidade, 8)

    def test_adicionar_quantidade_invalida(self):
        item = Item(id=1, nome="Arroz", quantidade=5, local="Despensa")
        
        with self.assertRaises(ValueError):
            item.adicionar_quantidade(0)
        
        with self.assertRaises(ValueError):
            item.adicionar_quantidade(-2)    

    def test_remover_quantidade_sucesso(self):
        item = Item(id=1, nome="Arroz", quantidade=5, local="Despensa")
        
        item.remover_quantidade(2)
        
        self.assertEqual(item.quantidade, 3)

    def test_remover_quantidade_invalida_ou_insuficiente(self):
        item = Item(id=1, nome="Arroz", quantidade=5, local="Despensa")
        
        with self.assertRaises(ValueError):
            item.remover_quantidade(0)
            
        with self.assertRaises(ValueError):
            item.remover_quantidade(10)

if __name__ == "__main__":
    unittest.main()

    