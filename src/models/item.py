class Item:
    def __init__(
        self,
        id: int,
        nome: str,
        quantidade: int,
        local: str,
        quantidade_minima: int = 1,
        obs: str = "",
        despensa_id: int = 1,
    ):
        self.id = id
        self.nome = nome
        self.quantidade = quantidade
        self.quantidade_minima = quantidade_minima
        self.local = local
        self.obs = obs
        self.despensa_id = despensa_id

    def __repr__(self):
        return (
            f"ID: {self.id} | Despensa: {self.despensa_id}\n"
            f"Nome do Produto: {self.nome}\n"
            f"Quantidade: {self.quantidade}\n"
            f"Local Armazenamento: {self.local}"
        )

    def adicionar_quantidade(self, quantidade: int):

        if quantidade <= 0:
            raise ValueError("ERRO ! Digite uma quantidade válida maior que 0!")            
        else:   
            self.quantidade += quantidade           

    def remover_quantidade(self, quantidade: int):

        if quantidade <= 0:
            raise ValueError("O valor a ser removido tem que ser maior que 0.")
        elif quantidade > self.quantidade:
            raise ValueError("Quantidade insuficiente em estoque.")
        else:
            self.quantidade -= quantidade            

    def esta_abaixo_do_minimo(self):

        return self.quantidade <= self.quantidade_minima     
            
    def esta_zerado(self):
        return self.quantidade == 0

        

        
        
        
            


        



    

