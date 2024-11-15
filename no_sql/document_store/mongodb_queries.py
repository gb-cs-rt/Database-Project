from pymongo import MongoClient
from tabulate import tabulate
import time

client = MongoClient("mongodb://localhost:27017/")
db = client['university']

# 1. histórico escolar de qualquer aluno, retornando o código e nome da disciplina, semestre e ano que a disciplina foi cursada e nota final

def get_historico_escolar(ra):
    print("\n1- Histórico escolar de qualquer aluno, retornando o código e nome da disciplina, semestre e ano que a disciplina foi cursada e nota final\n")

    student = db.aluno.find_one({"ra": ra})

    if student and "cursa" in student:
        academic_record = []
        for course in student["cursa"]:

            disciplina = db.disciplina.find_one({"_id": course["id_disciplina"]})
            if disciplina:
                record = {
                    "codigo_disciplina": course["codigo_disciplina"],
                    "nome_disciplina": disciplina["nome"],
                    "semestre": course["semestre"],
                    "ano": course["ano"],
                    "media_final": course["media"]
                }
                academic_record.append(record)

        academic_record.sort(key=lambda x: (x["ano"], x["semestre"]))

        headers = ["RA", "Código Disciplina", "Nome Disciplina", "Semestre", "Ano", "Média Final"]
        table = [[ra, record["codigo_disciplina"], record["nome_disciplina"], record["semestre"], record["ano"], record["media_final"]] for record in academic_record]
        print(tabulate(table, headers=headers, tablefmt="grid"))
    else:
        print("Este aluno não possui histórico.")

# 2. histórico de disciplinas ministradas por qualquer professor, com semestre e ano

def get_historico_disciplinas_lecionadas(id_professor):
    print("\n2- Histórico de disciplinas ministradas por qualquer professor, com semestre e ano\n")

    professor = db.professor.find_one({"id": id_professor})
    
    if professor and "leciona" in professor:
        teaching_history = []
        for leciona_entry in professor["leciona"]:

            disciplina = db.disciplina.find_one({"_id": leciona_entry["id_disciplina"]})
            if disciplina:
                record = {
                    "codigo_disciplina": leciona_entry["codigo_disciplina"],
                    "nome_disciplina": disciplina["nome"],
                    "semestre": leciona_entry["semestre"],
                    "ano": leciona_entry["ano"]
                }
                teaching_history.append(record)
        
        teaching_history.sort(key=lambda x: (x["ano"], x["semestre"]))
        
        headers = ["ID Professor", "Nome Professor", "Código Disciplina", "Nome Disciplina", "Semestre", "Ano"]
        table = [[id_professor, professor["nome"], record["codigo_disciplina"], record["nome_disciplina"], record["semestre"], record["ano"]] for record in teaching_history]
        print(tabulate(table, headers=headers, tablefmt="grid"))
    else:
        print("Este professor não possui histórico de disciplinas lecionadas.")

# 3. listar alunos que já se formaram (foram aprovados em todos os cursos de uma matriz curricular) em um determinado semestre de um ano
# obs: na nossa universidade, um aluno pode cursar as disciplinas da matriz curricular de seu curso na ordem que desejar
# portanto, "em um determinado semestre de um ano" se refere ao semestre e ano da última disciplina cursada e aprovada pelo aluno.
# para verificar todos os alunos formados em qualquer semestre e ano, basta não informar o semestre e ano

def listar_alunos_formados(semester=None, year=None):
    print("\n3- Listar alunos que já se formaram (foram aprovados em todos os cursos de uma matriz curricular) em um determinado semestre de um ano")
    
    if semester == 0:
        semester = None
    if year == 0:
        year = None
    
    pipeline = [
        {"$unwind": "$cursa"},

        {"$addFields": {
            "combined_year_semester": {
                "$concat": [
                    {"$toString": "$cursa.ano"}, "-",
                    {"$toString": "$cursa.semestre"}
                ]
            }
        }},

        {"$sort": {"combined_year_semester": -1}},

        {"$group": {
            "_id": "$ra",
            "nome": {"$first": "$nome"},
            "id_curso": {"$first": "$id_curso"},
            "all_courses": {"$push": "$cursa"},
            "latest_course": {"$first": "$cursa"}
        }},

        {"$match": {
            "$expr": {
                "$and": [
                    {"$or": [{"$eq": [semester, None]}, {"$eq": ["$latest_course.semestre", semester]}]},
                    {"$or": [{"$eq": [year, None]}, {"$eq": ["$latest_course.ano", year]}]}
                ]
            }
        }},

        {"$addFields": {
            "all_subjects_passed": {
                "$allElementsTrue": {
                    "$map": {
                        "input": "$all_courses",
                        "as": "course",
                        "in": {"$gte": ["$$course.media", 5]}
                    }
                }
            }
        }},
        {"$match": {"all_subjects_passed": True}},

        {"$project": {
            "_id": 0,
            "ra": "$_id",
            "nome": 1,
            "latest_semester": "$latest_course.semestre",
            "latest_year": "$latest_course.ano"
        }},

        {"$sort": {"latest_year": 1, "latest_semester": 1}}
    ]

    results = list(db.aluno.aggregate(pipeline))

    results.sort(key=lambda x: (x["latest_year"], x["latest_semester"], x["ra"]))

    headers = ["RA", "Nome", "Último Semestre", "Último Ano"]
    table = [[student["ra"], student["nome"], student["latest_semester"], student["latest_year"]] for student in results]
    if table:
        print(tabulate(table, headers=headers, tablefmt="grid"))
    else:
        print("Nenhum aluno encontrado que se formou no semestre e ano especificados.")

# 4. listar todos os professores que são chefes de departamento, junto com o nome do departamento

def listar_chefes_departamento():
    print("\n4- Listar todos os professores que são chefes de departamento, junto com o nome do departamento\n")

    pipeline = [
        {
            "$lookup": {
                "from": "departamento",
                "localField": "chefe_departamento",
                "foreignField": "nome_departamento",
                "as": "department_info"
            }
        },
        {
            "$match": {
                "department_info": {"$ne": []}
            }
        },
        {
            "$project": {
                "_id": 0,
                "nome_departamento": {"$arrayElemAt": ["$department_info.nome_departamento", 0]},
                "chefe": "$nome",
                "id": 1
            }
        }
    ]

    results = list(db.professor.aggregate(pipeline))

    headers = ["Nome Departamento", "Nome Chefe", "ID Chefe"]
    table = [[result["nome_departamento"], result["chefe"], result["id"]] for result in results]
    if table:
        print(tabulate(table, headers=headers, tablefmt="grid"))
    else:
        print("Nenhum chefe de departamento encontrado.")

# 5. saber quais alunos formaram um grupo de TCC e qual professor foi o orientador

def listar_grupos_tcc():
    print("\n5- Saber quais alunos formaram um grupo de TCC e qual professor foi o orientador\n")

    pipeline = [
        {
            "$match": {
                "grupo_tcc": {"$ne": None}
            }
        },
 
        {
            "$lookup": {
                "from": "professor",
                "let": {"grupo_id": "$grupo_tcc"},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$in": ["$$grupo_id", "$grupos_tcc"]
                            }
                        }
                    }
                ],
                "as": "professor_info"
            }
        },
        {"$unwind": "$professor_info"},

        {
            "$project": {
                "_id": 0,
                "id_grupo": "$grupo_tcc",
                "ra": "$ra",
                "nome_aluno": "$nome",
                "orientador": "$professor_info.nome"
            }
        },

        {"$sort": {"id_grupo": 1}}
    ]

    results = list(db.aluno.aggregate(pipeline))

    headers = ["ID Grupo", "RA Aluno", "Nome Aluno", "Orientador"]
    table = [[result["id_grupo"], result["ra"], result["nome_aluno"], result["orientador"]] for result in results]
    if table:
        print(tabulate(table, headers=headers, tablefmt="grid"))
    else:
        print("Nenhum grupo de TCC encontrado.")

# ===================
# Chamando as Queries
# ===================

def mongodb_queries():

    while True:

        print("\n==================  ESCOLHA UMA QUERY (MongoDB)  ==================")
        print("1 - Histórico escolar de qualquer aluno,")
        print("    retornando o código e nome da disciplina,")
        print("    semestre e ano que a disciplina foi cursada e nota final.\n")
        print("2 - Histórico de disciplinas ministradas por qualquer professor,")
        print("    com semestre e ano.\n")
        print("3 - Listar alunos que já se formaram (foram aprovados")
        print("    em todos os cursos de uma matriz curricular) em um")
        print("    determinado semestre de um ano.\n")
        print("4 - Listar todos os professores que são chefes de departamento,")
        print("    junto com o nome do departamento.\n")
        print("5 - Saber quais alunos formaram um grupo de TCC")
        print("    e qual professor foi o orientador.\n")
        print("0 - Voltar")
        print("===================================================================")

        option = input("Escolha uma opção: ")

        if option == "1":
            ra_aluno = int(input("Digite o RA do aluno: "))
            get_historico_escolar(ra_aluno)
        elif option == "2":
            id_professor = int(input("Digite o ID do professor: "))
            get_historico_disciplinas_lecionadas(id_professor)
        elif option == "3":
            semester = int(input("Digite o semestre (ou 0 para todos): "))
            year = int(input("Digite o ano (ou 0 para todos): "))
            listar_alunos_formados(semester, year)
        elif option == "4":
            listar_chefes_departamento()
        elif option == "5":
            listar_grupos_tcc()
        elif option == "0":
            break
        else:
            print("Opção inválida.")

        time.sleep(1)