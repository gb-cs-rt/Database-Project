from pymongo import MongoClient
import json
import os
import random
from faker import Faker

def read_sql_data(table):
    with open(f"../../sql/sql_data/{table}.json", "r", encoding="utf-8") as f:
        return json.load(f)

def insert_mongodb_data():

    # Muda o diretório para o diretório do arquivo
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Lê os dados dos arquivos JSON
    alunos = read_sql_data("aluno")
    cursa = read_sql_data("cursa")
    cursos = read_sql_data("curso")
    matrizes_curriculares = read_sql_data("matrizcurricular")
    departamentos = read_sql_data("departamento")
    chefes_departamento = read_sql_data("chefedepartamento")
    disciplinas = read_sql_data("disciplina")
    professores = read_sql_data("professor")
    leciona = read_sql_data("leciona")
    grupos_tcc = read_sql_data("grupotcc")

    # Cria a conexão com o MongoDB
    try:
        client = MongoClient("mongodb://localhost:27017/")
    except Exception as e:
        print("Erro ao conectar ao MongoDB:", e)
        return
    
    db = client['university']

    # Deleta as coleções existentes
    collections_to_drop = [
        "departamento", "professor", "curso", 
        "aluno", "disciplina"
    ]
    for collection in collections_to_drop:
        db[collection].drop()

    # Insere os departamentos
    db.departamento.insert_many(departamentos)

    # Insere as disciplinas
    db.disciplina.insert_many(disciplinas)

    # Insere os cursos
    disciplina_dict = list(db.disciplina.find({}))

    # Insere os professores
    profs_to_insert = []
    for professor in professores:

        leciona_to_insert = []
        for leciona_entry in leciona:
            if leciona_entry["id_professor"] == professor["id"]:
                
                disciplina_object = next(filter(lambda x: x["codigo_disciplina"] == leciona_entry["codigo_disciplina"], disciplina_dict))
                disciplina_object_id = disciplina_object["_id"]

                leciona_to_insert.append({
                    "id_curso": leciona_entry["id_curso"],
                    "id_disciplina": disciplina_object_id,
                    "codigo_disciplina": disciplina_object["codigo_disciplina"],
                    "semestre": leciona_entry["semestre"],
                    "ano": leciona_entry["ano"],
                    "carga_horaria": leciona_entry["carga_horaria"]
                })

        grupos_to_insert = []
        for grupo in grupos_tcc:
            if grupo["id_professor"] == professor["id"]:
                grupos_to_insert.append(grupo["id_grupo"])

        prof_to_insert = {
            "id": professor["id"],
            "nome": professor["nome"],
            "nome_departamento": professor["nome_departamento"],
            "email": professor["email"],
            "telefone": professor["telefone"],
            "salario": professor["salario"],
            "grupos_tcc": grupos_to_insert,
            "leciona": leciona_to_insert
        }

        profs_to_insert.append(prof_to_insert)

    db.professor.insert_many(profs_to_insert)

    # Insere os chefes de departamento
    professor_dict = list(db.professor.find({}))

    for departamento in departamentos:
        for chefe_departamento in chefes_departamento:

            if chefe_departamento["nome_departamento"] == departamento["nome_departamento"]:

                chefe_object = next(filter(lambda x: x["id"] == chefe_departamento["id_professor"], professor_dict))
                chefe_object_id = chefe_object["_id"]

                db.departamento.update_one(
                    {"nome_departamento": departamento["nome_departamento"]},
                    {"$set": {"chefe": chefe_object_id}}
                )

                db.professor.update_one(
                    {"_id": chefe_object_id},
                    {"$set": {"chefe_departamento": departamento["nome_departamento"]}}
                )

    cursos_to_insert = []
    for curso in cursos:

        matriz_curricular = []
        for matriz in matrizes_curriculares:
            if matriz["id_curso"] == curso["id_curso"]:
                
                disciplina_object = next(filter(lambda x: x["codigo_disciplina"] == matriz["codigo_disciplina"], disciplina_dict))
                disciplina_object_id = disciplina_object["_id"]

                matriz_curricular.append({
                    "id_disciplina": disciplina_object_id,
                    "codigo_disciplina": disciplina_object["codigo_disciplina"]
                })

        curso_to_insert = {
            "id_curso": curso["id_curso"],
            "nome_departamento": curso["nome_departamento"],
            "nome": curso["nome"],
            "horas_complementares": curso["horas_complementares"],
            "faltas": curso["faltas"],
            "matriz_curricular": matriz_curricular
        }
        
        cursos_to_insert.append(curso_to_insert)
        
    db.curso.insert_many(cursos_to_insert)

    # Insere os alunos

    alunos_to_insert = []
    for aluno in alunos:
            
        cursa_to_insert = []
        for cursa_entry in cursa:
            if cursa_entry["id_aluno"] == aluno["ra"]:
                
                disciplina_object = next(filter(lambda x: x["codigo_disciplina"] == cursa_entry["codigo_disciplina"], disciplina_dict))
                disciplina_object_id = disciplina_object["_id"]

                cursa_to_insert.append({
                    "id_disciplina": disciplina_object_id,
                    "codigo_disciplina": disciplina_object["codigo_disciplina"],
                    "semestre": int(cursa_entry["semestre"]),
                    "ano": int(cursa_entry["ano"]),
                    "media": float(cursa_entry["media"]),
                    "faltas": int(cursa_entry["faltas"])
                })
        
        grupo_tcc = None
        for grupo in grupos_tcc:
            if aluno["ra"] == grupo["ra"]:
                grupo_tcc = grupo["id_grupo"]

        aluno_to_insert = {
            "ra": aluno["ra"],
            "id_curso": aluno["id_curso"],
            "nome": aluno["nome"],
            "email": aluno["email"],
            "telefone": aluno["telefone"],
            "grupo_tcc": grupo_tcc,
            "cursa": cursa_to_insert
        }

        alunos_to_insert.append(aluno_to_insert)

    db.aluno.insert_many(alunos_to_insert)

    print("Dados inseridos no MongoDB com sucesso!")

def insert_new_mongodb_data():

    fake = Faker("pt_BR")

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    alunos = read_sql_data("aluno")
    cursa = read_sql_data("cursa")
    cursos = read_sql_data("curso")
    matriz_curricular = read_sql_data("matrizcurricular")
    departamentos = read_sql_data("departamento")
    chefe_departamento = read_sql_data("chefedepartamento")
    disciplinas = read_sql_data("disciplina")
    professores = read_sql_data("professor")
    leciona = read_sql_data("leciona")
    grupos_tcc = read_sql_data("grupotcc")

    try:
        client = MongoClient("mongodb://localhost:27017/")
    except Exception as e:
        print("Erro ao conectar ao MongoDB:", e)
        return
    
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