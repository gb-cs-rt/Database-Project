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