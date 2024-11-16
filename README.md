# Projeto NoSQL - CC6240

Este projeto foi desenvolvido durante a disciplina de Tópicos Avançados de Banco de Dados (CC6240) do Centro Universitário FEI.
O objetivo do projeto é converter os dados de um banco relacional (PostgreSQL) modelado para uma universidade, e inserir os mesmos dados em três diferentes bancos não relacionais: MongoDB, Cassandra e Neo4J.
Também devem ser feitas algumas queries de consulta nos bancos, que devem retornar o mesmo resultado.

## Requisitos

- Ubuntu 22.04
- Docker e Docker Compose
- Python e Pip

## Primeiros Passos

1- Clone o repositório da disciplina, que contém o arquivo de configuração do Docker para subir os 4 bancos:
```bash
git clone https://gitlab.com/laferreira/fei/cc6240.git
cd cc6240/src/
```

2- Inicie o Docker, que subirá os 4 bancos a serem utilizados (PostgreSQL, MongoDB, Cassandra e Neo4J):
```bash
sudo docker compose up
```

3- Clone o repositório do projeto, que contém os programas de inserção e consulta de dados nos bancos:
```bash
git clone https://github.com/gb-cs-rt/projeto_nosql.git
cd projeto_nosql/
```

4- Instale as dependências do projeto:
```bash
pip install -r requirements.txt
```

5- Inicie o programa:
```bash
python main.py
```

## Como usar

Logo de início, o programa irá inserir os dados no PostgreSQL, extrair dos dados do PostgreSQL e inserí-los nos demais bancos.<br>
Então, será exibido um menu, através do qual é possível escolher em qual banco deseja fazer a consulta de dados (query) e escolher, para cada um, entre as 5 queries solicitadas no projeto.<br>
Todas as queries são executadas através dos drivers dos bancos para python, e os resultados são mostrados em uma tabela (e em grafo HTML para o Neo4J).

# Descrição dos Bancos

Para cada banco não relacional, serão descritos: estrutura dos dados armazenados e queries utilizadas.

## MongoDB

### Descrição das Coleções

- Aluno
```
{
    "_id": (ObjectID),
    "ra": (Int32),
    "id_curso": (Int32),
    "nome": (String),
    "email": (String),
    "telefone": (String),
    "grupo_tcc": (Int32),
    "cursa": Array<{
                        "id_disciplina": (ObjectID),
                        "codigo_disciplina": (String),
                        "semestre": (Int32),
                        "ano": (Int32),
                        "media": (Double),
                        "faltas": (Int32)
             }>
}
```

- Curso
```
{
    "_id": (ObjectID),
    "id_curso": (Int32),
    "nome_departamento": (String),
    "nome": (String),
    "horas_complementares": (String),
    "faltas": (String),
    "matriz_curricular": Array<{
                                    "id_disciplina": (ObjectID),
                                    "codigo_disciplina": (String),
                         }>
}
```

- Departamento
```
{
    "_id": (ObjectID),
    "nome_departamento": (String),
    "chefe": (ObjectID)
}
```

- Disciplina
```
{
    "_id": (ObjectID),
    "codigo_disciplina": (String),
    "nome_departamento": (String),
    "nome": (String),
    "carga_horaria": (String)
}
```

- Professor
```
{
    "_id": (ObjectID),
    "id": (Int32),
    "nome": (String),
    "nome_departamento": (String),
    "email": (String),
    "telefone": (String),
    "salario": (String),
    "grupos_tcc": Array<Int32>,
    "leciona": Array<{
                        "id_curso": (Int32),
                        "id_disciplina": (ObjectID),
                        "codigo_disciplina": (String),
                        "semestre": (Int32),
                        "ano": (Int32),
                        "carga_horaria": (String)
                     }>
}
```

### Queries (MongoDB)

1. histórico escolar de qualquer aluno, retornando o código e nome da disciplina, semestre e ano que a disciplina foi cursada e nota final:
```
[
    {
        "$match": {
            "ra": 1 // Insira o RA desejado
        }
    },
    {
        "$unwind": "$cursa"
    },
    {
        "$lookup": {
            "from": "disciplina",
            "localField": "cursa.id_disciplina",
            "foreignField": "_id",
            "as": "disciplina_info"
        }
    },
    {
        "$unwind": "$disciplina_info"
    },
    {
        "$project": {
            "_id": 0,
            "ra": "$ra",
            "codigo_disciplina": "$cursa.codigo_disciplina",
            "nome_disciplina": "$disciplina_info.nome",
            "semestre": "$cursa.semestre",
            "ano": "$cursa.ano",
            "media_final": "$cursa.media"
        }
    },
    {
        "$sort": {
            "ano": 1,
            "semestre": 1
        }
    }
]
```

2. histórico de disciplinas ministradas por qualquer professor, com semestre e ano:
```
[
    {
        "$match": {
            "id": 1 // Insira o ID do professor
        }
    },
    {
        "$unwind": "$leciona"
    },
    {
        "$lookup": {
            "from": "disciplina",
            "localField": "leciona.id_disciplina",
            "foreignField": "_id",
            "as": "disciplina_info"
        }
    },
    {
        "$unwind": "$disciplina_info"
    },
    {
        "$project": {
            "_id": 0,
            "id_professor": "$id",
            "nome_professor": "$nome",
            "codigo_disciplina": "$leciona.codigo_disciplina",
            "nome_disciplina": "$disciplina_info.nome",
            "semestre": "$leciona.semestre",
            "ano": "$leciona.ano"
        }
    },
    {
        "$sort": {
            "ano": 1,
            "semestre": 1
        }
    }
]
```

3. listar alunos que já se formaram (foram aprovados em todos os cursos de uma matriz curricular) em um determinado semestre de um ano:
```
[
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
```

4. listar todos os professores que são chefes de departamento, junto com o nome do departamento:
```
[
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
```

5. saber quais alunos formaram um grupo de TCC e qual professor foi o orientador:
```
[
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
```

## Cassandra

### Descrição das Tabelas

- Tipo "Leciona"
```
leciona_entry (
            id_curso int,
            codigo_disciplina text,
            semestre int,
            ano int,
            carga_horaria double
        )
```

- Tipo "Cursa"
```
cursa_entry (
            codigo_disciplina text,
            semestre int,
            ano int,
            faltas int,
            media double
        )
```

- Aluno
```
aluno (
            ra int PRIMARY KEY,
            id_curso int,
            nome text,
            email text,
            telefone text,
            grupo_tcc int,
            cursa list<frozen<cursa_entry>>
        )
```

- Curso
```
curso (
            id_curso int PRIMARY KEY,
            nome_departamento text,
            nome text,
            horas_complementares int,
            faltas int,
            matriz_curricular list<text>
        )
```

- Departamento
```
departamento (
            nome_departamento text PRIMARY KEY,
            chefe_id int
        )
```

- Disciplina
```
disciplina (
            codigo_disciplina text PRIMARY KEY,
            nome text,
            carga_horaria int,
            nome_departamento text
        )
```

- Professor
```
professor (
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
```

### Queries (Cassandra)

1. histórico escolar de qualquer aluno, retornando o código e nome da disciplina, semestre e ano que a disciplina foi cursada e nota final:
```
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
```

2. histórico de disciplinas ministradas por qualquer professor, com semestre e ano:
```
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
```

3. listar alunos que já se formaram (foram aprovados em todos os cursos de uma matriz curricular) em um determinado semestre de um ano:
```
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
```

4. listar todos os professores que são chefes de departamento, junto com o nome do departamento:
```
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
```

5. saber quais alunos formaram um grupo de TCC e qual professor foi o orientador:
```
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
```

## Neo4J

![Graph](imageurl)

### Descrição dos Nós

- Aluno
```
{
    "ra": (int),
    "id_curso": (int),
    "nome": (string),
    "email": (string),
    "telefone": (string)
}

```

- Curso
```
{
    "id_curso": (int),
    "nome": (string),
    "nome_departamento": (string),
    "horas_complementares": (int),
    "faltas": (int)
}
```

- Departamento
```
{
    "nome_departamento": (string)
}
```

- Disciplina
```
{
    "codigo_disciplina": (string),
    "nome": (string),
    "carga_horaria": (int),
    "nome_departamento": (string)
}
```

- Professor
```
{
    "id": (int),
    "nome": (string),
    "email": (string),
    "telefone": (string),
    "salario": (float),
    "nome_departamento": (string)
}
```

- GrupoTCC
```
{
    "id_grupo": (int)
}
```

### Descrição das Relações

- CURSA (Aluno -> Disciplina)
```
{
    "semestre": (int),
    "ano": (int),
    "media": (float),
    "faltas": (int)
}
```

- LECIONA (Professor -> Disciplina)
```
{
    "semestre": (int),
    "ano": (int),
    "carga_horaria": (int)
}
```

- CHEFE_DE (Professor -> Departamento)
```
{
    "nome_departamento": (string)
}
```

- ORIENTA (Professor -> GrupoTCC)
```
{
    "id_grupo": (int)
}
```

- MEMBRO_DE (Aluno -> GrupoTCC)
```
{
    "id_grupo": (int)
}
```

- INCLUI (Curso -> Disciplina)
```
{
    "codigo_disciplina": (string)
}
```

### Queries (Neo4J)

1. histórico escolar de qualquer aluno, retornando o código e nome da disciplina, semestre e ano que a disciplina foi cursada e nota final:
```
MATCH (a:Aluno {ra: $ra})-[c:CURSA]->(d:Disciplina)
RETURN a.ra AS ra, d.codigo_disciplina AS codigo_disciplina, d.nome AS nome_disciplina,
        c.semestre AS semestre, c.ano AS ano, c.media AS nota_final
ORDER BY c.ano, c.semestre
```

2. histórico de disciplinas ministradas por qualquer professor, com semestre e ano:
```
MATCH (p:Professor {id: $id_professor})-[l:LECIONA]->(d:Disciplina)
RETURN p.id AS id_professor, p.nome AS nome_professor, d.codigo_disciplina AS codigo_disciplina, 
        d.nome AS nome_disciplina, l.semestre AS semestre, l.ano AS ano
ORDER BY l.ano, l.semestre
```

3. listar alunos que já se formaram (foram aprovados em todos os cursos de uma matriz curricular) em um determinado semestre de um ano:
```
MATCH (a:Aluno)-[c:CURSA]->(d:Disciplina)
WHERE c.media >= 5
WITH a, COLLECT(d.codigo_disciplina) AS disciplinas_aprovadas, MAX(c.ano * 10 + c.semestre) AS ultimo_periodo
MATCH (a)-[:CURSA]->(todasDisciplinas:Disciplina)
WITH a, disciplinas_aprovadas, ultimo_periodo, COLLECT(todasDisciplinas.codigo_disciplina) AS todas_disciplinas
WHERE SIZE(disciplinas_aprovadas) = SIZE(todas_disciplinas) AND ALL(disciplina IN todas_disciplinas WHERE disciplina IN disciplinas_aprovadas)
AND ultimo_periodo = $periodo
RETURN a.ra AS ra, a.nome AS nome, ultimo_periodo
ORDER BY a.ra
```

4. listar todos os professores que são chefes de departamento, junto com o nome do departamento:
```
MATCH (p:Professor)-[:CHEFE_DE]->(d:Departamento)
RETURN d.nome_departamento AS nome_departamento, p.nome AS chefe, p.id AS id
ORDER BY d.nome_departamento
```

5. saber quais alunos formaram um grupo de TCC e qual professor foi o orientador:
```
MATCH (g:GrupoTCC)<-[:MEMBRO_DE]-(a:Aluno)
OPTIONAL MATCH (p:Professor)-[:ORIENTA]->(g)
RETURN g.id_grupo AS id_grupo, a.ra AS ra, a.nome AS nome_aluno, p.nome AS orientador
ORDER BY g.id_grupo
```

# Componentes do Grupo

- Cauan Sousa > 24.124.084-5
- Guilherme Justiça > 24.122.045-8
- Gustavo Bagio > 24.122.012-8
- Ruan Turola > 24.122.050-8