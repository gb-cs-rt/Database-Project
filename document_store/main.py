from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
import random
from pymongo import MongoClient

# Conectar ao MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['universidade']

# Coleções
alunos_collection = db['students']
professores_collection = db['teachers']
cursos_collection = db['courses']

# Cursos e disciplinas
cursos_e_disciplinas = {
    "Engenharia de Software": ["Estruturas de Dados", "Sistemas Operacionais", "Programação", "Banco de Dados", "Algoritmos"],
    "Administração": ["Gestão de Pessoas", "Finanças Corporativas", "Marketing", "Economia", "Contabilidade"],
    "Direito": ["Introdução ao Direito", "Direito Penal", "Direito Civil", "Direito Empresarial", "Direito Constitucional"]
}

departamentos = {
    "Engenharia de Software": "Departamento de Computação",
    "Administração": "Departamento de Negócios",
    "Direito": "Departamento de Ciências Jurídicas"
}

# Classe Disciplina
class Disciplina(BaseModel):
    codigo: str
    nome: str
    semestre: str
    nota_final: float
    situacao: str

# Classe TCC
class Tcc(BaseModel):
    tema: Optional[str]
    orientador: Optional[str]
    grupo: Optional[List[str]]

# Classe Curso
class Curso(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    nome: str
    matriz_curricular: List[Disciplina]

# Classe Aluno
class Aluno(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    nome: str
    matricula: str
    curso: Curso
    disciplinas: List[Disciplina]
    formado: bool
    tcc: Optional[Tcc] = None

# Classe Professor
class Professor(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    nome: str
    departamento: str
    disciplinas: List[Disciplina]
    chefe_departamento: bool
    tccs_orientados: List[Tcc] = []

# Função para gerar nomes aleatórios
def gerar_nome_aleatorio():
    nomes = ["Ana", "João", "Carlos", "Mariana", "Pedro", "Julia", "Felipe", "Fernanda"]
    sobrenomes = ["Silva", "Santos", "Martins", "Oliveira", "Souza", "Pereira", "Lima", "Costa"]
    return f"{random.choice(nomes)} {random.choice(sobrenomes)}"

# Função para gerar uma disciplina aleatória
def gerar_disciplina_aleatoria_para_curso(curso_nome):
    disciplinas = cursos_e_disciplinas.get(curso_nome, ["Disciplina Genérica"])
    codigo = "DISC" + str(random.randint(100, 999))
    semestre = f"{random.randint(2020, 2025)}-{random.randint(1, 2)}"
    nota_final = round(random.uniform(4, 10), 2)
    return Disciplina(
        codigo=codigo,
        nome=random.choice(disciplinas),
        semestre=semestre,
        nota_final=nota_final,
        situacao="Aprovado" if nota_final >= 5.0 else "Reprovado"
    )

# Função para gerar um curso
def gerar_curso(nome_curso):
    disciplinas = [gerar_disciplina_aleatoria_para_curso(nome_curso) for _ in range(5)]
    curso = Curso(nome=nome_curso, matriz_curricular=disciplinas)
    cursos_collection.insert_one(curso.dict(by_alias=True))  # Armazena no MongoDB
    return curso

# Função para gerar um aluno aleatório com um curso
def gerar_aluno_aleatorio():
    nome_curso = random.choice(list(cursos_e_disciplinas.keys()))
    curso = cursos_collection.find_one({"nome": nome_curso}) or gerar_curso(nome_curso)

    disciplinas = [gerar_disciplina_aleatoria_para_curso(nome_curso) for _ in range(random.randint(4, 8))]
    tcc = Tcc(
        tema=f"TCC sobre {random.choice(cursos_e_disciplinas[nome_curso])}",
        orientador=gerar_nome_aleatorio(),
        grupo=[gerar_nome_aleatorio() for _ in range(random.randint(2, 4))]
    )

    return Aluno(
        nome=gerar_nome_aleatorio(),
        matricula=str(random.randint(1000000, 9999999)),
        curso=Curso(**curso),
        disciplinas=disciplinas,
        formado=random.choice([True, False]),
        tcc=tcc
    )

# Função para gerar um professor aleatório
def gerar_professor_aleatorio():
    nome_curso = random.choice(list(cursos_e_disciplinas.keys()))
    disciplinas = [gerar_disciplina_aleatoria_para_curso(nome_curso) for _ in range(random.randint(2, 4))]
    tccs_orientados = [Tcc(
        tema=f"TCC sobre {random.choice(cursos_e_disciplinas[nome_curso])}",
        orientador=gerar_nome_aleatorio(),
        grupo=[gerar_nome_aleatorio() for _ in range(random.randint(2, 4))]
    ) for _ in range(random.randint(1, 3))]

    return Professor(
        nome=gerar_nome_aleatorio(),
        departamento=departamentos[nome_curso],
        disciplinas=disciplinas,
        chefe_departamento=random.choice([True, False]),
        tccs_orientados=tccs_orientados
    )

# Inserir cursos no MongoDB
for nome_curso in cursos_e_disciplinas.keys():
    gerar_curso(nome_curso)

# Inserir alunos no MongoDB
for _ in range(10):
    aluno = gerar_aluno_aleatorio()
    alunos_collection.insert_one(aluno.dict(by_alias=True))

# Inserir professores no MongoDB
for _ in range(5):
    professor = gerar_professor_aleatorio()
    professores_collection.insert_one(professor.dict(by_alias=True))

print("Dados inseridos com sucesso!")
