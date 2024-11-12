from pymongo import MongoClient
from faker import Faker
import random

# Initialize Faker for generating random data
fake = Faker("pt_BR")

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['university']

# Clear existing collections (drop collections if they exist)
collections_to_drop = [
    "departamento", "professor", "curso", 
    "aluno", "disciplina"
]
for collection in collections_to_drop:
    db[collection].drop()

# Insert data into Departamento
departamentos = ['Ciência da Computação', 'Engenharia Elétrica', 'Engenharia Mecânica', 'Engenharia de Robôs']
departamento_docs = [{"nome_departamento": dep} for dep in departamentos]
departamento_ids = db.departamento.insert_many(departamento_docs).inserted_ids

# Insert data into Professor with embedded "GrupoTCC" and optional "Chefe" field
professores = []
for _ in range(40):
    nome_dep = random.choice(departamentos)
    professores.append({
        "nome_departamento": nome_dep,
        "nome": fake.name(),
        "email": fake.email(),
        "telefone": fake.phone_number(),
        "salario": round(random.uniform(3000, 10000), 2),
        "grupos_tcc": []  # This will hold GrupoTCC information as a list of group IDs
    })
professores_ids = db.professor.insert_many(professores).inserted_ids

# Assign department leaders (ChefeDepartamento)
for dep_id, dep in zip(departamento_ids, departamentos):
    id_professor = random.choice(professores_ids)
    db.professor.update_one({"_id": id_professor}, {"$set": {"chefe_departamento": dep}})
    db.departamento.update_one({"nome_departamento": dep}, {"$set": {"chefe": id_professor}})

# Insert data into Curso with embedded MatrizCurricular
cursos = []
for dep in departamentos:
    curso = {
        "nome_departamento": dep,
        "nome": dep,
        "horas_complementares": random.randint(180, 320),
        "faltas": random.randint(10, 20),
        "matriz_curricular": []  # This will hold a list of subjects (Disciplina)
    }
    cursos.append(curso)
cursos_ids = db.curso.insert_many(cursos).inserted_ids

# Insert data into Aluno with "GrupoTCC" field
alunos = []
for _ in range(100):
    id_curso = random.choice(cursos_ids)
    aluno = {
        "id_curso": id_curso,
        "nome": fake.name(),
        "email": fake.email(),
        "telefone": fake.phone_number(),
        "grupo_tcc": None  # Will be populated later
    }
    alunos.append(aluno)
alunos_ids = db.aluno.insert_many(alunos).inserted_ids

# Insert data into Disciplina
disciplinas = ['Comunicação e Expressão', 'Cálculo I', 'Cálculo II', 'Cálculo III', 'Álgebra Linear', 'Física I', 
               'Física II', 'Física III', 'Química Geral', 'Química Orgânica', 'Programação I', 'Programação II', 
               'Programação III', 'Estrutura de Dados', 'Banco de Dados', 'Redes de Computadores', 
               'Sistemas Operacionais', 'Engenharia de Software', 'Inteligência Artificial', 'Computação Gráfica', 
               'Sistemas Distribuídos', 'Segurança da Informação', 'Empreendedorismo', 'Gestão de Projetos', 
               'Tópicos Especiais em Computação', 'Ética e Cidadania', 'Metodologia Científica', 
               'Trabalho de Conclusão de Curso']
disciplina_docs = []
for _ in range(len(disciplinas)):
    disciplina_docs.append({
        "codigo_disciplina": fake.unique.bothify(text='??###'),
        "nome_departamento": random.choice(departamentos),
        "nome": disciplinas.pop(random.randint(0, len(disciplinas) - 1)),
        "carga_horaria": random.randint(30, 180)
    })
disciplinas_inserted = db.disciplina.insert_many(disciplina_docs).inserted_ids

# Add disciplines to MatrizCurricular of courses
for curso in db.curso.find():
    disciplinas_matriz = random.sample(list(db.disciplina.find()), k=random.randint(3, 8))
    db.curso.update_one({"_id": curso["_id"]}, {"$set": {"matriz_curricular": [d["codigo_disciplina"] for d in disciplinas_matriz]}})

# Insert data into Cursa directly into Aluno collection
for aluno in db.aluno.find():
    id_curso = aluno["id_curso"]
    disciplinas_matriz = list(db.curso.find_one({"_id": id_curso})["matriz_curricular"])
    cursa = []
    for disciplina in disciplinas_matriz:
        cursa.append({
            "codigo_disciplina": disciplina,
            "semestre": random.randint(1, 2),
            "ano": random.randint(2019, 2024),
            "media": random.uniform(0, 10) if random.random() < 0.3 else random.uniform(5, 10),
            "faltas": random.randint(0, 10)
        })
    db.aluno.update_one({"_id": aluno["_id"]}, {"$set": {"cursa": cursa}})

# Assign GrupoTCC to Aluno and Professor
qtd_grupos = round(len(alunos) / 3)
qtd_alunos_por_grupo = 3
grupos_tcc = []
for i in range(qtd_grupos):
    id_grupo = i + 1
    id_professor = random.choice(professores_ids)
    grupo_members = []
    for _ in range(qtd_alunos_por_grupo):
        ra = alunos_ids.pop(random.randint(0, len(alunos_ids) - 1))
        grupo_members.append(ra)
        db.aluno.update_one({"_id": ra}, {"$set": {"grupo_tcc": id_grupo}})
    db.professor.update_one({"_id": id_professor}, {"$push": {"grupos_tcc": id_grupo}})
    grupos_tcc.append({
        "id_grupo": id_grupo,
        "id_professor": id_professor,
        "members": grupo_members
    })

# Insert data into Leciona and embed it in Professor collection
leciona_docs = []
for _ in range(80):
    id_professor = random.choice(professores_ids)
    id_curso = random.choice(cursos_ids)
    disciplina = random.choice(list(db.disciplina.find()))
    leciona_entry = {
        "id_curso": id_curso,
        "codigo_disciplina": disciplina["codigo_disciplina"],
        "semestre": random.randint(1, 2),
        "ano": random.randint(2019, 2024),
        "carga_horaria": random.randint(30, 60)
    }
    # Add this leciona entry to the corresponding Professor document
    db.professor.update_one(
        {"_id": id_professor},
        {"$push": {"leciona": leciona_entry}}
    )

print("MongoDB database and collections created with embedded relations!")