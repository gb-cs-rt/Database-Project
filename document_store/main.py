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

# Cursos, disciplinas e departamentos realistas
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

# Classe que representa a Disciplina
class Disciplina(BaseModel):
    codigo: str
    nome: str
    semestre: str
    nota_final: float
    situacao: str

# Classe que representa o TCC do aluno
class Tcc(BaseModel):
    tema: Optional[str]
    orientador: Optional[str]
    grupo: Optional[List[str]]

# Classe que representa o Aluno
class Aluno(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    nome: str
    matricula: str
    curso: str
    disciplinas: List[Disciplina]
    formado: bool
    tcc: Optional[Tcc] = None

# Classe que representa o Professor
class Professor(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    nome: str
    departamento: str
    disciplinas: List[Disciplina]
    chefe_departamento: bool

# Função para gerar nomes aleatórios
def gerar_nome_aleatorio():
    nomes = ["Ana", "João", "Carlos", "Mariana", "Pedro", "Julia", "Felipe", "Fernanda"]
    sobrenomes = ["Silva", "Santos", "Martins", "Oliveira", "Souza", "Pereira", "Lima", "Costa"]
    return f"{random.choice(nomes)} {random.choice(sobrenomes)}"

# Função para gerar uma disciplina aleatória de um curso específico
def gerar_disciplina_aleatoria_para_curso(curso):
    disciplinas = cursos_e_disciplinas.get(curso, ["Disciplina Genérica"])
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

# Função para gerar um aluno aleatório com disciplinas e TCC
def gerar_aluno_aleatorio():
    curso = random.choice(list(cursos_e_disciplinas.keys()))
    disciplinas = [gerar_disciplina_aleatoria_para_curso(curso) for _ in range(random.randint(4, 8))]
    
    if random.choice([True, False]):
        tcc = Tcc(
            tema=f"TCC sobre {random.choice(cursos_e_disciplinas[curso])}",
            orientador=gerar_nome_aleatorio(),
            grupo=[gerar_nome_aleatorio() for _ in range(random.randint(2, 4))]
        )
    else:
        tcc = None

    return Aluno(
        nome=gerar_nome_aleatorio(),
        matricula=str(random.randint(1000000, 9999999)),
        curso=curso,
        disciplinas=disciplinas,
        formado=random.choice([True, False]),
        tcc=tcc
    )

# Função para gerar um professor aleatório com disciplinas
def gerar_professor_aleatorio():
    curso = random.choice(list(cursos_e_disciplinas.keys()))
    disciplinas = [gerar_disciplina_aleatoria_para_curso(curso) for _ in range(random.randint(2, 4))]
    
    return Professor(
        nome=gerar_nome_aleatorio(),
        departamento=departamentos[curso],
        disciplinas=disciplinas,
        chefe_departamento=random.choice([True, False])
    )

# Função para histórico escolar de um aluno
def historico_escolar_aluno(matricula):
    aluno = alunos_collection.find_one({"matricula": matricula}, {"disciplinas": 1, "nome": 1, "curso": 1, "_id": 0})
    if aluno:
        print(f"Histórico escolar de {aluno['nome']} no curso de {aluno['curso']}:")
        for disciplina in aluno['disciplinas']:
            print(f"Código: {disciplina['codigo']}, Nome: {disciplina['nome']}, Semestre: {disciplina['semestre']}, Nota Final: {disciplina['nota_final']}, Status: {disciplina['situacao']}")
    else:
        print("Aluno não encontrado.")

# Função para histórico de disciplinas ministradas por um professor
def historico_disciplinas_professor(nome_professor):
    professor = professores_collection.find_one({"nome": nome_professor}, {"disciplinas": 1, "nome": 1, "_id": 0})
    if professor:
        print(f"Disciplinas ministradas por {professor['nome']}:")
        for disciplina in professor['disciplinas']:
            print(f"Código: {disciplina['codigo']}, Nome: {disciplina['nome']}, Semestre: {disciplina['semestre']}")
    else:
        print("Professor não encontrado.")

# Função para listar alunos que se formaram em um determinado semestre
def listar_alunos_formados(semestre):
    formados = alunos_collection.find({"formado": True, "disciplinas.semestre": semestre}, {"nome": 1, "matricula": 1, "_id": 0})
    print(f"Alunos formados no semestre {semestre}:")
    for aluno in formados:
        print(f"Nome: {aluno['nome']}, Matrícula: {aluno['matricula']}")

# Função para listar professores que são chefes de departamento
def listar_chefes_departamento():
    chefes = professores_collection.find({"chefe_departamento": True}, {"nome": 1, "departamento": 1, "_id": 0})
    print("Professores que são chefes de departamento:")
    for chefe in chefes:
        print(f"Nome: {chefe['nome']}, Departamento: {chefe['departamento']}")

# Função para listar alunos que formaram um grupo de TCC e seus orientadores
def listar_grupos_tcc():
    alunos_com_tcc = alunos_collection.find({"tcc": {"$exists": True}}, {"nome": 1, "tcc": 1, "_id": 0})
    print("Grupos de TCC e seus orientadores:")
    for aluno in alunos_com_tcc:
        tcc = aluno.get('tcc', None)
        if tcc:
            tema = tcc.get('tema', 'Tema não definido')
            orientador = tcc.get('orientador', 'Orientador não definido')
            grupo = tcc.get('grupo', [])
            grupo_str = ', '.join(grupo) if grupo else 'Grupo não definido'
        else:
            tema = 'Tema não definido'
            orientador = 'Orientador não definido'
            grupo_str = 'Grupo não definido'
        
        print(f"Aluno: {aluno['nome']}, Tema: {tema}, Orientador: {orientador}, Grupo: {grupo_str}")

# Inserir alunos aleatórios melhorados no MongoDB
for _ in range(10):  # Insere 10 alunos
    aluno = gerar_aluno_aleatorio()
    alunos_collection.insert_one(aluno.dict(by_alias=True))  # Converte o objeto para dicionário

# Inserir professores aleatórios melhorados no MongoDB
for _ in range(5):  # Insere 5 professores
    professor = gerar_professor_aleatorio()
    professores_collection.insert_one(professor.dict(by_alias=True))  # Converte o objeto para dicionário

print("Dados aleatórios realistas inseridos com sucesso!")

# Exemplos de uso das consultas:
historico_escolar_aluno("202312345")
historico_disciplinas_professor("Ana Silva")
listar_alunos_formados("2024-1")
listar_chefes_departamento()
listar_grupos_tcc()

