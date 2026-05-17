from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Projeto:
    nome: str
    descricao: Optional[str] = None
    id: Optional[int] = None
    data_criacao: datetime = field(default_factory=datetime.now)
    ultima_alteracao: datetime = field(default_factory=datetime.now)

    def validar(self):
        """
        Regra de negócio pura. O sistema não pode, sob nenhuma circunstância tecnológica,
        permitir um projeto sem nome válido.
        """
        if not self.nome or len(self.nome.strip()) < 3:
            raise ValueError("Um projeto não pode existir sem um nome válido (mínimo de 3 caracteres).")

        if self.descricao and len(self.descricao) > 1000:
            raise ValueError("A descrição excedeu o limite de caracteres permitido.")

    def atualizar_descricao(self, nova_descricao: str):
        self.descricao = nova_descricao
        self.ultima_alteracao = datetime.now()
        self.validar()