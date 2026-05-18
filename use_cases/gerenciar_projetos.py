from typing import List, Optional
from domain.entidades import Projeto
from ports.repositorio import IProjetoRepository
from datetime import datetime


class GerenciarProjetosUseCase:
    """
    Esta classe orquestra as ações que o utilizador pode fazer no sistema.
    Ela não sabe se os dados vêm do Django, de uma API ou de um ficheiro de texto.
    Apenas confia na "Porta" (IProjetoRepository) que lhe foi entregue.
    """

    def __init__(self, repositorio: IProjetoRepository):
        # Injeção de Dependência: o repositório real será "injetado" aqui
        # por quem instanciar esta classe. O Caso de Uso só sabe que
        # este repositório respeita o contrato de IProjetoRepository.
        self.repositorio = repositorio

    def criar_projeto(self, nome: str, descricao: str = None) -> Projeto:
        # 1. Instancia a Entidade Pura
        novo_projeto = Projeto(nome=nome, descricao=descricao)

        # 2. Executa as regras de negócio intrínsecas (validação)
        novo_projeto.validar()

        # 3. Usa a Porta para salvar
        return self.repositorio.salvar(novo_projeto)

    def garantir_projeto_padrao(self) -> Projeto:
        """
        No teu código original, o `views.py` do Django verificava se existia
        um projeto e criava o "MVP - Gestão Inicial".
        Essa lógica de negócio não pertence ao controlador HTTP (views.py),
        pertence ao Caso de Uso.
        """
        projetos = self.repositorio.listar_todos()

        if not projetos:
            return self.criar_projeto(
                nome="MVP - Gestão Inicial",
                descricao="Projeto de teste gerado pelo sistema."
            )

        return projetos[0]

    def listar_projetos(self) -> List[Projeto]:
        return self.repositorio.listar_todos()

    def editar_projeto(self, projeto_id: int, nome: str, descricao: str = None) -> Projeto:
        """
        Regra de aplicação para edição completa dos dados de um projeto.
        """
        # 1. Recupera o estado atual do projeto
        projeto = self.repositorio.buscar_por_id(projeto_id)
        if not projeto:
            raise ValueError(f"Projeto com o ID {projeto_id} não foi encontrado.")

        # 2. Modifica os atributos com os novos dados passados pelo usuário
        projeto.nome = nome
        projeto.descricao = descricao
        projeto.ultima_alteracao = datetime.now()

        # 3. Força o Domínio a validar se as novas alterações são permitidas
        projeto.validar()

        # 4. Grava no banco usando o método salvar (que fará o UPDATE devido ao ID)
        return self.repositorio.salvar(projeto)

    def deletar_projeto(self, projeto_id: int) -> bool:
        projeto = self.repositorio.buscar_por_id(projeto_id)
        if not projeto:
            raise ValueError(f"Projeto com o ID {projeto_id} não foi encontrado.")

        return self.repositorio.deletar(projeto_id)