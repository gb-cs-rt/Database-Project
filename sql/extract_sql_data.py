import psycopg2
import os
import json
import decimal

# Classe para serializar decimais em JSON
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super().default(o)
    

# Função para extrair os dados do PostgreSQL e salvar em arquivos JSON
def extract_sql_data():

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Conecta ao PostgreSQL
    try:
        conn = psycopg2.connect(password="cc6240", host="localhost", port="5432", database="postgres", user="postgres")
    except Exception as e:
        print("Erro ao conectar ao PostgreSQL:", e)
        return
    
    cursor = conn.cursor()

    # Função para exportar uma tabela para JSON
    def export_table_to_json(table_name):
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
        rows_dict = [dict(zip(colnames, row)) for row in rows]

        if not os.path.exists("sql_data"):
            os.makedirs("sql_data")

        with open(f"sql_data/{table_name.lower()}.json", "w", encoding="utf-8") as f:
            json.dump(rows_dict, f, ensure_ascii=False, indent=4, cls=DecimalEncoder)

    # Exporta todas as tabelas para JSON
    tables = ["Aluno", "ChefeDepartamento", "Cursa", "Curso", "Departamento", "Disciplina", "GrupoTCC", "Leciona", "MatrizCurricular", "Professor"]
    for table in tables:
        export_table_to_json(table)

    cursor.close()
    conn.close()

    print("Dados do PostgreSQL extraídos com sucesso e salvos em arquivos JSON no diretório 'sql_data'.")