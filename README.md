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
