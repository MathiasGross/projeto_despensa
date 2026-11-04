from src.models.item import Item
from src.repositories.item_repository import ItemRepository


class ItemService:
    def __init__(self, repository: ItemRepository):
        self.repository = repository

    def cadastrar_item(
        self,
        nome: str,
        quantidade: int,
        local: str,
        quantidade_minima: int = 1,
        obs: str = "",
    ) -> Item:
        nome_limpo = nome.strip() if nome else ""
        if not nome_limpo:
            raise ValueError("O nome do produto não pode ser vazio.")
        if quantidade < 0:
            raise ValueError("A quantidade inicial não pode ser negativa.")
        if quantidade_minima < 0:
            raise ValueError("A quantidade mínima não pode ser negativa.")

        todos = self.repository.listar_todos()
        proximo_id = max([item.id for item in todos], default=0) + 1

        novo_item = Item(
            id=proximo_id,
            nome=nome_limpo,
            quantidade=quantidade,
            local=local.strip() if local else "",
            quantidade_minima=quantidade_minima,
            obs=obs.strip() if obs else "",
        )
        self.repository.adicionar(novo_item)
        return novo_item

    def listar_todos(self) -> list[Item]:
        return self.repository.listar_todos()

    def buscar_por_id(self, item_id: int) -> Item:
        item = self.repository.busca_por_id(item_id)
        if not item:
            raise ValueError(f"Item com ID {item_id} não encontrado.")
        return item

    def deletar_item(self, item_id: int) -> bool:
        removido = self.repository.deletar_por_id(item_id)
        if not removido:
            raise ValueError(f"Item com ID {item_id} não encontrado para exclusão.")
        return True

    def adicionar_estoque(self, item_id: int, quantidade: int) -> Item:
        item = self.buscar_por_id(item_id)
        item.adicionar_quantidade(quantidade)
        return item

    def remover_estoque(self, item_id: int, quantidade: int) -> Item:
        item = self.buscar_por_id(item_id)
        item.remover_quantidade(quantidade)
        return item

    def obter_alertas(self) -> dict:
        todos = self.repository.listar_todos()
        zerados = [item for item in todos if item.esta_zerado()]
        acabando = [
            item
            for item in todos
            if item.esta_abaixo_do_minimo() and not item.esta_zerado()
        ]
        return {
            "zerados": zerados,
            "acabando": acabando,
            "total_alertas": len(zerados) + len(acabando),
        }

    def gerar_lista_compras(self) -> list[dict]:
        todos = self.repository.listar_todos()
        lista = []

        for item in todos:
            if item.esta_abaixo_do_minimo():
                diferenca = item.quantidade_minima - item.quantidade
                quantidade_sugerida = diferenca if diferenca > 0 else 1

                lista.append(
                    {
                        "item_id": item.id,
                        "nome": item.nome,
                        "quantidade_atual": item.quantidade,
                        "quantidade_minima": item.quantidade_minima,
                        "quantidade_sugerida": quantidade_sugerida,
                        "local": item.local,
                        "obs": item.obs,
                    }
                )
        return lista

    def formatar_lista_compras_texto(
        self, itens_compras: list[dict] | None = None
    ) -> str:
        if itens_compras is None:
            itens_compras = self.gerar_lista_compras()

        if not itens_compras:
            return "🛒 *Lista de Compras - Despensa*\n\n✅ Tudo abastecido! Nenhum item precisando de reposição no momento."

        linhas = [
            "🛒 *Lista de Compras - Despensa*",
            "----------------------------------",
        ]

        for item in itens_compras:
            obs_texto = f" ({item['obs']})" if item.get("obs") else ""
            linhas.append(
                f"▫️ *{item['nome']}*{obs_texto}\n"
                f"   Comprar: {item['quantidade_sugerida']} | Estoque: {item['quantidade_atual']} | Mínimo: {item['quantidade_minima']}"
            )

        linhas.append("----------------------------------")
        linhas.append(f"Total de itens para comprar: {len(itens_compras)}")
        return "\n".join(linhas)
