from sql.insert_sql_data import insert_sql_data
from sql.extract_sql_data import extract_sql_data
from no_sql.document_store.insert_mongodb_data import insert_mongodb_data
from no_sql.document_store.mongodb_queries import mongodb_queries
from no_sql.wide_column.insert_cassandra_data import insert_cassandra_data
from no_sql.wide_column.cassandra_queries import cassandra_queries
from no_sql.graph_database.insert_neo4j_data import insert_neo4j_data
from no_sql.graph_database.neo4j_queries import neo4j_queries

# Insere os dados no PostgreSQL que está rodando no Docker (mesmo código do projeto do semestre passado)
insert_sql_data()

# Extrai os dados do PostgreSQL e salva em arquivos JSON
extract_sql_data()

# Insere os dados no MongoDB
insert_mongodb_data()

# Insere os dados no Cassandra
insert_cassandra_data()

# Insere os dados no Neo4J
insert_neo4j_data()

while True:

    print("\n======== SELECIONE O BANCO DE DADOS =======")
    print("1. MongoDB")
    print("2. Cassandra")
    print("3. Neo4J")
    print("0. Sair")
    print("===========================================")
    db = input("Escolha uma opção: ")

    if db == "1":
        mongodb_queries()
    elif db == "2":
        cassandra_queries()
    elif db == "3":
        neo4j_queries()
    elif db == "0":
        break
    else:
        print("Opção inválida!\n")