from neo4j import GraphDatabase
from pyvis.network import Network
import webbrowser
import time

neo4j_uri = "bolt://localhost:7687"
default_user = "neo4j"
default_password = "cc6240admin"

driver = GraphDatabase.driver(neo4j_uri, auth=(default_user, default_password))

# 1. histórico escolar de qualquer aluno, retornando o código e nome da disciplina, semestre e ano que a disciplina foi cursada e nota final

def get_historico_escolar(session, ra):
    print("\n1- Histórico escolar de qualquer aluno, retornando o código e nome da disciplina, semestre e ano que a disciplina foi cursada e nota final\n")

    query = """
    MATCH (a:Aluno {ra: $ra})-[c:CURSA]->(d:Disciplina)
    RETURN a.ra AS ra, d.codigo_disciplina AS codigo_disciplina, d.nome AS nome_disciplina,
           c.semestre AS semestre, c.ano AS ano, c.media AS nota_final
    ORDER BY c.ano, c.semestre
    """
    
    result = session.run(query, ra=ra)
    
    records = []
    for record in result:
        records.append({
            "ra": record["ra"],
            "codigo_disciplina": record["codigo_disciplina"],
            "nome_disciplina": record["nome_disciplina"],
            "semestre": record["semestre"],
            "ano": record["ano"],
            "nota_final": record["nota_final"]
        })

    if records:
        headers = ["RA", "Código Disciplina", "Nome Disciplina", "Semestre", "Ano", "Nota Final"]
        table = [[rec["ra"], rec["codigo_disciplina"], rec["nome_disciplina"], rec["semestre"], rec["ano"], rec["nota_final"]] for rec in records]
        from tabulate import tabulate
        print(tabulate(table, headers=headers, tablefmt="grid"))
    else:
        print("Este aluno não possui histórico escolar.")

def grafo_historico_escolar(session, ra):
    query = """
    MATCH p=(a:Aluno {ra: $ra})-[c:CURSA]->(d:Disciplina)
    RETURN p
    """
    nodes = {}
    edges = []
    
    result = session.run(query, ra=ra)
    
    for record in result:
        for segment in record["p"].relationships:

            start_node = segment.start_node
            end_node = segment.end_node
            
            start_node_id = start_node.element_id
            end_node_id = end_node.element_id
            
            start_label = list(start_node.labels)[0] if start_node.labels else "Node"
            end_label = list(end_node.labels)[0] if end_node.labels else "Node"
            
            # Assign display label and color for start node
            if start_label == "Aluno":
                display_label = f"RA: {start_node.get('ra', 'N/A')}"
                node_color = "lightblue"  # Color for Aluno nodes
            elif start_label == "Disciplina":
                display_label = f"{start_node.get('codigo_disciplina', 'N/A')}"
                node_color = "lightgreen"  # Color for Disciplina nodes
            else:
                display_label = start_label
                node_color = "gray"  # Default color for other nodes
            
            if start_node_id not in nodes:
                nodes[start_node_id] = {
                    "label": display_label,
                    "properties": dict(start_node.items()),
                    "color": node_color
                }
            
            # Assign display label and color for end node
            if end_label == "Aluno":
                display_label = f"RA: {end_node.get('ra', 'N/A')}"
                node_color = "lightblue"  # Color for Aluno nodes
            elif end_label == "Disciplina":
                display_label = f"{end_node.get('codigo_disciplina', 'N/A')}"
                node_color = "lightgreen"  # Color for Disciplina nodes
            else:
                display_label = end_label
                node_color = "gray"  # Default color for other nodes
            
            if end_node_id not in nodes:
                nodes[end_node_id] = {
                    "label": display_label,
                    "properties": dict(end_node.items()),
                    "color": node_color
                }
            
            edge_properties = " | ".join([f"{key}: {value}" for key, value in segment.items()])
            edges.append({
                "source": start_node_id,
                "target": end_node_id,
                "type": segment.type,
                "properties": dict(segment.items()),
                "title": edge_properties
            })

    net = Network(notebook=False, directed=True)

    for node_id, node_data in nodes.items():
        title = " | ".join([f"{key}: {value}" for key, value in node_data["properties"].items()])
        net.add_node(
            node_id, 
            label=node_data["label"], 
            title=title, 
            color=node_data["color"],  # Set node color
            font={"vadjust": -40, "align": "middle"}
        )

    for edge in edges:
        net.add_edge(edge["source"], edge["target"], title=edge["title"], label=edge["type"])

    html_file = "query1.html"
    net.write_html(html_file)
    print(f"Grafo salvo como {html_file}.")
    
    webbrowser.open(html_file)

# 2. histórico de disciplinas ministradas por qualquer professor, com semestre e ano

def get_historico_disciplinas_lecionadas(session, id_professor):
    print("\n2- Histórico de disciplinas ministradas por qualquer professor, com semestre e ano\n")
    
    query = """
    MATCH (p:Professor {id: $id_professor})-[l:LECIONA]->(d:Disciplina)
    RETURN p.id AS id_professor, p.nome AS nome_professor, d.codigo_disciplina AS codigo_disciplina, 
           d.nome AS nome_disciplina, l.semestre AS semestre, l.ano AS ano
    ORDER BY l.ano, l.semestre
    """
    
    result = session.run(query, id_professor=id_professor)
    
    records = []
    for record in result:
        records.append({
            "id_professor": record["id_professor"],
            "nome_professor": record["nome_professor"],
            "codigo_disciplina": record["codigo_disciplina"],
            "nome_disciplina": record["nome_disciplina"],
            "semestre": record["semestre"],
            "ano": record["ano"]
        })

    if records:
        headers = ["ID Professor", "Nome Professor", "Código Disciplina", "Nome Disciplina", "Semestre", "Ano"]
        table = [[rec["id_professor"], rec["nome_professor"], rec["codigo_disciplina"], rec["nome_disciplina"], rec["semestre"], rec["ano"]] for rec in records]
        from tabulate import tabulate
        print(tabulate(table, headers=headers, tablefmt="grid"))
    else:
        print("Este professor não possui histórico de disciplinas ministradas.")

def grafo_historico_disciplinas_lecionadas(session, id_professor):
    query = """
    MATCH p=(prof:Professor {id: $id_professor})-[l:LECIONA]->(d:Disciplina)
    RETURN p
    """
    nodes = {}
    edges = []
    
    result = session.run(query, id_professor=id_professor)
    
    for record in result:
        for segment in record["p"].relationships:

            start_node = segment.start_node
            end_node = segment.end_node
            
            start_node_id = start_node.element_id
            end_node_id = end_node.element_id
            
            start_label = list(start_node.labels)[0] if start_node.labels else "Node"
            end_label = list(end_node.labels)[0] if end_node.labels else "Node"
            
            # Assign display label and color for start node
            if start_label == "Professor":
                display_label = f"ID: {start_node.get('id', 'N/A')}"
                node_color = "lightcoral"  # Color for Professor nodes
            elif start_label == "Disciplina":
                display_label = f"{start_node.get('codigo_disciplina', 'N/A')}"
                node_color = "lightgreen"  # Color for Disciplina nodes
            else:
                display_label = start_label
                node_color = "gray"  # Default color for other nodes
            
            if start_node_id not in nodes:
                nodes[start_node_id] = {
                    "label": display_label,
                    "properties": dict(start_node.items()),
                    "color": node_color
                }
            
            # Assign display label and color for end node
            if end_label == "Professor":
                display_label = f"ID: {end_node.get('id', 'N/A')}"
                node_color = "lightcoral"  # Color for Professor nodes
            elif end_label == "Disciplina":
                display_label = f"{end_node.get('codigo_disciplina', 'N/A')}"
                node_color = "lightgreen"  # Color for Disciplina nodes
            else:
                display_label = end_label
                node_color = "gray"  # Default color for other nodes
            
            if end_node_id not in nodes:
                nodes[end_node_id] = {
                    "label": display_label,
                    "properties": dict(end_node.items()),
                    "color": node_color
                }
            
            edge_properties = " | ".join([f"{key}: {value}" for key, value in segment.items()])
            edges.append({
                "source": start_node_id,
                "target": end_node_id,
                "type": segment.type,
                "properties": dict(segment.items()),
                "title": edge_properties
            })

    net = Network(notebook=False, directed=True)

    for node_id, node_data in nodes.items():
        title = " | ".join([f"{key}: {value}" for key, value in node_data["properties"].items()])
        net.add_node(
            node_id, 
            label=node_data["label"], 
            title=title, 
            color=node_data["color"],  # Set node color
            font={"vadjust": -40, "align": "middle"}
        )

    for edge in edges:
        net.add_edge(edge["source"], edge["target"], title=edge["title"], label=edge["type"])

    html_file = "query2.html"
    net.write_html(html_file)
    print(f"Grafo salvo como {html_file}.")
    
    webbrowser.open(html_file)

# 3. listar alunos que já se formaram (foram aprovados em todos os cursos de uma matriz curricular) em um determinado semestre de um ano

def listar_alunos_formados(session, semestre=None, ano=None):
    print("\n3- Listar alunos que já se formaram (foram aprovados em todas as disciplinas relacionadas a ele) em um determinado semestre de um ano\n")

    if semestre == 0 or ano == 0:
        semestre = None
        ano = None

    # Base query para coletar os alunos que passaram em todas as disciplinas
    query = """
        MATCH (a:Aluno)-[c:CURSA]->(d:Disciplina)
        WHERE c.media >= 5
        WITH a, COLLECT(d.codigo_disciplina) AS disciplinas_aprovadas, MAX(c.ano * 10 + c.semestre) AS ultimo_periodo
        MATCH (a)-[:CURSA]->(todasDisciplinas:Disciplina)
        WITH a, disciplinas_aprovadas, ultimo_periodo, COLLECT(todasDisciplinas.codigo_disciplina) AS todas_disciplinas
        WHERE SIZE(disciplinas_aprovadas) = SIZE(todas_disciplinas) AND ALL(disciplina IN todas_disciplinas WHERE disciplina IN disciplinas_aprovadas)
    """

    # Filter by semester and year if provided
    if semestre is not None and ano is not None:
        periodo = ano * 10 + semestre
        query += """
        AND ultimo_periodo = $periodo
        """

    # Continue to get final details
    query += """
    RETURN a.ra AS ra, a.nome AS nome, ultimo_periodo
    ORDER BY a.ra
    """

    # Execute the query
    parameters = {}
    if semestre is not None and ano is not None:
        parameters = {"periodo": periodo}
    result = session.run(query, parameters)

    # Processar os resultados para a saída da tabela
    records = []
    for record in result:
        records.append({
            "ra": record["ra"],
            "nome": record["nome"],
            "ultimo_semestre": record["ultimo_periodo"] % 10,
            "ultimo_ano": record["ultimo_periodo"] // 10
        })

    # Exibir os resultados em uma tabela
    if records:
        headers = ["RA", "Nome", "Último Semestre", "Último Ano"]
        table = [[rec["ra"], rec["nome"], rec["ultimo_semestre"], rec["ultimo_ano"]] for rec in records]
        from tabulate import tabulate
        print(tabulate(table, headers=headers, tablefmt="grid"))
    else:
        print("Nenhum aluno encontrado que se formou no semestre e ano especificados.")

def grafo_alunos_formados(session, semestre=None, ano=None):
    # Base graph query para coletar os alunos formados
    query = """
    MATCH (a:Aluno)-[c:CURSA]->(d:Disciplina)
    WHERE c.media >= 5
    WITH a, COLLECT(d.codigo_disciplina) AS disciplinas_aprovadas, MAX(c.ano * 10 + c.semestre) AS ultimo_periodo
    MATCH (a)-[:CURSA]->(todasDisciplinas:Disciplina)
    WITH a, disciplinas_aprovadas, ultimo_periodo, COLLECT(todasDisciplinas.codigo_disciplina) AS todas_disciplinas
    WHERE SIZE(disciplinas_aprovadas) = SIZE(todas_disciplinas) AND ALL(disciplina IN todas_disciplinas WHERE disciplina IN disciplinas_aprovadas)
    """

    # Filter by semester and year if provided
    if semestre is not None and ano is not None:
        periodo = ano * 10 + semestre
        query += """
        AND ultimo_periodo = $periodo
        """

    # Continue to find graph paths
    query += """
    MATCH p=(a)-[c:CURSA]->(d)
    RETURN p
    """

    # Execute the query
    parameters = {}
    if semestre is not None and ano is not None:
        parameters = {"periodo": periodo}
    result = session.run(query, parameters)

    # Processar resultados para visualização do grafo
    nodes = {}
    edges = []

    for record in result:
        for segment in record["p"].relationships:
            start_node = segment.start_node
            end_node = segment.end_node
            
            start_node_id = start_node.element_id
            end_node_id = end_node.element_id
            
            start_label = list(start_node.labels)[0] if start_node.labels else "Node"
            end_label = list(end_node.labels)[0] if end_node.labels else "Node"
            
            # Atribuir rótulo e cor para os nós
            if start_label == "Aluno":
                display_label = f"RA: {start_node.get('ra', 'N/A')}"
                node_color = "lightblue"
            elif start_label == "Disciplina":
                display_label = f"{start_node.get('codigo_disciplina', 'N/A')}"
                node_color = "lightgreen"
            else:
                display_label = start_label
                node_color = "gray"
            
            if start_node_id not in nodes:
                nodes[start_node_id] = {
                    "label": display_label,
                    "properties": dict(start_node.items()),
                    "color": node_color
                }
            
            if end_label == "Aluno":
                display_label = f"RA: {end_node.get('ra', 'N/A')}"
                node_color = "lightblue"
            elif end_label == "Disciplina":
                display_label = f"{end_node.get('codigo_disciplina', 'N/A')}"
                node_color = "lightgreen"
            else:
                display_label = end_label
                node_color = "gray"
            
            if end_node_id not in nodes:
                nodes[end_node_id] = {
                    "label": display_label,
                    "properties": dict(end_node.items()),
                    "color": node_color
                }
            
            edge_properties = " | ".join([f"{key}: {value}" for key, value in segment.items()])
            edges.append({
                "source": start_node_id,
                "target": end_node_id,
                "type": segment.type,
                "properties": dict(segment.items()),
                "title": edge_properties
            })

    net = Network(notebook=False, directed=True)

    for node_id, node_data in nodes.items():
        title = " | ".join([f"{key}: {value}" for key, value in node_data["properties"].items()])
        net.add_node(
            node_id, 
            label=node_data["label"], 
            title=title, 
            color=node_data["color"],
            font={"vadjust": -40, "align": "middle"}
        )

    for edge in edges:
        net.add_edge(edge["source"], edge["target"], title=edge["title"], label=edge["type"])

    html_file = "query3.html"
    net.write_html(html_file)
    print(f"Grafo salvo como {html_file}.")
    
    webbrowser.open(html_file)

# 4. listar todos os professores que são chefes de departamento, junto com o nome do departamento

def listar_chefes_departamento(session):
    print("\n4- Listar todos os professores que são chefes de departamento, junto com o nome do departamento\n")

    # Query para buscar chefes de departamento
    query = """
    MATCH (p:Professor)-[:CHEFE_DE]->(d:Departamento)
    RETURN d.nome_departamento AS nome_departamento, p.nome AS chefe, p.id AS id
    ORDER BY d.nome_departamento
    """

    # Executar a consulta
    result = session.run(query)

    # Processar os resultados para a saída da tabela
    records = []
    for record in result:
        records.append({
            "nome_departamento": record["nome_departamento"],
            "chefe": record["chefe"],
            "id": record["id"]
        })

    # Exibir os resultados em uma tabela
    if records:
        headers = ["Nome Departamento", "Nome Chefe", "ID Chefe"]
        table = [[rec["nome_departamento"], rec["chefe"], rec["id"]] for rec in records]
        from tabulate import tabulate
        print(tabulate(table, headers=headers, tablefmt="grid"))
    else:
        print("Nenhum chefe de departamento encontrado.")

def grafo_chefes_departamento(session):
    # Query para buscar chefes de departamento
    query = """
    MATCH p=(prof:Professor)-[:CHEFE_DE]->(d:Departamento)
    RETURN p
    """

    # Executar a consulta
    result = session.run(query)

    # Processar resultados para visualização do grafo
    nodes = {}
    edges = []

    for record in result:
        for segment in record["p"].relationships:
            start_node = segment.start_node
            end_node = segment.end_node
            
            start_node_id = start_node.element_id
            end_node_id = end_node.element_id
            
            start_label = list(start_node.labels)[0] if start_node.labels else "Node"
            end_label = list(end_node.labels)[0] if end_node.labels else "Node"
            
            # Atribuir rótulo e cor para os nós
            if start_label == "Professor":
                display_label = f"ID: {start_node.get('id', 'N/A')}"
                node_color = "lightcoral"  # Cor para professores
            elif start_label == "Departamento":
                display_label = f"{start_node.get('nome_departamento', 'N/A')}"
                node_color = "lightskyblue"  # Cor para departamentos
            else:
                display_label = start_label
                node_color = "gray"
            
            if start_node_id not in nodes:
                nodes[start_node_id] = {
                    "label": display_label,
                    "properties": dict(start_node.items()),
                    "color": node_color
                }
            
            if end_label == "Professor":
                display_label = f"ID: {end_node.get('id', 'N/A')}"
                node_color = "lightcoral"  # Cor para professores
            elif end_label == "Departamento":
                display_label = f"{end_node.get('nome_departamento', 'N/A')}"
                node_color = "lightskyblue"  # Cor para departamentos
            else:
                display_label = end_label
                node_color = "gray"
            
            if end_node_id not in nodes:
                nodes[end_node_id] = {
                    "label": display_label,
                    "properties": dict(end_node.items()),
                    "color": node_color
                }
            
            edge_properties = " | ".join([f"{key}: {value}" for key, value in segment.items()])
            edges.append({
                "source": start_node_id,
                "target": end_node_id,
                "type": segment.type,
                "properties": dict(segment.items()),
                "title": edge_properties
            })

    net = Network(notebook=False, directed=True)

    for node_id, node_data in nodes.items():
        title = " | ".join([f"{key}: {value}" for key, value in node_data["properties"].items()])
        net.add_node(
            node_id, 
            label=node_data["label"], 
            title=title, 
            color=node_data["color"],
            font={"vadjust": -40, "align": "middle"}
        )

    for edge in edges:
        net.add_edge(edge["source"], edge["target"], title=edge["title"], label=edge["type"])

    html_file = "query4.html"
    net.write_html(html_file)
    print(f"Grafo salvo como {html_file}.")
    
    webbrowser.open(html_file)

# 5. saber quais alunos formaram um grupo de TCC e qual professor foi o orientador

def listar_grupos_tcc(session):
    print("\n5- Saber quais alunos formaram um grupo de TCC e qual professor foi o orientador\n")

    # Query para buscar grupos de TCC com membros (alunos) e orientadores (professores)
    query = """
    MATCH (g:GrupoTCC)<-[:MEMBRO_DE]-(a:Aluno)
    OPTIONAL MATCH (p:Professor)-[:ORIENTA]->(g)
    RETURN g.id_grupo AS id_grupo, a.ra AS ra, a.nome AS nome_aluno, p.nome AS orientador
    ORDER BY g.id_grupo
    """

    # Executar a consulta
    result = session.run(query)

    # Processar os resultados para a saída da tabela
    records = []
    for record in result:
        records.append({
            "id_grupo": record["id_grupo"],
            "ra": record["ra"],
            "nome_aluno": record["nome_aluno"],
            "orientador": record["orientador"] if record["orientador"] else "Nenhum"
        })

    # Exibir os resultados em uma tabela
    if records:
        headers = ["ID Grupo", "RA Aluno", "Nome Aluno", "Orientador"]
        table = [[rec["id_grupo"], rec["ra"], rec["nome_aluno"], rec["orientador"]] for rec in records]
        from tabulate import tabulate
        print(tabulate(table, headers=headers, tablefmt="grid"))
    else:
        print("Nenhum grupo de TCC encontrado.")

def grafo_grupos_tcc(session):
    # Query to fetch TCC groups with members (students) and advisors (professors)
    query = """
    MATCH p=(g:GrupoTCC)<-[:MEMBRO_DE]-(a:Aluno)
    OPTIONAL MATCH q=(prof:Professor)-[:ORIENTA]->(g)
    RETURN p, q
    """

    # Execute the query
    result = session.run(query)

    # Process results for graph visualization
    nodes = {}
    edges = []  # Use a list for edges
    seen_edges = set()  # Use a set to track unique edges

    for record in result:
        # Process the relationship between Aluno and GrupoTCC
        if record.get("p"):
            for segment in record["p"].relationships:
                start_node = segment.start_node
                end_node = segment.end_node

                start_node_id = start_node.element_id
                end_node_id = end_node.element_id

                start_label = list(start_node.labels)[0] if start_node.labels else "Node"
                end_label = list(end_node.labels)[0] if end_node.labels else "Node"

                # Assign label and color for nodes
                if start_label == "Aluno":
                    display_label = f"RA: {start_node.get('ra', 'N/A')}"
                    node_color = "lightblue"
                elif start_label == "GrupoTCC":
                    display_label = f"{start_node.get('id_grupo', 'N/A')}"
                    node_color = "lightyellow"
                else:
                    display_label = start_label
                    node_color = "gray"

                if start_node_id not in nodes:
                    nodes[start_node_id] = {
                        "label": display_label,
                        "properties": dict(start_node.items()),
                        "color": node_color
                    }

                if end_label == "Aluno":
                    display_label = f"RA: {end_node.get('ra', 'N/A')}"
                    node_color = "lightblue"
                elif end_label == "GrupoTCC":
                    display_label = f"{end_node.get('id_grupo', 'N/A')}"
                    node_color = "lightyellow"
                else:
                    display_label = end_label
                    node_color = "gray"

                if end_node_id not in nodes:
                    nodes[end_node_id] = {
                        "label": display_label,
                        "properties": dict(end_node.items()),
                        "color": node_color
                    }

                edge_key = (start_node_id, end_node_id, segment.type)
                if edge_key not in seen_edges:
                    edge_properties = " | ".join([f"{key}: {value}" for key, value in segment.items()])
                    seen_edges.add(edge_key)
                    edges.append({
                        "source": start_node_id,
                        "target": end_node_id,
                        "type": segment.type,
                        "properties": dict(segment.items()),
                        "title": edge_properties
                    })

        # Process the relationship between Professor and GrupoTCC (if exists)
        if record.get("q"):
            for segment in record["q"].relationships:
                start_node = segment.start_node
                end_node = segment.end_node

                start_node_id = start_node.element_id
                end_node_id = end_node.element_id

                start_label = list(start_node.labels)[0] if start_node.labels else "Node"
                end_label = list(end_node.labels)[0] if end_node.labels else "Node"

                # Assign label and color for nodes
                if start_label == "Professor":
                    display_label = f"ID: {start_node.get('id', 'N/A')}"
                    node_color = "lightcoral"
                elif start_label == "GrupoTCC":
                    display_label = f"{start_node.get('id_grupo', 'N/A')}"
                    node_color = "lightyellow"
                else:
                    display_label = start_label
                    node_color = "gray"

                if start_node_id not in nodes:
                    nodes[start_node_id] = {
                        "label": display_label,
                        "properties": dict(start_node.items()),
                        "color": node_color
                    }

                if end_label == "Professor":
                    display_label = f"ID: {end_node.get('id', 'N/A')}"
                    node_color = "lightcoral"
                elif end_label == "GrupoTCC":
                    display_label = f"{end_node.get('id_grupo', 'N/A')}"
                    node_color = "lightyellow"
                else:
                    display_label = end_label
                    node_color = "gray"

                if end_node_id not in nodes:
                    nodes[end_node_id] = {
                        "label": display_label,
                        "properties": dict(end_node.items()),
                        "color": node_color
                    }

                edge_key = (start_node_id, end_node_id, segment.type)
                if edge_key not in seen_edges:
                    edge_properties = " | ".join([f"{key}: {value}" for key, value in segment.items()])
                    seen_edges.add(edge_key)
                    edges.append({
                        "source": start_node_id,
                        "target": end_node_id,
                        "type": segment.type,
                        "properties": dict(segment.items()),
                        "title": edge_properties
                    })

    net = Network(notebook=False, directed=True)

    for node_id, node_data in nodes.items():
        title = " | ".join([f"{key}: {value}" for key, value in node_data["properties"].items()])
        net.add_node(
            node_id, 
            label=node_data["label"], 
            title=title, 
            color=node_data["color"],
            font={"vadjust": -40, "align": "middle"}
        )

    for edge in edges:
        net.add_edge(edge["source"], edge["target"], title=edge["title"], label=edge["type"])

    html_file = "query5.html"
    net.write_html(html_file)
    print(f"Graph saved as {html_file}.")
    
    webbrowser.open(html_file)

def neo4j_queries():

    try:
        with driver.session() as session:
            while True:

                print("\n=================  ESCOLHA UMA QUERY (Neo4J)  ==================")
                print("1 - Histórico escolar de qualquer aluno,")
                print("    retornando o código e nome da disciplina,")
                print("    semestre e ano que a disciplina foi cursada e nota final.\n")
                print("2 - Histórico de disciplinas ministradas por qualquer professor,")
                print("    com semestre e ano.\n")
                print("3 - Listar alunos que já se formaram (foram aprovados")
                print("    em todos os cursos de uma matriz curricular) em um")
                print("    determinado semestre de um ano.\n")
                print("4 - Listar todos os professores que são chefes de departamento,")
                print("    junto com o nome do departamento.\n")
                print("5 - Saber quais alunos formaram um grupo de TCC")
                print("    e qual professor foi o orientador.\n")
                print("0 - Voltar")
                print("==================================================================")

                option = input("Escolha uma opção: ")

                if option == "1":
                    ra_aluno = int(input("Digite o RA do aluno: "))
                    get_historico_escolar(session, ra=ra_aluno)
                    grafo_historico_escolar(session, ra=ra_aluno)
                elif option == "2":
                    id_professor = int(input("Digite o ID do professor: "))
                    get_historico_disciplinas_lecionadas(session, id_professor)
                    grafo_historico_disciplinas_lecionadas(session, id_professor)
                elif option == "3":
                    semestre = int(input("Digite o semestre: "))
                    ano = int(input("Digite o ano: "))
                    listar_alunos_formados(session, semestre=semestre, ano=ano)
                    grafo_alunos_formados(session, semestre=semestre, ano=ano)
                elif option == "4":
                    listar_chefes_departamento(session)
                    grafo_chefes_departamento(session)
                elif option == "5":
                    listar_grupos_tcc(session)
                    grafo_grupos_tcc(session)
                elif option == "0":
                    break
                else:
                    print("Opção inválida.")

                time.sleep(1)
    finally:
        driver.close()