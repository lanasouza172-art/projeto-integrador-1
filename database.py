import sqlite3
import datetime

class Database:
    def __init__(self, db_name="fornoDoro.db"):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Garantir que a tabela Pizza exista antes da migração

        # Tabela de Clientes (RF02) - Expandida para os requisitos da interface
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                ID_Cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT UNIQUE,
                telefone TEXT UNIQUE NOT NULL,
                endereco TEXT NOT NULL,
                bairro TEXT,
                numero TEXT,
                Ponto_Ref TEXT,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabela de Pizza (Sincronizada com sqllite.py)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Pizza (
                ID_Pizza INTEGER PRIMARY KEY AUTOINCREMENT,
                Nome TEXT NOT NULL,
                Custo_Producao REAL NOT NULL,
                Preco_Venda REAL NOT NULL,
                Ingredientes TEXT
            )
        ''')

        # Tabela de Pedidos (RF03, RF04)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_Cliente INTEGER,
                total REAL NOT NULL,
                status TEXT NOT NULL,
                tempo_estimado INTEGER DEFAULT 0,
                observacao TEXT,
                forma_pagamento TEXT,
                troco_para TEXT,
                data_hora DATETIME,
                FOREIGN KEY (ID_Cliente) REFERENCES clientes (ID_Cliente)
            )
        ''')

        # Tabela de Itens Pedidos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS itens_pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER,
                produto_id1 INTEGER,
                produto_id2 INTEGER,
                quantidade INTEGER,
                tamanho TEXT,
                preco_unitario REAL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos (id)
            )
        ''')
        self.conn.commit()

        # Migração de Emergência (Garante que colunas existam se a tabela for antiga)
        self._verificar_e_migrar_pedidos()
        self._verificar_e_migrar_clientes()

    def _verificar_e_migrar_pedidos(self):
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(pedidos)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'status' not in colunas:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN status TEXT NOT NULL DEFAULT 'Pendente'")
        if 'ID_Cliente' not in colunas and 'cliente_id' not in colunas:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN ID_Cliente INTEGER REFERENCES clientes(ID_Cliente)")
        if 'total' not in colunas:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN total REAL NOT NULL DEFAULT 0.0")
        if 'data_hora' not in colunas:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN data_hora DATETIME")
        if 'tempo_estimado' not in colunas:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN tempo_estimado INTEGER DEFAULT 0")
        if 'data_hora_preparo' not in colunas:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN data_hora_preparo DATETIME")
        if 'data_hora_entrega' not in colunas:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN data_hora_entrega DATETIME")
        if 'forma_pagamento' not in colunas:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN forma_pagamento TEXT")
        if 'troco_para' not in colunas:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN troco_para TEXT")
        if 'tipo_pedido' not in colunas:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN tipo_pedido TEXT NOT NULL DEFAULT 'Entrega'")
        if 'oculto_entrega' not in colunas:
            cursor.execute("ALTER TABLE pedidos ADD COLUMN oculto_entrega INTEGER DEFAULT 0")
        self.conn.commit()

    def _verificar_e_migrar_clientes(self):
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(clientes)")
        colunas = [col[1] for col in cursor.fetchall()]
        if 'data_cadastro' not in colunas:
            # SQLite não aceita CURRENT_TIMESTAMP em ALTER TABLE ADD COLUMN em certas versões
            cursor.execute("ALTER TABLE clientes ADD COLUMN data_cadastro DATETIME")
            cursor.execute("UPDATE clientes SET data_cadastro = CURRENT_TIMESTAMP WHERE data_cadastro IS NULL")
        self.conn.commit()

    def salvar_cliente(self, nome, cpf, endereco, bairro, numero, telefone, referencia):
        data_hora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO clientes (nome, cpf, endereco, bairro, numero, telefone, Ponto_Ref, data_cadastro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nome, cpf, endereco, bairro, numero, telefone, referencia, data_hora))
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def buscar_cliente_por_id(self, id_cliente):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE ID_Cliente = ?", (id_cliente,))
        return cursor.fetchone()

    def buscar_cliente_por_telefone(self, telefone):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE telefone = ?", (telefone,))
        return cursor.fetchone()

    def buscar_cliente_por_cpf(self, cpf):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE cpf = ?", (cpf,))
        return cursor.fetchone()

    def atualizar_cliente(self, id_cliente, nome, cpf, endereco, bairro, numero, telefone, referencia):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE clientes SET nome=?, cpf=?, endereco=?, bairro=?, numero=?, telefone=?, Ponto_Ref=?
                WHERE ID_Cliente=?
            ''', (nome, cpf, endereco, bairro, numero, telefone, referencia, id_cliente))
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def excluir_cliente(self, id_cliente):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM clientes WHERE ID_Cliente = ?", (id_cliente,))
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def salvar_pizza(self, nome, custo, preco, ingredientes=""):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO Pizza (Nome, Custo_Producao, Preco_Venda, Ingredientes)
                VALUES (?, ?, ?, ?)
            ''', (nome, custo, preco, ingredientes))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao salvar pizza no banco: {e}")
            return False

    def buscar_pizza(self, id_pizza):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Pizza, Nome, Custo_Producao, Preco_Venda, Ingredientes FROM Pizza WHERE ID_Pizza = ?", (id_pizza,))
        return cursor.fetchone()

    def atualizar_pizza(self, id_pizza, nome, custo, preco, ingredientes):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE Pizza SET Nome=?, Custo_Producao=?, Preco_Venda=?, Ingredientes=?
                WHERE ID_Pizza=?
            ''', (nome, custo, preco, ingredientes, id_pizza))
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def excluir_pizza(self, id_pizza):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM Pizza WHERE ID_Pizza = ?", (id_pizza,))
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_posicao_na_fila(self):
        """Retorna a quantidade de pedidos pendentes ou em preparo para calcular a estimativa."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status IN ('Pendente', 'Preparando')")
        resultado = cursor.fetchone()
        return resultado[0] if resultado else 0

    def salvar_pedido(self, id_cliente, valor_total, tempo_estimado=0, observacao="", forma_pagamento="", troco_para="", tipo_pedido="Entrega"):
        data_hora_local = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO pedidos (ID_Cliente, total, status, tempo_estimado, observacao, forma_pagamento, troco_para, data_hora, tipo_pedido)
                VALUES (?, ?, 'Pendente', ?, ?, ?, ?, ?, ?)
            ''', (id_cliente, valor_total, tempo_estimado, observacao, forma_pagamento, troco_para, data_hora_local, tipo_pedido))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro no banco (salvar_pedido): {e}")
            return None

    def salvar_itens_pedido(self, id_pedido, itens):
        try:
            cursor = self.conn.cursor()
            for item in itens:
                cursor.execute('''
                    INSERT INTO itens_pedidos (pedido_id, produto_id1, produto_id2, quantidade, tamanho, preco_unitario)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (id_pedido, item['id1'], item['id2'], item['quantidade'], item.get('tamanho', 'Média'), item['preco']))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro no banco (salvar_itens): {e}")
            return False

    def buscar_itens_com_detalhes(self, pedido_id):
        cursor = self.conn.cursor()
        query = '''
            SELECT i.*, 
                   p1.Nome as nome1, p1.Ingredientes as ing1,
                   p2.Nome as nome2, p2.Ingredientes as ing2
            FROM itens_pedidos i
            LEFT JOIN Pizza p1 ON i.produto_id1 = p1.ID_Pizza
            LEFT JOIN Pizza p2 ON i.produto_id2 = p2.ID_Pizza
            WHERE i.pedido_id = ?
        '''
        cursor.execute(query, (pedido_id,))
        return cursor.fetchall()

    def buscar_pedidos_por_status(self, lista_status):
        # Busca pedidos com detalhes do cliente para a cozinha/entrega
        cursor = self.conn.cursor()
        placeholders = ','.join(['?'] * len(lista_status))
        # Tenta usar ID_Cliente, mas aceita cliente_id se a migração falhou em renomear
        col_cliente = "ID_Cliente" if "ID_Cliente" in [c[1] for c in cursor.execute("PRAGMA table_info(pedidos)").fetchall()] else "cliente_id"
        
        query = f'''
            SELECT p.*, c.nome as cliente_nome, c.endereco, c.bairro, c.telefone, c.numero, c.Ponto_Ref as referencia,
                   (SELECT SUM(quantidade) FROM itens_pedidos WHERE pedido_id = p.id) as total_pizzas
            FROM pedidos p
            JOIN clientes c ON p.{col_cliente} = c.ID_Cliente
            WHERE p.status IN ({placeholders}) AND p.oculto_entrega = 0
            ORDER BY p.data_hora ASC
        '''
        cursor.execute(query, lista_status)
        return cursor.fetchall()

    def ocultar_pedidos_entrega(self, lista_status):
        try:
            cursor = self.conn.cursor()
            placeholders = ','.join(['?'] * len(lista_status))
            cursor.execute(f"UPDATE pedidos SET oculto_entrega = 1 WHERE status IN ({placeholders}) AND tipo_pedido = 'Entrega'", lista_status)
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def atualizar_status_pedido(self, id_pedido, novo_status):
        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            cursor = self.conn.cursor()
            if novo_status == "Preparando":
                cursor.execute("UPDATE pedidos SET status = ?, data_hora_preparo = ? WHERE id = ?", (novo_status, now_str, id_pedido))
            elif novo_status == "A Caminho":
                # Quando sai para entrega, garante o registro do novo horário independente do tempo de cozinha
                cursor.execute("UPDATE pedidos SET status = ?, data_hora_entrega = ? WHERE id = ?", (novo_status, now_str, id_pedido))
            else:
                cursor.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, id_pedido))
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def excluir_todos_pedidos(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM itens_pedidos")
            cursor.execute("DELETE FROM pedidos")
            # Resetar contadores de ID para começar do 1 novamente
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('pedidos', 'itens_pedidos')")
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def excluir_pedidos_por_status(self, status):
        try:
            cursor = self.conn.cursor()
            # Remove itens primeiro para manter integridade referencial
            cursor.execute("DELETE FROM itens_pedidos WHERE pedido_id IN (SELECT id FROM pedidos WHERE status = ?)", (status,))
            cursor.execute("DELETE FROM pedidos WHERE status = ?", (status,))
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def buscar_clientes_para_combobox(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Cliente, nome, telefone FROM clientes")
        return [f"{r['ID_Cliente']} | {r['nome']} | {r['telefone']}" for r in cursor.fetchall()]

    def buscar_pizzas_para_combobox(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Pizza, Nome, Preco_Venda FROM Pizza")
        return [f"{r['ID_Pizza']} | {r['Nome']} | {r['Preco_Venda']}" for r in cursor.fetchall()]

    def buscar_vendas_por_data(self, data):
        """
        Busca o total de pedidos entregues e o valor total de vendas para uma data específica.
        A data deve estar no formato 'YYYY-MM-DD'.
        """
        cursor = self.conn.cursor()
        query = '''
            SELECT COUNT(*) as total_pedidos, SUM(total) as valor_total_vendas
            FROM pedidos
            WHERE DATE(data_hora) = ? AND status = 'Entregue'
        '''
        cursor.execute(query, (data,))
        return cursor.fetchone()

    def get_relatorio_vendas(self, data_inicio, data_fim):
        cursor = self.conn.cursor()
        params = (data_inicio, data_fim)

        # 1. Faturamento, Total Pedidos, Maior Venda e Clientes que compraram (Ativos)
        cursor.execute("""
            SELECT SUM(total), COUNT(*), MAX(total), COUNT(DISTINCT ID_Cliente)
            FROM pedidos 
            WHERE status = 'Entregue' AND DATE(data_hora) BETWEEN ? AND ?
        """, params)
        res_geral = cursor.fetchone()
        total_vendas = res_geral[0] or 0.0
        total_pedidos = res_geral[1] or 0
        maior_venda = res_geral[2] or 0.0
        clientes_ativos = res_geral[3] or 0

        # 2. Novos Clientes cadastrados no período
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE DATE(data_cadastro) BETWEEN ? AND ?", params)
        novos_clientes = cursor.fetchone()[0] or 0

        # 3. Ticket Médio
        ticket_medio = total_vendas / total_pedidos if total_pedidos > 0 else 0.0

        # 4. Pizzas Vendidas e Custos de Produção
        cursor.execute("""
            SELECT i.quantidade, i.tamanho, i.produto_id1, i.produto_id2,
                   p1.Custo_Producao as custo1, p2.Custo_Producao as custo2
            FROM itens_pedidos i
            JOIN pedidos p ON i.pedido_id = p.id
            LEFT JOIN Pizza p1 ON i.produto_id1 = p1.ID_Pizza
            LEFT JOIN Pizza p2 ON i.produto_id2 = p2.ID_Pizza
            WHERE p.status = 'Entregue' AND DATE(p.data_hora) BETWEEN ? AND ?
        """, params)
        itens = cursor.fetchall()
        
        custo_total = 0.0
        total_pizzas = 0
        multiplicadores = {"Pequena": 0.70, "Média": 0.85, "Grande": 1.0, "Família": 1.25}
        
        for item in itens:
            total_pizzas += item['quantidade']
            c1 = item['custo1'] or 0.0
            c2 = item['custo2'] or 0.0
            custo_base = (c1 + c2) / 2 if item['produto_id2'] else c1
            mult = multiplicadores.get(item['tamanho'], 1.0)
            custo_total += (custo_base * mult) * item['quantidade']

        # 5. Formas de Pagamento (Quantidade e Total por tipo)
        cursor.execute("""
            SELECT forma_pagamento, COUNT(*) as "COUNT(*)", SUM(total) as "SUM(total)"
            FROM pedidos WHERE status = 'Entregue' AND DATE(data_hora) BETWEEN ? AND ?
            GROUP BY forma_pagamento
        """, params)
        pagamentos = [dict(r) for r in cursor.fetchall()]

        # 6. Top 10 Sabores mais vendidos (Contando sabores em meio-a-meio)
        cursor.execute("""
            SELECT nome, SUM(qtd) as total FROM (
                SELECT p1.Nome as nome, SUM(i.quantidade) as qtd
                FROM itens_pedidos i JOIN pedidos p ON i.pedido_id = p.id
                JOIN Pizza p1 ON i.produto_id1 = p1.ID_Pizza
                WHERE p.status = 'Entregue' AND DATE(p.data_hora) BETWEEN ? AND ?
                GROUP BY p1.Nome
                UNION ALL
                SELECT p2.Nome as nome, SUM(i.quantidade) as qtd
                FROM itens_pedidos i JOIN pedidos p ON i.pedido_id = p.id
                JOIN Pizza p2 ON i.produto_id2 = p2.ID_Pizza
                WHERE p.status = 'Entregue' AND i.produto_id2 IS NOT NULL AND DATE(p.data_hora) BETWEEN ? AND ?
                GROUP BY p2.Nome
            ) GROUP BY nome ORDER BY total DESC LIMIT 10
        """, (params[0], params[1], params[0], params[1]))
        sabores = [dict(r) for r in cursor.fetchall()]

        # 7. Horário de Pico
        cursor.execute("""
            SELECT strftime('%H', data_hora) as hora, COUNT(*) as total
            FROM pedidos WHERE status = 'Entregue' AND DATE(data_hora) BETWEEN ? AND ?
            GROUP BY hora ORDER BY total DESC LIMIT 1
        """, params)
        res_pico = cursor.fetchone()
        pico = f"{res_pico[0]}h ({res_pico[1]} ped.)" if res_pico else "N/A"

        # 8. Top 5 Clientes (Conforme proximospassos.md)
        cursor.execute("""
            SELECT c.nome, COUNT(p.id) as qtd_pedidos, SUM(p.total) as total_gasto
            FROM pedidos p
            JOIN clientes c ON p.ID_Cliente = c.ID_Cliente
            WHERE p.status = 'Entregue' AND DATE(p.data_hora) BETWEEN ? AND ?
            GROUP BY p.ID_Cliente
            ORDER BY total_gasto DESC LIMIT 5
        """, params)
        top_clientes = [dict(r) for r in cursor.fetchall()]

        return {
            "vendas": total_vendas,
            "pedidos": total_pedidos,
            "ticket_medio": ticket_medio,
            "pizzas": total_pizzas,
            "clientes_novos": novos_clientes,
            "clientes_ativos": clientes_ativos,
            "custo": custo_total,
            "lucro": total_vendas - custo_total,
            "maior_venda": maior_venda,
            "pagamentos": pagamentos,
            "sabores": sabores,
            "pico_horario": pico,
            "top_clientes": top_clientes
        }

    def get_clientes_por_mes(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT strftime('%m/%Y', data_cadastro) as mes, COUNT(*) as total 
            FROM clientes 
            GROUP BY mes 
            ORDER BY data_cadastro DESC
        """)
        return cursor.fetchall()

# Funções de exportação para compatibilidade com os módulos de interface
db_instance = Database()

def realizar_login(usuario, senha):
    # Validação baseada no arquivo vibe-coding.md e proximospassos.md
    credenciais = {"administrador": ("doro123", "Administrador"), "cozinha": ("forno123", "Cozinheiro"), "entrega": ("moto123", "Motoboy")}
    if usuario in credenciais and credenciais[usuario][0] == senha:
        return credenciais[usuario][1]
    return None

def salvar_cliente(*args): return db_instance.salvar_cliente(*args)
def buscar_cliente_por_id(i): return db_instance.buscar_cliente_por_id(i)
def buscar_cliente_por_telefone(t): return db_instance.buscar_cliente_por_telefone(t)
def buscar_cliente_por_cpf(c): return db_instance.buscar_cliente_por_cpf(c)
def atualizar_cliente(*args): return db_instance.atualizar_cliente(*args)
def excluir_cliente(i): return db_instance.excluir_cliente(i)
def salvar_pizza(*args): return db_instance.salvar_pizza(*args)
def buscar_pizza(i): return db_instance.buscar_pizza(i)
def atualizar_pizza(*args): return db_instance.atualizar_pizza(*args)
def excluir_pizza(i): return db_instance.excluir_pizza(i)
def salvar_pedido(*args): return db_instance.salvar_pedido(*args)
def salvar_itens_pedido(*args): return db_instance.salvar_itens_pedido(*args)
def buscar_pedidos_por_status(s): return db_instance.buscar_pedidos_por_status(s)
def ocultar_pedidos_entrega(s): return db_instance.ocultar_pedidos_entrega(s)
def atualizar_status_pedido(i, s): return db_instance.atualizar_status_pedido(i, s)
def get_posicao_na_fila(): return db_instance.get_posicao_na_fila()
def excluir_todos_pedidos(): return db_instance.excluir_todos_pedidos()
def excluir_pedidos_por_status(s): return db_instance.excluir_pedidos_por_status(s)
def buscar_vendas_por_data(d): return db_instance.buscar_vendas_por_data(d)
def buscar_clientes_para_combobox(): return db_instance.buscar_clientes_para_combobox()
def buscar_pizzas_para_combobox(): return db_instance.buscar_pizzas_para_combobox()
def buscar_itens_com_detalhes(i): return db_instance.buscar_itens_com_detalhes(i)
def get_relatorio_vendas(s, e): return db_instance.get_relatorio_vendas(s, e)
def get_clientes_por_mes(): return db_instance.get_clientes_por_mes()

if __name__ == "__main__":
    print("Banco de dados inicializado com sucesso.")