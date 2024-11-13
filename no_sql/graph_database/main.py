from pydantic import BaseModel, Field
from typing import List, Optional
import random
from neo4j import GraphDatabase
from faker import Faker

fake = Faker('pt_BR')

neo4j_uri = "bolt://localhost:7687"
neo4j_user = ""
neo4j_password = ""
neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

# Cursos e disciplinas
cursos_e_disciplinas = {
    "Engenharia de Software": ["Estruturas de Dados", "Sistemas Operacionais", 
                               "Programação", "Banco de Dados", "Algoritmos"],
    "Administração": ["Gestão de Pessoas", "Finanças Corporativas", 
                      "Marketing", "Economia", "Contabilidade"],
    "Direito": ["Introdução ao Direito", "Direito Penal", 
                "Direito Civil", "Direito Empresarial", "Direito Constitucional"]
}

departamentos = {
    "Engenharia de Software": "Departamento de Computação",
    "Administração": "Departamento de Negócios",
    "Direito": "Departamento de Ciências Jurídicas"
}

class Disciplina(BaseModel):
    codigo_disciplina: str = Field(max_length=100)
    nome: str = Field(max_length=100)
    semestre: int
    ano: int
    nota_final: float
    situacao: str

class Curso(BaseModel):
    id_curso: int
    nome: str = Field(max_length=100)
    nome_departamento: str = Field(max_length=100)

class Aluno(BaseModel):
    ra: int
    nome: str = Field(max_length=100)
    email: str = Field(max_length=100)
    telefone: Optional[str] = Field(max_length=100, default=None)
    curso: Curso
    disciplinas: List[Disciplina]
    formado: bool

class Professor(BaseModel):
    id: int
    nome: str = Field(max_length=100)
    email: str = Field(max_length=100)
    telefone: Optional[str] = Field(max_length=100)
    salario: float
    departamento: str
    chefe_departamento: bool

class GrupoTCC(BaseModel):
    id_grupo: int
    tema: str
    orientador: int
    alunos: List[int]

def executar_query(tx, query, parametros=None):
    tx.run(query, parametros or {})

def criar_no_curso(tx, curso):
    query = """
    MERGE (c:Curso {id_curso: $id_curso, nome: $nome, nome_departamento: $nome_departamento})
    """
    executar_query(tx, query, curso)

def criar_no_aluno(tx, aluno):
    query = """
    MERGE (a:Aluno {ra: $ra, nome: $nome, email: $email, telefone: $telefone, formado: $formado})
    WITH a
    MATCH (c:Curso {id_curso: $id_curso})
    MERGE (a)-[:ESTUDA_EM]->(c)
    """
    aluno_dados = {
        "ra": aluno.ra,
        "nome": aluno.nome,
        "email": aluno.email,
        "telefone": aluno.telefone,
        "formado": aluno.formado,
        "id_curso": aluno.curso.id_curso
    }
    executar_query(tx, query, aluno_dados)

def criar_no_professor(tx, professor):
    query = """
    MERGE (p:Professor {id: $id, nome: $nome, email: $email, telefone: $telefone, salario: $salario, chefe_departamento: $chefe_departamento, departamento: $departamento})
    """
    executar_query(tx, query, professor)

def criar_no_grupo_tcc(tx, grupo_tcc):
    query = """
    MERGE (g:GrupoTCC {id_grupo: $id_grupo, tema: $tema})
    WITH g
    MATCH (p:Professor {id: $orientador})
    MERGE (g)-[:ORIENTADO_POR]->(p)
    """
    executar_query(tx, query, grupo_tcc)

def gerar_nome_aleatorio():
    return fake.name()

def gerar_disciplina_aleatoria_para_curso(curso_nome):
    disciplinas = cursos_e_disciplinas.get(curso_nome, ["Disciplina Genérica"])
    codigo = f"DISC{random.randint(100, 999)}"
    semestre = random.randint(1, 2)
    ano = random.randint(2020, 2025)
    nota_final = round(random.uniform(4, 10), 2)
    situacao = "Aprovado" if nota_final >= 5.0 else "Reprovado"
    return Disciplina(
        codigo_disciplina=codigo,
        nome=random.choice(disciplinas),
        semestre=semestre,
        ano=ano,
        nota_final=nota_final,
        situacao=situacao
    )

def gerar_curso(nome_curso):
    id_curso = random.randint(1, 1000)
    curso = Curso(
        id_curso=id_curso,
        nome=nome_curso,
        nome_departamento=departamentos[nome_curso]
    )
    with neo4j_driver.session() as session:
        session.write_transaction(criar_no_curso, curso.dict())
    return curso

def gerar_aluno_aleatorio():
    nome_curso = random.choice(list(cursos_e_disciplinas.keys()))
    curso = gerar_curso(nome_curso)
    disciplinas = [gerar_disciplina_aleatoria_para_curso(nome_curso) for _ in range(5)]
    aluno = Aluno(
        ra=random.randint(1000000, 9999999),
        nome=gerar_nome_aleatorio(),
        email=fake.email(),
        telefone=fake.phone_number(),
        curso=curso,
        disciplinas=disciplinas,
        formado=random.choice([True, False])
    )
    with neo4j_driver.session() as session:
        session.write_transaction(criar_no_aluno, aluno)
    return aluno

def gerar_professor_aleatorio():
    nome_curso = random.choice(list(cursos_e_disciplinas.keys()))
    professor = Professor(
        id=random.randint(1, 100),
        nome=gerar_nome_aleatorio(),
        email=fake.email(),
        telefone=fake.phone_number(),
        salario=round(random.uniform(3000, 15000), 2),
        departamento=departamentos[nome_curso],
        chefe_departamento=random.choice([True, False])
    )
    with neo4j_driver.session() as session:
        session.write_transaction(criar_no_professor, professor.dict())
    return professor

def gerar_grupo_tcc_aleatorio():
    id_grupo = random.randint(1, 1000)
    tema = f"Tema do TCC {id_grupo}"
    orientador = random.randint(1, 100)
    grupo_tcc = GrupoTCC(
        id_grupo=id_grupo,
        tema=tema,
        orientador=orientador,
        alunos=[]
    )
    with neo4j_driver.session() as session:
        session.write_transaction(criar_no_grupo_tcc, grupo_tcc.dict())
    return grupo_tcc

for nome_curso in cursos_e_disciplinas.keys():
    gerar_curso(nome_curso)

for _ in range(10):
    gerar_aluno_aleatorio()

for _ in range(5):
    gerar_professor_aleatorio()

for _ in range(3):
    gerar_grupo_tcc_aleatorio()

print("Dados inseridos com sucesso no Neo4j!")

neo4j_driver.close()
