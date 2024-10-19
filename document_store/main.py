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

# Coleções
alunos_collection = db['students']
professores_collection = db['teachers']
cursos_collection = db['courses']

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
    codigo_disciplina: str = Field(max_length=6)
    nome: str = Field(max_length=40)
    semestre: str
    nota_final: float
    situacao: str

class Curso(BaseModel):
    id_curso: int
    nome: str = Field(max_length=30)
    nome_departamento: str = Field(max_length=30)

class Aluno(BaseModel):
    ra: int
    nome: str = Field(max_length=50)
    email: str = Field(max_length=50)
    telefone: Optional[str] = Field(max_length=20, default=None)
    curso: Curso
    disciplinas: List[Disciplina]
    formado: bool

class Professor(BaseModel):
    id: int
    nome: str = Field(max_length=50)
    email: str = Field(max_length=50)
    telefone: Optional[str] = Field(max_length=20)
    salario: float
    departamento: str
    chefe_departamento: bool

class Tcc(BaseModel):
    tema: str
    orientador: str
    grupo: List[str]

def gerar_nome_aleatorio():
    return fake.name()

def gerar_disciplina_aleatoria_para_curso(curso_nome):
    disciplinas = cursos_e_disciplinas.get(curso_nome, ["Disciplina Genérica"])
    codigo = f"DISC{random.randint(100, 999)}"
    semestre = f"{random.randint(2020, 2025)}-{random.randint(1, 2)}"
    nota_final = round(random.uniform(4, 10), 2)
    situacao = "Aprovado" if nota_final >= 5.0 else "Reprovado"
    return Disciplina(
        codigo_disciplina=codigo,
        nome=random.choice(disciplinas),
        semestre=semestre,
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

def historico_escolar_aluno(ra):
    historico = alunos_collection.find_one(
        {"ra": ra},
        {"_id": 0, "disciplinas.codigo_disciplina": 1, "disciplinas.nome": 1,
         "disciplinas.semestre": 1, "disciplinas.nota_final": 1}
    )
    return historico

def disciplinas_ministradas_por_professor(nome_professor):
    professor = professores_collection.find_one(
        {"nome": nome_professor},
        {"_id": 0, "disciplinas.semestre": 1, "disciplinas.nome": 1}
    )
    return professor

def alunos_formados_por_semestre(ano, semestre):
    alunos = alunos_collection.find(
        {
            "formado": True,
            "disciplinas": {"$elemMatch": {"semestre": f"{ano}-{semestre}"}}
        },
        {"_id": 0, "nome": 1, "ra": 1}
    )
    return list(alunos)

def professores_chefes_departamento():
    chefes = professores_collection.find(
        {"chefe_departamento": True},
        {"_id": 0, "nome": 1, "departamento": 1}
    )
    return list(chefes)

# Inserir dados no MongoDB
for nome_curso in cursos_e_disciplinas.keys():
    gerar_curso(nome_curso)

for _ in range(10):
    gerar_aluno_aleatorio()

for _ in range(5):
    gerar_professor_aleatorio()

print("Dados inseridos com sucesso!")

# Consultas de exemplo
print(historico_escolar_aluno(1234567))
print(disciplinas_ministradas_por_professor("Carlos Silva"))
print(alunos_formados_por_semestre(2023, 1))
print(professores_chefes_departamento())
