import sqlite3
from src.models.item import Item


class SqliteItemRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def adicionar(self, item: Item, despensa_id: int | None = None) -> Item:
        despensa = despensa_id if despensa_id is not None else getattr(item, "despensa_id", 1)
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO itens (despensa_id, nome, quantidade, quantidade_minima, local, obs)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                despensa,
                item.nome,
                item.quantidade,
                item.quantidade_minima,
                item.local,
                item.obs,
            ),
        )
        self.conn.commit()
        item.id = cursor.lastrowid
        item.despensa_id = despensa
        return item

    def listar_por_despensa(self, despensa_id: int) -> list[Item]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, despensa_id, nome, quantidade, quantidade_minima, local, obs
            FROM itens
            WHERE despensa_id = ?
            ORDER BY nome ASC
            """,
            (despensa_id,),
        )
        rows = cursor.fetchall()
        return [
            Item(
                id=row["id"],
                nome=row["nome"],
                quantidade=row["quantidade"],
                local=row["local"],
                quantidade_minima=row["quantidade_minima"],
                obs=row["obs"],
                despensa_id=row["despensa_id"],
            )
            for row in rows
        ]

    def listar_todos(self) -> list[Item]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, despensa_id, nome, quantidade, quantidade_minima, local, obs
            FROM itens
            ORDER BY nome ASC
            """
        )
        rows = cursor.fetchall()
        return [
            Item(
                id=row["id"],
                nome=row["nome"],
                quantidade=row["quantidade"],
                local=row["local"],
                quantidade_minima=row["quantidade_minima"],
                obs=row["obs"],
                despensa_id=row["despensa_id"],
            )
            for row in rows
        ]

    def busca_por_id(self, item_id: int, despensa_id: int | None = None) -> Item | None:
        cursor = self.conn.cursor()
        if despensa_id is not None:
            cursor.execute(
                """
                SELECT id, despensa_id, nome, quantidade, quantidade_minima, local, obs
                FROM itens
                WHERE id = ? AND despensa_id = ?
                """,
                (item_id, despensa_id),
            )
        else:
            cursor.execute(
                """
                SELECT id, despensa_id, nome, quantidade, quantidade_minima, local, obs
                FROM itens
                WHERE id = ?
                """,
                (item_id,),
            )
        row = cursor.fetchone()
        if not row:
            return None
        return Item(
            id=row["id"],
            nome=row["nome"],
            quantidade=row["quantidade"],
            local=row["local"],
            quantidade_minima=row["quantidade_minima"],
            obs=row["obs"],
            despensa_id=row["despensa_id"],
        )

    def atualizar_quantidade(
        self, item_id: int, nova_quantidade: int, despensa_id: int | None = None
    ) -> bool:
        cursor = self.conn.cursor()
        if despensa_id is not None:
            cursor.execute(
                """
                UPDATE itens
                SET quantidade = ?, atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ? AND despensa_id = ?
                """,
                (nova_quantidade, item_id, despensa_id),
            )
        else:
            cursor.execute(
                """
                UPDATE itens
                SET quantidade = ?, atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (nova_quantidade, item_id),
            )
        self.conn.commit()
        return cursor.rowcount > 0

    def deletar_por_id(self, item_id: int, despensa_id: int | None = None) -> bool:
        cursor = self.conn.cursor()
        if despensa_id is not None:
            cursor.execute(
                "DELETE FROM itens WHERE id = ? AND despensa_id = ?",
                (item_id, despensa_id),
            )
        else:
            cursor.execute("DELETE FROM itens WHERE id = ?", (item_id,))
        self.conn.commit()
        return cursor.rowcount > 0
