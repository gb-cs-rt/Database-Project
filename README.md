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
