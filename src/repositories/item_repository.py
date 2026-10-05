from src.models.item import Item

class ItemRepository:

    def __init__(self):
        self._itens = []

    def adicionar(self, item : Item) -> None: 
        self._itens.append(item)

    def listar_todos(self) -> list[Item]:
        return self._itens

    def busca_por_id(self, id:int)-> Item | None:
        
        for item in self._itens:
            if item.id == id:
                return item

        return None

    def deletar_por_id(self, id:int) -> bool:
        for item in self._itens:
            if item.id == id:
                self._itens.remove(item)
                return True
        return False
        
                