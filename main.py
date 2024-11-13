from sql.insert_sql_data import insert_sql_data
from sql.extract_sql_data import extract_sql_data
from no_sql.document_store.insert_mongodb_data import insert_new_mongodb_data, insert_mongodb_data

# Insere os dados no PostgreSQL que está rodando no Docker (mesmo código do projeto do semestre passado)
insert_sql_data()

# Extrai os dados do PostgreSQL e salva em arquivos JSON
extract_sql_data()

# Insere os dados no MongoDB
insert_mongodb_data()