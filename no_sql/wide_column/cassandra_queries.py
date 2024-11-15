from cassandra.cluster import Cluster
from tabulate import tabulate
import time

# 1. histórico escolar de qualquer aluno, retornando o código e nome da disciplina, semestre e ano que a disciplina foi cursada e nota final

def get_historico_escolar(session, ra):
    print("\n1- Histórico escolar de qualquer aluno, retornando o código e nome da disciplina, semestre e ano que a disciplina foi cursada e nota final\n")
    
    rows = session.execute("""
        SELECT cursa FROM aluno WHERE ra = %s
    """, (ra,))
    
    academic_record = []
    for row in rows:
        if row.cursa:
            for course in row.cursa:

                disciplina_row = session.execute("""
                    SELECT nome FROM disciplina WHERE codigo_disciplina = %s
                """, (course.codigo_disciplina,)).one()
                
                if disciplina_row:
                    record = {
                        "codigo_disciplina": course.codigo_disciplina,
                        "nome_disciplina": disciplina_row.nome,
                        "semestre": course.semestre,
                        "ano": course.ano,
                        "media_final": course.media
                    }
                    academic_record.append(record)

    academic_record.sort(key=lambda x: (x["ano"], x["semestre"]))
    
    headers = ["RA", "Código Disciplina", "Nome Disciplina", "Semestre", "Ano", "Média Final"]
    table = [[ra, record["codigo_disciplina"], record["nome_disciplina"], record["semestre"], record["ano"], record["media_final"]] for record in academic_record]
    if table:
        print(tabulate(table, headers=headers, tablefmt="grid"))
    else:
        print("Este aluno não possui histórico.")

# 2. histórico de disciplinas ministradas por qualquer professor, com semestre e ano

def get_historico_disciplinas_lecionadas(session, id_professor):
    print("\n2- Histórico de disciplinas ministradas por qualquer professor, com semestre e ano\n")
    
    rows = session.execute("""
        SELECT leciona, nome FROM professor WHERE id = %s
    """, (id_professor,))
    
    teaching_history = []
    for row in rows:
        if row.leciona:
            for leciona_entry in row.leciona:

                disciplina_row = session.execute("""
                    SELECT nome FROM disciplina WHERE codigo_disciplina = %s
                """, (leciona_entry.codigo_disciplina,)).one()
                
                if disciplina_row:
                    record = {
                        "nome_professor": row.nome,
                        "codigo_disciplina": leciona_entry.codigo_disciplina,
                        "nome_disciplina": disciplina_row.nome,
                        "semestre": leciona_entry.semestre,
                        "ano": leciona_entry.ano
                    }
                    teaching_history.append(record)
    
    teaching_history.sort(key=lambda x: (x["ano"], x["semestre"]))
    
    headers = ["ID Professor", "Nome Professor", "Código Disciplina", "Nome Disciplina", "Semestre", "Ano"]
    table = [[id_professor, record["nome_professor"], record["codigo_disciplina"], record["nome_disciplina"], record["semestre"], record["ano"]] for record in teaching_history]
    if table:
        print(tabulate(table, headers=headers, tablefmt="grid"))
    else:
        print("Este professor não possui histórico de disciplinas lecionadas.")

# 3. listar alunos que já se formaram (foram aprovados em todos os cursos de uma matriz curricular) em um determinado semestre de um ano
# obs: na nossa universidade, um aluno pode cursar as disciplinas da matriz curricular de seu curso na ordem que desejar
# portanto, "em um determinado semestre de um ano" se refere ao semestre e ano da última disciplina cursada e aprovada pelo aluno.
# para verificar todos os alunos formados em qualquer semestre e ano, basta não informar o semestre e ano

def listar_alunos_formados(session, semester=None, year=None):
    print("\n3- Listar alunos que já se formaram (foram aprovados em todos os cursos de uma matriz curricular) em um determinado semestre de um ano\n")
    
    if semester == 0:
        semester = None
    if year == 0:
        year = None

    rows = session.execute("""
        SELECT ra, nome, id_curso, cursa FROM aluno
    """)

    graduated_students = []
    for row in rows:
        if row.cursa:

            all_passed = all(course.media >= 5 for course in row.cursa)
            latest_semester = max(row.cursa, key=lambda x: (x.ano, x.semestre)).semestre
            latest_year = max(row.cursa, key=lambda x: (x.ano, x.semestre)).ano

            if all_passed and (semester is None or semester == latest_semester) and (year is None or year == latest_year):
                graduated_students.append({
                    "ra": row.ra,
                    "nome": row.nome,
                    "latest_semester": latest_semester,
                    "latest_year": latest_year
                })

    # Sorting results
    graduated_students.sort(key=lambda x: (x["latest_year"], x["latest_semester"], x["ra"]))

    headers = ["RA", "Nome", "Último Semestre", "Último Ano"]
    table = [[student["ra"], student["nome"], student["latest_semester"], student["latest_year"]] for student in graduated_students]
    if table:
        print(tabulate(table, headers=headers, tablefmt="grid"))
    else:
        print("Nenhum aluno encontrado que se formou no semestre e ano especificados.")

# 4. listar todos os professores que são chefes de departamento, junto com o nome do departamento

def listar_chefes_departamento(session):
    print("\n4- Listar todos os professores que são chefes de departamento, junto com o nome do departamento\n")
    
    rows = session.execute("""
        SELECT nome_departamento, chefe_id FROM departamento
    """)

    results = []
    for row in rows:
        if row.chefe_id is not None:

            professor = session.execute("""
                SELECT nome FROM professor WHERE id = %s
            """, (row.chefe_id,)).one()
            
            if professor:
                results.append({
                    "nome_departamento": row.nome_departamento,
                    "chefe": professor.nome,
                    "id": row.chefe_id
                })

    results.sort(key=lambda x: x["id"])

    headers = ["Nome Departamento", "Nome Chefe", "ID Chefe"]
    table = [[result["nome_departamento"], result["chefe"], result["id"]] for result in results]
    if table:
        print(tabulate(table, headers=headers, tablefmt="grid"))
    else:
        print("Nenhum chefe de departamento encontrado.")

# 5. saber quais alunos formaram um grupo de TCC e qual professor foi o orientador

def listar_grupos_tcc(session):
    print("\n5- Saber quais alunos formaram um grupo de TCC e qual professor foi o orientador\n")
    
    rows = session.execute("""
        SELECT ra, nome, grupo_tcc FROM aluno
    """)

    results = []
    for row in rows:
        if row.grupo_tcc is not None:

            professors = session.execute("""
                SELECT id, nome, grupos_tcc FROM professor
            """)
            for professor in professors:

                if professor.grupos_tcc is not None and row.grupo_tcc in professor.grupos_tcc:
                    results.append({
                        "id_grupo": row.grupo_tcc,
                        "ra": row.ra,
                        "nome_aluno": row.nome,
                        "orientador": professor.nome
                    })
                    break

    results.sort(key=lambda x: x["id_grupo"])

    headers = ["ID Grupo", "RA Aluno", "Nome Aluno", "Orientador"]
    table = [[result["id_grupo"], result["ra"], result["nome_aluno"], result["orientador"]] for result in results]
    if table:
        print(tabulate(table, headers=headers, tablefmt="grid"))
    else:
        print("Nenhum grupo de TCC encontrado.")

# ===================
# Chamando as Queries
# ===================

def cassandra_queries():

    try:
        cluster = Cluster(['127.0.0.1'])
        session = cluster.connect()
        session.set_keyspace('university')
    except Exception as e:
        print("Error connecting to Cassandra:", e)

    while True:

        print("\n=================  ESCOLHA UMA QUERY (Cassandra)  ==================")
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
        print("====================================================================")


        option = input("Escolha uma opção: ")

        if option == "1":
            ra_aluno = int(input("Digite o RA do aluno: "))
            get_historico_escolar(session, ra_aluno)
        elif option == "2":
            id_professor = int(input("Digite o ID do professor: "))
            get_historico_disciplinas_lecionadas(session, id_professor)
        elif option == "3":
            semester = int(input("Digite o semestre (ou 0 para todos): "))
            year = int(input("Digite o ano (ou 0 para todos): "))
            listar_alunos_formados(session, semester, year)
        elif option == "4":
            listar_chefes_departamento(session)
        elif option == "5":
            listar_grupos_tcc(session)
        elif option == "0":
            break
        else:
            print("Opção inválida.")

        time.sleep(1)