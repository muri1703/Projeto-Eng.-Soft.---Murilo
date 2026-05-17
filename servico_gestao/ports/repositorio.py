from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entidades import Projeto


class IProjetoRepository(ABC):
    """
    Este é o contrato. O domínio exige que qualquer tecnologia de base de dados
    (SQLite, PostgreSQL, MongoDB, ou mesmo uma API externa) obedeça a estas exatas regras.
    O domínio não se adapta à base de dados; a base de dados adapta-se ao domínio.
    """

    @abstractmethod
    def salvar(self, projeto: Projeto) -> Projeto:
        pass

    @abstractmethod
    def buscar_por_id(self, projeto_id: int) -> Optional[Projeto]:
        pass

    @abstractmethod
    def listar_todos(self) -> List[Projeto]:
        pass

    @abstractmethod
    def deletar(self, projeto_id: int) -> bool:
        pass