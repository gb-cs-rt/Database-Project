from pymongo import MongoClient
from faker import Faker
import random

fake = Faker("pt_BR")

client = MongoClient("mongodb://localhost:27017/")
db = client['university']

collections_to_drop = [
    "departamento", "professor", "curso", 
    "aluno", "disciplina"
]
for collection in collections_to_drop:
    db[collection].drop()

departamentos = ['Ciência da Computação', 'Engenharia Elétrica', 'Engenharia Mecânica', 'Engenharia de Robôs']
departamento_docs = [{"nome_departamento": dep} for dep in departamentos]
departamento_ids = db.departamento.insert_many(departamento_docs).inserted_ids

professores = []
prof_ra = 1
for _ in range(40):
    nome_dep = random.choice(departamentos)
    professores.append({
        "ra": prof_ra,
        "nome_departamento": nome_dep,
        "nome": fake.name(),
        "email": fake.email(),
        "telefone": fake.phone_number(),
        "salario": round(random.uniform(3000, 10000), 2),
        "grupos_tcc": []
    })
    prof_ra += 1

professor_ids = db.professor.insert_many(professores).inserted_ids
professores_dict = {prof["_id"]: prof for prof in db.professor.find()}
professores_list = list(professores_dict.keys())

for dep in departamentos:
    id_professor = random.choice(professores_list)
    db.professor.update_one({"_id": id_professor}, {"$set": {"chefe_departamento": dep}})
    db.departamento.update_one({"nome_departamento": dep}, {"$set": {"chefe": id_professor}})

cursos = []
for dep in departamentos:
    curso = {
        "nome_departamento": dep,
        "nome": dep,
        "horas_complementares": random.randint(180, 320),
        "faltas": random.randint(10, 20),
        "matriz_curricular": []
    }
    cursos.append(curso)

curso_ids = db.curso.insert_many(cursos).inserted_ids
cursos_dict = {curso["_id"]: curso for curso in db.curso.find()}

alunos = []
ra_counter = 1
for _ in range(100):
    id_curso = random.choice(list(cursos_dict.keys()))
    aluno = {
        "ra": ra_counter,
        "id_curso": id_curso,
        "nome": fake.name(),
        "email": fake.email(),
        "telefone": fake.phone_number(),
        "grupo_tcc": None
    }
    alunos.append(aluno)
    ra_counter += 1

aluno_ids = db.aluno.insert_many(alunos).inserted_ids
alunos_dict = {aluno["_id"]: aluno for aluno in db.aluno.find()}

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

disciplinas_dict = {disc["codigo_disciplina"]: disc for disc in db.disciplina.find()}

for curso in db.curso.find():
    disciplinas_matriz = random.sample(list(disciplinas_dict.values()), k=random.randint(3, 8))
    matriz_curricular = []
    for disciplina in disciplinas_matriz:
        matriz_curricular.append({
            "codigo_disciplina": disciplina["codigo_disciplina"],
            "id_disciplina": disciplina["_id"]
        })
    db.curso.update_one(
        {"_id": curso["_id"]},
        {"$set": {"matriz_curricular": matriz_curricular}}
    )

for aluno in db.aluno.find():
    id_curso = aluno["id_curso"]
    disciplinas_matriz = list(db.curso.find_one({"_id": id_curso})["matriz_curricular"])
    cursa = []
    for disciplina_entry in disciplinas_matriz:
        disciplina = disciplinas_dict.get(disciplina_entry["codigo_disciplina"])
        cursa.append({
            "codigo_disciplina": disciplina["codigo_disciplina"],
            "id_disciplina": disciplina["_id"],
            "semestre": random.randint(1, 2),
            "ano": random.randint(2019, 2024),
            "media": round(random.uniform(0, 10) if random.random() < 0.3 else random.uniform(5, 10), 2),
            "faltas": random.randint(0, 10)
        })
    db.aluno.update_one({"_id": aluno["_id"]}, {"$set": {"cursa": cursa}})

qtd_grupos = round(len(alunos) / 3)
qtd_alunos_por_grupo = 3
grupos_tcc = []

alunos_list = list(alunos_dict.keys())

for i in range(qtd_grupos):
    id_grupo = i + 1
    id_professor = random.choice(list(professores_dict.keys()))
    grupo_members = []
    for _ in range(qtd_alunos_por_grupo):
        ra = alunos_list.pop(random.randint(0, len(alunos_list) - 1))
        grupo_members.append(ra)
        db.aluno.update_one({"_id": ra}, {"$set": {"grupo_tcc": id_grupo}})
    db.professor.update_one({"_id": id_professor}, {"$push": {"grupos_tcc": id_grupo}})
    grupos_tcc.append({
        "id_grupo": id_grupo,
        "id_professor": id_professor,
        "members": grupo_members
    })

for _ in range(80):
    id_professor = random.choice(list(professores_dict.keys()))
    id_curso = random.choice(list(cursos_dict.keys()))
    disciplina = random.choice(list(disciplinas_dict.values()))
    leciona_entry = {
        "id_curso": id_curso,
        "codigo_disciplina": disciplina["codigo_disciplina"],
        "id_disciplina": disciplina["_id"],
        "semestre": random.randint(1, 2),
        "ano": random.randint(2019, 2024),
        "carga_horaria": random.randint(30, 60)
    }

    db.professor.update_one(
        {"_id": id_professor},
        {"$push": {"leciona": leciona_entry}}
    )

print("Database and tables created, and data inserted successfully!")