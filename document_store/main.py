from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
import random
from pymongo import MongoClient
from faker import Faker

fake = Faker('pt_BR')

# Conectar ao MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['universidade']

db.drop_database('universidade')
# Coleções
alunos_collection = db['students']
professores_collection = db['teachers']
cursos_collection = db['courses']
grupos_tcc_collection = db['grupos_tcc']

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
    cursos_collection.insert_one(curso.dict())
    return curso

def gerar_aluno_aleatorio():
    nome_curso = random.choice(list(cursos_e_disciplinas.keys()))
    curso = cursos_collection.find_one({"nome": nome_curso}) or gerar_curso(nome_curso)
    disciplinas = [gerar_disciplina_aleatoria_para_curso(nome_curso) for _ in range(5)]
    aluno = Aluno(
        ra=random.randint(1000000, 9999999),
        nome=gerar_nome_aleatorio(),
        email=fake.email(),
        telefone=fake.phone_number(),
        curso=Curso(**curso),
        disciplinas=disciplinas,
        formado=random.choice([True, False])
    )
    alunos_collection.insert_one(aluno.dict())
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
    professores_collection.insert_one(professor.dict())
    return professor

def gerar_grupo_tcc_aleatorio():
    id_grupo = random.randint(1, 1000)
    tema = f"Tema do TCC {id_grupo}"
    orientador = professores_collection.find_one({}, {"id": 1})["id"]
    alunos = alunos_collection.aggregate([{"$sample": {"size": 3}}])
    alunos_ra = [aluno["ra"] for aluno in alunos]

    grupo_tcc = GrupoTCC(
        id_grupo=id_grupo,
        tema=tema,
        orientador=orientador,
        alunos=alunos_ra
    )
    grupos_tcc_collection.insert_one(grupo_tcc.dict())
    return grupo_tcc

def consultar_grupo_tcc(id_grupo):
    grupo = grupos_tcc_collection.find_one({"id_grupo": id_grupo})
    orientador = professores_collection.find_one(
        {"id": grupo["orientador"]}, {"_id": 0, "nome": 1}
    )
    alunos = alunos_collection.find(
        {"ra": {"$in": grupo["alunos"]}}, {"_id": 0, "nome": 1, "ra": 1}
    )
    return {
        "id_grupo": grupo["id_grupo"],
        "tema": grupo["tema"],
        "orientador": orientador["nome"],
        "alunos": list(alunos)
    }

def consultar_grupos_por_professor(id_professor):
    grupos = grupos_tcc_collection.find({"orientador": id_professor}, {"_id": 0, "id_grupo": 1, "tema": 1})
    return list(grupos)

def consultar_alunos_grupo_tcc(id_grupo):
    grupo = grupos_tcc_collection.find_one({"id_grupo": id_grupo})
    alunos = alunos_collection.find(
        {"ra": {"$in": grupo["alunos"]}}, {"_id": 0, "nome": 1, "email": 1, "telefone": 1}
    )
    return list(alunos)

# Inserir dados no MongoDB
for nome_curso in cursos_e_disciplinas.keys():
    gerar_curso(nome_curso)

for _ in range(10):
    gerar_aluno_aleatorio()

for _ in range(5):
    gerar_professor_aleatorio()

for _ in range(3):
    gerar_grupo_tcc_aleatorio()

print("Dados inseridos com sucesso!")
