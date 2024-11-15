from cassandra.cluster import Cluster
import json
import os

class LecionaEntry:
    def __init__(self, id_curso, codigo_disciplina, semestre, ano, carga_horaria):
        self.id_curso = id_curso
        self.codigo_disciplina = codigo_disciplina
        self.semestre = semestre
        self.ano = ano
        self.carga_horaria = carga_horaria

    def __repr__(self):
        return f"LecionaEntry({self.id_curso}, {self.codigo_disciplina}, {self.semestre}, {self.ano}, {self.carga_horaria})"

class CursaEntry:
    def __init__(self, codigo_disciplina, semestre, ano, faltas, media):
        self.codigo_disciplina = codigo_disciplina
        self.semestre = semestre
        self.ano = ano
        self.faltas = faltas
        self.media = media

    def __repr__(self):
        return f"CursaEntry({self.codigo_disciplina}, {self.semestre}, {self.ano}, {self.faltas}, {self.media})"

def read_sql_data(table):
    with open(f"../../sql/sql_data/{table}.json", "r", encoding="utf-8") as f:
        return json.load(f)

def insert_cassandra_data():
    # Muda o diretório para o diretório do script
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

    # Conecta ao Cassandra
    try:
        cluster = Cluster(['127.0.0.1'])  # Adjust the contact points as needed
        session = cluster.connect()
    except Exception as e:
        print("Error connecting to Cassandra:", e)
        return

    # Cria o keyspace e seta o keyspace
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS university
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
    """)

    session.set_keyspace('university')

    # Apaga as tabelas e tipos de dados se existirem
    session.execute("DROP TABLE IF EXISTS departamento")
    session.execute("DROP TABLE IF EXISTS disciplina")
    session.execute("DROP TABLE IF EXISTS professor")
    session.execute("DROP TABLE IF EXISTS curso")
    session.execute("DROP TABLE IF EXISTS aluno")
    session.execute("DROP TYPE IF EXISTS leciona_entry")
    session.execute("DROP TYPE IF EXISTS cursa_entry")

    # Cria os tipos de dados customizados
    session.execute("""
        CREATE TYPE IF NOT EXISTS leciona_entry (
            id_curso int,
            codigo_disciplina text,
            semestre int,
            ano int,
            carga_horaria double
        )
    """)

    session.execute("""
        CREATE TYPE IF NOT EXISTS cursa_entry (
            codigo_disciplina text,
            semestre int,
            ano int,
            faltas int,
            media double
        )
    """)

    cluster.register_user_type('university', 'leciona_entry', LecionaEntry)
    cluster.register_user_type('university', 'cursa_entry', CursaEntry)

    # Cria a tabela 'departamento'
    session.execute("""
        CREATE TABLE departamento (
            nome_departamento text PRIMARY KEY,
            chefe_id int
        )
    """)

    # Cria a tabela 'disciplina'
    session.execute("""
        CREATE TABLE disciplina (
            codigo_disciplina text PRIMARY KEY,
            nome text,
            carga_horaria int,
            nome_departamento text
        )
    """)

    # Cria a tabela 'professor'
    session.execute("""
        CREATE TABLE professor (
            id int PRIMARY KEY,
            nome text,
            nome_departamento text,
            email text,
            telefone text,
            salario double,
            chefe_departamento text,
            grupos_tcc list<int>,
            leciona list<frozen<leciona_entry>>
        )
    """)

    # Cria a tabela 'curso'
    session.execute("""
        CREATE TABLE curso (
            id_curso int PRIMARY KEY,
            nome_departamento text,
            nome text,
            horas_complementares int,
            faltas int,
            matriz_curricular list<text>
        )
    """)

    # Cria a tabela 'aluno'
    session.execute("""
        CREATE TABLE aluno (
            ra int PRIMARY KEY,
            id_curso int,
            nome text,
            email text,
            telefone text,
            grupo_tcc int,
            cursa list<frozen<cursa_entry>>
        )
    """)

    # Insere os dados na tabela 'departamento'
    for dept in departamentos:
        session.execute("""
            INSERT INTO departamento (nome_departamento)
            VALUES (%s)
        """, (dept['nome_departamento'],))

    # Insere os dados na tabela 'disciplina'
    for disc in disciplinas:
        session.execute("""
            INSERT INTO disciplina (codigo_disciplina, nome, carga_horaria, nome_departamento)
            VALUES (%s, %s, %s, %s)
        """, (disc['codigo_disciplina'], disc['nome'], int(disc['carga_horaria']), disc['nome_departamento']))

    # Insere os dados na tabela 'professor'
    for professor in professores:
        # Insere os dados de 'leciona' na tabela 'professor'
        leciona_entries = []
        for leciona_entry in leciona:
            if leciona_entry['id_professor'] == professor['id']:
                leciona_instance = LecionaEntry(
                    id_curso=int(leciona_entry['id_curso']),
                    codigo_disciplina=leciona_entry['codigo_disciplina'],
                    semestre=int(leciona_entry['semestre']),
                    ano=int(leciona_entry['ano']),
                    carga_horaria=float(leciona_entry['carga_horaria'])
                )
                leciona_entries.append(leciona_instance)

        # Insere os dados de 'grupos_tcc' na tabela 'professor'
        grupos_ids = [int(grupo['id_grupo']) for grupo in grupos_tcc if grupo['id_professor'] == professor['id']]

        # Insere os dados do professor na tabela 'professor'
        session.execute("""
            INSERT INTO professor (id, nome, nome_departamento, email, telefone, salario, grupos_tcc, leciona)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            int(professor['id']),
            professor['nome'],
            professor['nome_departamento'],
            professor['email'],
            professor['telefone'],
            float(professor['salario']),
            grupos_ids,
            leciona_entries
        ))

    # Atualiza as tabelas 'departamento' e 'professor' com os chefes de departamento
    for chefe_departamento in chefes_departamento:
        nome_departamento = chefe_departamento['nome_departamento']
        id_professor = int(chefe_departamento['id_professor'])

        # Atualiza 'departamento' com 'chefe_id'
        session.execute("""
            UPDATE departamento
            SET chefe_id = %s
            WHERE nome_departamento = %s
        """, (id_professor, nome_departamento))

        # Atualiza 'professor' com 'chefe_departamento'
        session.execute("""
            UPDATE professor
            SET chefe_departamento = %s
            WHERE id = %s
        """, (nome_departamento, id_professor))

    # Insere os dados na tabela 'curso'
    for curso in cursos:
        # Insere os dados de 'matriz_curricular' na tabela 'curso'
        matriz = [matriz_entry['codigo_disciplina'] for matriz_entry in matrizes_curriculares if matriz_entry['id_curso'] == curso['id_curso']]

        session.execute("""
            INSERT INTO curso (id_curso, nome_departamento, nome, horas_complementares, faltas, matriz_curricular)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            int(curso['id_curso']),
            curso['nome_departamento'],
            curso['nome'],
            int(curso['horas_complementares']),
            int(curso['faltas']),
            matriz
        ))

    # Insere os dados na tabela 'aluno'
    for aluno in alunos:
        # Insere os dados de 'cursa' na tabela 'aluno'
        cursa_entries = []
        for cursa_entry in cursa:
            if cursa_entry['id_aluno'] == aluno['ra']:
                cursa_dict = CursaEntry(
                    codigo_disciplina=cursa_entry['codigo_disciplina'],
                    semestre=int(cursa_entry['semestre']),
                    ano=int(cursa_entry['ano']),
                    faltas=int(cursa_entry['faltas']),
                    media=float(cursa_entry['media'])
                )
                cursa_entries.append(cursa_dict)

        # Insere os dados de 'grupos_tcc' na tabela 'aluno'
        grupo_tcc = next((int(grupo['id_grupo']) for grupo in grupos_tcc if grupo['ra'] == aluno['ra']), None)

        # Insere os dados do aluno na tabela 'aluno'
        session.execute("""
            INSERT INTO aluno (ra, id_curso, nome, email, telefone, grupo_tcc, cursa)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            int(aluno['ra']),
            int(aluno['id_curso']),
            aluno['nome'],
            aluno['email'],
            aluno['telefone'],
            grupo_tcc,
            cursa_entries
        ))

    print("Dados inseridos no Cassandra com sucesso!")