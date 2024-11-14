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
    # Change directory to the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Read data from JSON files
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

    # Connect to the Cassandra cluster
    try:
        cluster = Cluster(['127.0.0.1'])  # Adjust the contact points as needed
        session = cluster.connect()
    except Exception as e:
        print("Error connecting to Cassandra:", e)
        return

    # Create keyspace 'university' if it doesn't exist
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS university
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
    """)

    session.set_keyspace('university')

    # Drop tables if they exist
    session.execute("DROP TABLE IF EXISTS departamento")
    session.execute("DROP TABLE IF EXISTS disciplina")
    session.execute("DROP TABLE IF EXISTS professor")
    session.execute("DROP TABLE IF EXISTS curso")
    session.execute("DROP TABLE IF EXISTS aluno")
    session.execute("DROP TYPE IF EXISTS leciona_entry")
    session.execute("DROP TYPE IF EXISTS cursa_entry")

    # Create User-Defined Types (UDTs)
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

    # Create tables
    session.execute("""
        CREATE TABLE departamento (
            nome_departamento text PRIMARY KEY,
            chefe_id int
        )
    """)

    session.execute("""
        CREATE TABLE disciplina (
            codigo_disciplina text PRIMARY KEY,
            nome text,
            carga_horaria int,
            nome_departamento text
        )
    """)

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

    # Insert data into 'departamento'
    for dept in departamentos:
        session.execute("""
            INSERT INTO departamento (nome_departamento)
            VALUES (%s)
        """, (dept['nome_departamento'],))

    # Insert data into 'disciplina'
    for disc in disciplinas:
        session.execute("""
            INSERT INTO disciplina (codigo_disciplina, nome, carga_horaria, nome_departamento)
            VALUES (%s, %s, %s, %s)
        """, (disc['codigo_disciplina'], disc['nome'], int(disc['carga_horaria']), disc['nome_departamento']))

    # Insert data into 'professor'
    for professor in professores:
        # Process 'leciona' entries
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

        # Process 'grupos_tcc' entries
        grupos_ids = [int(grupo['id_grupo']) for grupo in grupos_tcc if grupo['id_professor'] == professor['id']]

        # Insert professor data
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

    # Update 'departamento' with 'chefe_id'
    for chefe_departamento in chefes_departamento:
        nome_departamento = chefe_departamento['nome_departamento']
        id_professor = int(chefe_departamento['id_professor'])

        # Update 'departamento' table
        session.execute("""
            UPDATE departamento
            SET chefe_id = %s
            WHERE nome_departamento = %s
        """, (id_professor, nome_departamento))

        # Update 'professor' table with 'chefe_departamento'
        session.execute("""
            UPDATE professor
            SET chefe_departamento = %s
            WHERE id = %s
        """, (nome_departamento, id_professor))

    # Insert data into 'curso'
    for curso in cursos:
        # Process 'matriz_curricular'
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

    # Insert data into 'aluno'
    for aluno in alunos:
        # Process 'cursa' entries
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

        # Get 'grupo_tcc'
        grupo_tcc = next((int(grupo['id_grupo']) for grupo in grupos_tcc if grupo['ra'] == aluno['ra']), None)

        # Insert aluno data
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