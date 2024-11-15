from pymongo import MongoClient
import json
import os

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
        
        # Insere as entradas de leciona
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

        # Insere as entradas de grupos_tcc
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

    # Insere os cursos
    cursos_to_insert = []
    for curso in cursos:

        # Insere as entradas de matriz_curricular
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
        
        # Insere as entradas de cursa
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
        
        # Insere as entradas de grupos_tcc
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