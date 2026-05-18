from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Importamos a nossa arquitetura limpa
from use_cases.gerenciar_projetos import GerenciarProjetosUseCase
from adapters.repositorio_sqlite import SQLiteProjetoRepository

# 1. Configuração do Adaptador HTTP (FastAPI)
app = FastAPI(title="Microsserviço de Gestão Organizacional")

# Permitir que o teu Front-End (HTML/JS) consiga fazer requisições para esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Num ambiente real, colocaríamos o domínio exato do Front-End
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Injeção de Dependências (A montagem do Hexágono)
# Instanciamos o adaptador de banco de dados
repositorio = SQLiteProjetoRepository(caminho_banco="banco_gestao.sqlite")
# Injetamos o adaptador no Caso de Uso
use_case = GerenciarProjetosUseCase(repositorio=repositorio)

# Garantir que o projeto "MVP" existe logo que o servidor liga
use_case.garantir_projeto_padrao()

# 3. DTOs (Data Transfer Objects) - O que entra e sai da API
# O Pydantic valida o JSON do Front-End. O nosso Núcleo não conhece o Pydantic!
class ProjetoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None

class ProjetoResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]

# 4. Rotas HTTP (As tomadas da Porta de Entrada)

@app.get("/api/projetos/", response_model=List[ProjetoResponse])
def listar_projetos():
    """
    Lista todos os projetos. Repara que a View (Rota) é 'burra'.
    Ela apenas pede ao Caso de Uso para trabalhar e devolve a resposta.
    """
    return use_case.listar_projetos()

@app.post("/api/projetos/", response_model=ProjetoResponse)
def criar_projeto(projeto_in: ProjetoCreate):
    """
    Recebe um JSON, envia para o Caso de Uso criar o projeto.
    Se o nosso Núcleo disparar um erro de regra de negócio (ex: nome curto),
    a API apanha o erro e traduz para um Erro HTTP 400.
    """
    try:
        novo_projeto = use_case.criar_projeto(
            nome=projeto_in.nome,
            descricao=projeto_in.descricao
        )
        return novo_projeto
    except ValueError as erro:
        # Tradução de erro de Domínio para erro de Web
        raise HTTPException(status_code=400, detail=str(erro))

@app.delete("/api/projetos/{projeto_id}", response_model=dict)
def deletar_projeto(projeto_id: int):
    """
    Porta de Entrada HTTP para exclusão.
    Recebe o ID da URL e encaminha para o Caso de Uso tratar.
    """
    try:
        sucesso = use_case.deletar_projeto(projeto_id)
        return {"success": sucesso, "message": f"Projeto {projeto_id} removido com sucesso."}
    except ValueError as erro:
        raise HTTPException(status_code=404, detail=str(erro))
    except Exception as erro:
        raise HTTPException(status_code=500, detail=f"Erro interno de infraestrutura: {str(erro)}")

@app.put("/api/projetos/{projeto_id}", response_model=ProjetoResponse)
def editar_projeto(projeto_id: int, projeto_in: ProjetoCreate):
    """
    Porta de entrada HTTP para modificação dos dados cadastrais do projeto.
    """
    try:
        projeto_editado = use_case.editar_projeto(
            projeto_id=projeto_id,
            nome=projeto_in.nome,
            descricao=projeto_in.descricao
        )
        return projeto_editado
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))
    except Exception as erro:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(erro)}")