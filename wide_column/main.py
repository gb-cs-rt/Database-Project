from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from pydantic import BaseModel, Field
from typing import List, Optional
import random
from faker import Faker

fake = Faker('pt_BR')

# Conectar ao Cassandra
cluster = Cluster(['localhost'])  # Ajuste o IP/porta se necessário
session = cluster.connect()

# Criar o keyspace (esquema)
session.execute("""
    CREATE KEYSPACE IF NOT EXISTS universidade
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
""")

# Selecionar o keyspace
session.set_keyspace('universidade')

# Criar tabelas
session.execute("""
    CREATE TABLE IF NOT EXISTS students (
        ra int PRIMARY KEY,
        nome text,
        email text,
        telefone text,
        id_curso int,
        disciplinas list<frozen<map<text, text>>>,
        formado boolean
    )
""")

session.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id_curso int PRIMARY KEY,
        nome text,
        nome_departamento text
    )
""")

session.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        id int PRIMARY KEY,
        nome text,
        email text,
        telefone text,
        salario float,
        departamento text,
        chefe_departamento boolean
    )
""")

session.execute("""
    CREATE TABLE IF NOT EXISTS grupos_tcc (
        id_grupo int PRIMARY KEY,
        tema text,
        orientador int,
        alunos list<int>
    )
""")

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

class Curso(BaseModel):
    id_curso: int
    nome: str = Field(max_length=100)
    nome_departamento: str = Field(max_length=100)

class Disciplina(BaseModel):
    codigo_disciplina: str = Field(max_length=100)
    nome: str = Field(max_length=100)
    semestre: int
    ano: int
    nota_final: float
    situacao: str

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

def gerar_curso(nome_curso):
    id_curso = random.randint(1, 1000)
    curso = Curso(
        id_curso=id_curso,
        nome=nome_curso,
        nome_departamento=departamentos[nome_curso]
    )
    session.execute("""
        INSERT INTO courses (id_curso, nome, nome_departamento) 
        VALUES (%s, %s, %s)
    """, (curso.id_curso, curso.nome, curso.nome_departamento))
    return curso

def gerar_disciplina_aleatoria_para_curso(curso_nome):
    disciplinas = cursos_e_disciplinas.get(curso_nome, ["Disciplina Genérica"])
    return Disciplina(
        codigo_disciplina=f"DISC{random.randint(100, 999)}",
        nome=random.choice(disciplinas),
        semestre=random.randint(1, 2),
        ano=random.randint(2020, 2025),
        nota_final=round(random.uniform(4, 10), 2),
        situacao="Aprovado" if random.uniform(4, 10) >= 5 else "Reprovado"
    )

def gerar_aluno_aleatorio():
    nome_curso = random.choice(list(cursos_e_disciplinas.keys()))
    curso = gerar_curso(nome_curso)
    disciplinas = [gerar_disciplina_aleatoria_para_curso(nome_curso) for _ in range(5)]
    aluno = Aluno(
        ra=random.randint(1000000, 9999999),
        nome=fake.name(),
        email=fake.email(),
        telefone=fake.phone_number(),
        curso=curso,
        disciplinas=[d.dict() for d in disciplinas],
        formado=random.choice([True, False])
    )
    session.execute("""
        INSERT INTO students (ra, nome, email, telefone, id_curso, disciplinas, formado) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (aluno.ra, aluno.nome, aluno.email, aluno.telefone, aluno.curso.id_curso, aluno.disciplinas, aluno.formado))
    return aluno

def gerar_professor_aleatorio():
    nome_curso = random.choice(list(cursos_e_disciplinas.keys()))
    professor = Professor(
        id=random.randint(1, 100),
        nome=fake.name(),
        email=fake.email(),
        telefone=fake.phone_number(),
        salario=round(random.uniform(3000, 15000), 2),
        departamento=departamentos[nome_curso],
        chefe_departamento=random.choice([True, False])
    )
    session.execute("""
        INSERT INTO teachers (id, nome, email, telefone, salario, departamento, chefe_departamento) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (professor.id, professor.nome, professor.email, professor.telefone, professor.salario, professor.departamento, professor.chefe_departamento))
    return professor

print("Dados inseridos com sucesso!")
