from neo4j import GraphDatabase
import json
import os

neo4j_uri = "bolt://localhost:7687"
default_user = "neo4j"
default_password = "cc6240admin"

def read_sql_data(table):
    with open(f"../../sql/sql_data/{table}.json", "r", encoding="utf-8") as f:
        return json.load(f)

def insert_neo4j_data():

    try:
        driver = GraphDatabase.driver(neo4j_uri, auth=(default_user, default_password))
    except Exception as e:
        print("Erro ao conectar ao Neo4J:", e)
        return
    finally:
        driver.close()

    # Change directory to the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Read data from JSON files
    alunos = read_sql_data("aluno")
    cursos = read_sql_data("curso")
    departamentos = read_sql_data("departamento")
    disciplinas = read_sql_data("disciplina")
    professores = read_sql_data("professor")
    leciona = read_sql_data("leciona")
    cursa = read_sql_data("cursa")
    matrizes_curriculares = read_sql_data("matrizcurricular")
    chefes_departamento = read_sql_data("chefedepartamento")
    grupos_tcc = read_sql_data("grupotcc")

    with driver.session() as session:

        # Clear database
        session.run("MATCH (n) DETACH DELETE n")

        # Insert nodes
        for aluno in alunos:
            session.run("""
                MERGE (a:Aluno {ra: $ra})
                SET a.nome = $nome, a.email = $email, a.telefone = $telefone
            """, ra=aluno["ra"], nome=aluno["nome"], email=aluno["email"], telefone=aluno["telefone"])
        
        for curso in cursos:
            session.run("""
                MERGE (c:Curso {id_curso: $id_curso})
                SET c.nome = $nome, c.nome_departamento = $nome_departamento, c.horas_complementares = $horas_complementares, c.faltas = $faltas
            """, id_curso=curso["id_curso"], nome=curso["nome"], nome_departamento=curso["nome_departamento"],
            horas_complementares=curso["horas_complementares"], faltas=curso["faltas"])
        
        for departamento in departamentos:
            session.run("""
                MERGE (d:Departamento {nome_departamento: $nome_departamento})
            """, nome_departamento=departamento["nome_departamento"])
        
        for disciplina in disciplinas:
            session.run("""
                MERGE (di:Disciplina {codigo_disciplina: $codigo_disciplina})
                SET di.nome = $nome, di.carga_horaria = $carga_horaria, di.nome_departamento = $nome_departamento
            """, codigo_disciplina=disciplina["codigo_disciplina"], nome=disciplina["nome"], 
            carga_horaria=disciplina["carga_horaria"], nome_departamento=disciplina["nome_departamento"])
        
        for professor in professores:
            session.run("""
                MERGE (p:Professor {id: $id})
                SET p.nome = $nome, p.email = $email, p.telefone = $telefone, p.salario = $salario, p.nome_departamento = $nome_departamento
            """, id=professor["id"], nome=professor["nome"], email=professor["email"], telefone=professor["telefone"], 
            salario=professor["salario"], nome_departamento=professor["nome_departamento"])

        # Insert relationships
        for leciona_entry in leciona:
            session.run("""
                MATCH (p:Professor {id: $id_professor}), (di:Disciplina {codigo_disciplina: $codigo_disciplina})
                MERGE (p)-[:LECIONA {semestre: $semestre, ano: $ano, carga_horaria: $carga_horaria}]->(di)
            """, id_professor=leciona_entry["id_professor"], codigo_disciplina=leciona_entry["codigo_disciplina"], 
            semestre=leciona_entry["semestre"], ano=leciona_entry["ano"], carga_horaria=leciona_entry["carga_horaria"])
        
        for cursa_entry in cursa:
            session.run("""
                MATCH (a:Aluno {ra: $ra}), (di:Disciplina {codigo_disciplina: $codigo_disciplina})
                MERGE (a)-[:CURSA {semestre: $semestre, ano: $ano, media: $media, faltas: $faltas}]->(di)
            """, ra=cursa_entry["id_aluno"], codigo_disciplina=cursa_entry["codigo_disciplina"], 
            semestre=cursa_entry["semestre"], ano=cursa_entry["ano"], media=cursa_entry["media"], faltas=cursa_entry["faltas"])
        
        for matriz in matrizes_curriculares:
            session.run("""
                MATCH (c:Curso {id_curso: $id_curso}), (di:Disciplina {codigo_disciplina: $codigo_disciplina})
                MERGE (c)-[:INCLUI]->(di)
            """, id_curso=matriz["id_curso"], codigo_disciplina=matriz["codigo_disciplina"])
        
        for chefe in chefes_departamento:
            session.run("""
                MATCH (p:Professor {id: $id_professor}), (d:Departamento {nome_departamento: $nome_departamento})
                MERGE (p)-[:CHEFE_DE]->(d)
            """, id_professor=chefe["id_professor"], nome_departamento=chefe["nome_departamento"])
        
        for grupo in grupos_tcc:
            session.run("""
                MATCH (a:Aluno {ra: $ra}), (p:Professor)
                WHERE $id_grupo IN p.grupos_tcc
                MERGE (a)-[:MEMBRO_DO_GRUPO {id_grupo: $id_grupo}]->(p)
            """, ra=grupo["ra"], id_grupo=grupo["id_grupo"])

    print("Dados inseridos no Neo4J com sucesso!")