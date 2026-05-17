import sqlite3
from typing import List, Optional
from datetime import datetime
from domain.entidades import Projeto
from ports.repositorio import IProjetoRepository


class SQLiteProjetoRepository(IProjetoRepository):
    """
    Este é o Adaptador de Saída.
    Ele assina o contrato 'IProjetoRepository' e sabe como traduzir a nossa
    Entidade Pura (Projeto) para comandos SQL no banco SQLite.
    Zero ORM, zero Django. Apenas SQL e Python nativo.
    """

    def __init__(self, caminho_banco: str = "banco_gestao.sqlite"):
        self.caminho_banco = caminho_banco
        self._criar_tabela_se_nao_existir()

    def _conectar(self):
        return sqlite3.connect(self.caminho_banco)

    def _criar_tabela_se_nao_existir(self):
        query = """
                CREATE TABLE IF NOT EXISTS projetos \
                ( \
                    id \
                    INTEGER \
                    PRIMARY \
                    KEY \
                    AUTOINCREMENT, \
                    nome \
                    TEXT \
                    NOT \
                    NULL, \
                    descricao \
                    TEXT, \
                    data_criacao \
                    TIMESTAMP, \
                    ultima_alteracao \
                    TIMESTAMP
                ) \
                """
        with self._conectar() as conn:
            conn.execute(query)

    def salvar(self, projeto: Projeto) -> Projeto:
        with self._conectar() as conn:
            cursor = conn.cursor()

            # Se o projeto já tem ID, é um Update. Se não, é um Insert.
            if projeto.id:
                query = """
                        UPDATE projetos
                        SET nome             = ?, \
                            descricao        = ?, \
                            ultima_alteracao = ?
                        WHERE id = ? \
                        """
                cursor.execute(query, (projeto.nome, projeto.descricao, projeto.ultima_alteracao, projeto.id))
            else:
                query = """
                        INSERT INTO projetos (nome, descricao, data_criacao, ultima_alteracao)
                        VALUES (?, ?, ?, ?) \
                        """
                cursor.execute(query, (projeto.nome, projeto.descricao, projeto.data_criacao, projeto.ultima_alteracao))
                projeto.id = cursor.lastrowid  # Pega o ID gerado pelo banco

            conn.commit()
        return projeto

    def buscar_por_id(self, projeto_id: int) -> Optional[Projeto]:
        query = "SELECT id, nome, descricao, data_criacao, ultima_alteracao FROM projetos WHERE id = ?"
        with self._conectar() as conn:
            cursor = conn.cursor()
            linha = cursor.execute(query, (projeto_id,)).fetchone()

            if linha:
                return Projeto(
                    id=linha[0],
                    nome=linha[1],
                    descricao=linha[2],
                    data_criacao=linha[3],
                    ultima_alteracao=linha[4]
                )
        return None

    def listar_todos(self) -> List[Projeto]:
        query = "SELECT id, nome, descricao, data_criacao, ultima_alteracao FROM projetos"
        projetos = []
        with self._conectar() as conn:
            cursor = conn.cursor()
            linhas = cursor.execute(query).fetchall()

            for linha in linhas:
                projetos.append(Projeto(
                    id=linha[0],
                    nome=linha[1],
                    descricao=linha[2],
                    data_criacao=linha[3],
                    ultima_alteracao=linha[4]
                ))
        return projetos

    def deletar(self, projeto_id: int) -> bool:
        """
        Execução direta do comando DELETE usando SQL nativo.
        """
        query = "DELETE FROM projetos WHERE id = ?"
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (projeto_id,))
            conn.commit()
            # Retorna True se pelo menos uma linha foi modificada no banco
            return cursor.rowcount > 0