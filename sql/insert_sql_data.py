import psycopg2
from faker import Faker
import random

def insert_sql_data():
    # Initialize Faker for generating random data
    fake = Faker("pt_BR")

    # Connect to the SQLite database (replace with your DB connection)
    try:
        conn = psycopg2.connect(password="cc6240", host="localhost", port="5432", database="postgres", user="postgres")
    except Exception as e:
        print("Erro ao conectar ao PostgreSQL:", e)
        return
    
    cursor = conn.cursor()

    # Clear all tables
    cursor.execute("DROP TABLE IF EXISTS GrupoTCC")
    cursor.execute("DROP TABLE IF EXISTS Leciona")
    cursor.execute("DROP TABLE IF EXISTS Cursa")
    cursor.execute("DROP TABLE IF EXISTS MatrizCurricular")
    cursor.execute("DROP TABLE IF EXISTS Disciplina")
    cursor.execute("DROP TABLE IF EXISTS Aluno")
    cursor.execute("DROP TABLE IF EXISTS Curso")
    cursor.execute("DROP TABLE IF EXISTS ChefeDepartamento")
    cursor.execute("DROP TABLE IF EXISTS Professor")
    cursor.execute("DROP TABLE IF EXISTS Departamento")

    # Clear all sequences
    cursor.execute("DROP SEQUENCE IF EXISTS aluno_ra_seq")
    cursor.execute("DROP SEQUENCE IF EXISTS curso_id_seq")
    cursor.execute("DROP SEQUENCE IF EXISTS professor_id_seq")

    # Create tables
    tables = [
        """
        CREATE TABLE IF NOT EXISTS Departamento (
            nome_departamento VARCHAR(30) PRIMARY KEY
        );
        """,
        """
        CREATE SEQUENCE professor_id_seq START 1;
        
        CREATE TABLE IF NOT EXISTS Professor (
            id INTEGER PRIMARY KEY DEFAULT nextval('professor_id_seq'),
            nome_departamento VARCHAR(30),
            nome VARCHAR(50),
            email VARCHAR(50),
            telefone VARCHAR(20),
            salario NUMERIC(8, 2),
            FOREIGN KEY (nome_departamento) REFERENCES Departamento(nome_departamento)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS ChefeDepartamento (
            id_professor INTEGER PRIMARY KEY,
            nome_departamento VARCHAR(30),
            FOREIGN KEY (id_professor) REFERENCES Professor(id),
            FOREIGN KEY (nome_departamento) REFERENCES Departamento(nome_departamento)
        );
        """,
        """
        CREATE SEQUENCE curso_id_seq START 1;

        CREATE TABLE IF NOT EXISTS Curso (
            id_curso INTEGER PRIMARY KEY DEFAULT nextval('curso_id_seq'),
            nome VARCHAR(30),
            nome_departamento VARCHAR(30),
            horas_complementares NUMERIC(3),
            faltas NUMERIC(2),
            FOREIGN KEY (nome_departamento) REFERENCES Departamento(nome_departamento)
        );
        """,
        """
        CREATE SEQUENCE aluno_ra_seq START 1;

        CREATE TABLE IF NOT EXISTS Aluno (
            ra INTEGER PRIMARY KEY DEFAULT nextval('aluno_ra_seq'),
            id_curso INTEGER,
            nome VARCHAR(50),
            email VARCHAR(50),
            telefone VARCHAR(20),
            FOREIGN KEY (id_curso) REFERENCES Curso(id_curso)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Disciplina (
            codigo_disciplina VARCHAR(6) PRIMARY KEY,
            nome_departamento VARCHAR(30),
            nome VARCHAR(40),
            carga_horaria NUMERIC(3),
            FOREIGN KEY (nome_departamento) REFERENCES Departamento(nome_departamento)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS MatrizCurricular (
            codigo_disciplina VARCHAR(6),
            id_curso INTEGER,
            PRIMARY KEY (codigo_disciplina, id_curso),
            FOREIGN KEY (codigo_disciplina) REFERENCES Disciplina(codigo_disciplina),
            FOREIGN KEY (id_curso) REFERENCES Curso(id_curso)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Cursa (
            id_aluno INTEGER,
            id_curso INTEGER,
            codigo_disciplina VARCHAR(6),
            semestre NUMERIC(1),
            ano NUMERIC(4),
            media NUMERIC(4, 2),
            faltas NUMERIC(2),
            PRIMARY KEY (id_aluno, codigo_disciplina),
            FOREIGN KEY (id_aluno) REFERENCES Aluno(ra),
            FOREIGN KEY (id_curso) REFERENCES Curso(id_curso),
            FOREIGN KEY (codigo_disciplina) REFERENCES Disciplina(codigo_disciplina)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS Leciona (
            id_professor INTEGER,
            id_curso INTEGER,
            codigo_disciplina VARCHAR(6),
            semestre NUMERIC(1),
            ano NUMERIC(4),
            carga_horaria NUMERIC(3),
            PRIMARY KEY (id_professor, codigo_disciplina),
            FOREIGN KEY (id_professor) REFERENCES Professor(id),
            FOREIGN KEY (id_curso) REFERENCES Curso(id_curso),
            FOREIGN KEY (codigo_disciplina) REFERENCES Disciplina(codigo_disciplina)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS GrupoTCC (
            id_grupo INTEGER,
            id_professor INTEGER,
            ra INTEGER,
            PRIMARY KEY (id_grupo, ra),
            FOREIGN KEY (id_professor) REFERENCES Professor(id),
            FOREIGN KEY (ra) REFERENCES Aluno(ra)
        );
        """
    ]

    for table in tables:
        cursor.execute(table)

    # Insert data into Departamento
    departamentos = ['Ciência da Computação', 'Engenharia Elétrica', 'Engenharia Mecânica', 'Engenharia de Robôs']
    for dep in departamentos:
        cursor.execute("INSERT INTO Departamento (nome_departamento) VALUES (%s) ON CONFLICT (nome_departamento) DO NOTHING", (dep,))

    # Insert data into Professor
    for _ in range(40):
        nome_dep = random.choice(departamentos)
        nome = fake.name()
        email = fake.email()
        telefone = fake.phone_number()
        salario = round(random.uniform(3000, 10000), 2)
        cursor.execute("""
            INSERT INTO Professor (nome_departamento, nome, email, telefone, salario) 
            VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING
        """, (nome_dep, nome, email, telefone, salario))

    # Insert data into Curso
    for dep in departamentos:
        nome_dep = dep
        nome_curso = dep
        horas_complementares = random.randint(180, 320)
        faltas = random.randint(10, 20)
        cursor.execute("""
            INSERT INTO Curso (nome_departamento, nome, horas_complementares, faltas) 
            VALUES (%s, %s, %s, %s) ON CONFLICT (id_curso) DO NOTHING
        """, (nome_dep, nome_curso, horas_complementares, faltas))

    cursor.execute("SELECT id_curso FROM Curso")
    id_cursos = cursor.fetchall()

    # Insert data into Aluno
    for _ in range(100):
        id_curso = random.choice(id_cursos)[0]
        nome = fake.name()
        email = fake.email()
        telefone = fake.phone_number()
        cursor.execute("""
            INSERT INTO Aluno (id_curso, nome, email, telefone) 
            VALUES (%s, %s, %s, %s) ON CONFLICT (ra) DO NOTHING
        """, (id_curso, nome, email, telefone))

    # Insert data into Disciplina
    disciplinas = ['Comunicação e Expressão', 'Cálculo I', 'Cálculo II', 'Cálculo III', 'Álgebra Linear', 'Física I', 'Física II', 'Física III', 'Química Geral', 'Química Orgânica', 'Programação I', 'Programação II', 'Programação III', 'Estrutura de Dados', 'Banco de Dados', 'Redes de Computadores', 'Sistemas Operacionais', 'Engenharia de Software', 'Inteligência Artificial', 'Computação Gráfica', 'Sistemas Distribuídos', 'Segurança da Informação', 'Empreendedorismo', 'Gestão de Projetos', 'Tópicos Especiais em Computação', 'Ética e Cidadania', 'Metodologia Científica', 'Trabalho de Conclusão de Curso']
    for _ in range(len(disciplinas)):
        codigo_disciplina = fake.unique.bothify(text='??###')
        nome_dep = random.choice(departamentos)
        nome = disciplinas.pop(random.randint(0, len(disciplinas) - 1))
        carga_horaria = random.randint(30, 180)
        cursor.execute("""
            INSERT INTO Disciplina (codigo_disciplina, nome_departamento, nome, carga_horaria) 
            VALUES (%s, %s, %s, %s) ON CONFLICT (codigo_disciplina) DO NOTHING
        """, (codigo_disciplina, nome_dep, nome, carga_horaria))

    # Insert data into MatrizCurricular
    cursor.execute("SELECT codigo_disciplina, nome_departamento FROM Disciplina")
    disciplinas = cursor.fetchall()
    disciplinas_copy = disciplinas.copy()

    for _ in range(len(disciplinas)):
        disciplina = disciplinas_copy.pop()
        codigo_disciplina = disciplina[0]

        cursor.execute(f"""SELECT id_curso FROM Curso as c
                    WHERE c.nome_departamento = \'{disciplina[1]}\'""")

        id_curso = cursor.fetchone()[0]
        cursor.execute("""
            INSERT INTO MatrizCurricular (codigo_disciplina, id_curso) 
            VALUES (%s, %s) ON CONFLICT (codigo_disciplina, id_curso) DO NOTHING
        """, (codigo_disciplina, id_curso))

    # Insert data into Cursa
    cursor.execute("SELECT ra, id_curso FROM Aluno")
    alunos = cursor.fetchall()
    alunos_copy = alunos.copy()

    for _ in range(len(alunos)):
        aluno = alunos_copy.pop(random.randint(0, len(alunos_copy) - 1))
        id_aluno = aluno[0]
        id_curso = aluno[1]

        cursor.execute(f"""SELECT codigo_disciplina FROM MatrizCurricular as m
                        WHERE m.id_curso = {id_curso}""")
        disciplinas_matriz = cursor.fetchall()

        for _ in range(len(disciplinas_matriz)):
            codigo_disciplina = disciplinas_matriz.pop()[0]
            semestre = random.randint(1, 2)
            ano = random.randint(2019, 2024)
            # 70% of the students have a grade between 5 and 10
            # 30% of the students have a grade between 0 and 5
            media = random.uniform(0, 10) if random.random() < 0.3 else random.uniform(5, 10)
            faltas = random.randint(0, 10)
            cursor.execute("""
                INSERT INTO Cursa (id_aluno, id_curso, codigo_disciplina, semestre, ano, media, faltas) 
                VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id_aluno, codigo_disciplina) DO NOTHING
            """, (id_aluno, id_curso, codigo_disciplina, semestre, ano, media, faltas))

    # Insert data into Leciona
    cursor.execute("SELECT id_curso FROM Curso")
    cursos = cursor.fetchall()

    cursor.execute("SELECT id FROM Professor")
    professores = cursor.fetchall()

    for _ in range(80):
        id_professor = random.choice(professores)[0]
        id_curso = random.choice(cursos)[0]
        codigo_disciplina = random.choice(disciplinas)[0]
        semestre = random.randint(1, 2)
        ano = random.randint(2019, 2024)
        carga_horaria = random.randint(30, 60)
        cursor.execute("""
            INSERT INTO Leciona (id_professor, id_curso, codigo_disciplina, semestre, ano, carga_horaria) 
            VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (id_professor, codigo_disciplina) DO NOTHING
        """, (id_professor, id_curso, codigo_disciplina, semestre, ano, carga_horaria))

    # Insert data into GrupoTCC
    qtd_grupos = round(len(alunos)/3)
    qtd_alunos_por_grupo = 3

    for i in range(qtd_grupos):
        id_grupo = i + 1
        id_professor = random.choice(professores)[0]

        for _ in range(qtd_alunos_por_grupo):
            ra = alunos.pop(random.randint(0, len(alunos) - 1))[0]
            cursor.execute("""
                INSERT INTO GrupoTCC (id_grupo, id_professor, ra) 
                VALUES (%s, %s, %s) ON CONFLICT (id_grupo, ra) DO NOTHING
            """, (id_grupo, id_professor, ra))

    # Insert data into ChefeDepartamento
    cursor.execute("SELECT id FROM Professor")
    professores = cursor.fetchall()
    for _ in range(len(departamentos)):
        id_professor = professores.pop(random.randint(0, len(professores) - 1))[0]
        nome_dep = departamentos.pop()
        cursor.execute("""
            INSERT INTO ChefeDepartamento (id_professor, nome_departamento) 
            VALUES (%s, %s) ON CONFLICT (id_professor) DO NOTHING
        """, (id_professor, nome_dep))

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

    print("Dados inseridos no PostgreSQL com sucesso!")