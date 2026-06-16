import sqlite3

def criar_banco_sqlite():
    conn = sqlite3.connect('fornoDoro.db')
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS Usuarios (
            ID_Usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            Login TEXT NOT NULL UNIQUE,
            Senha TEXT NOT NULL,
            Perfil TEXT CHECK (Perfil IN ('Administrador', 'Cozinheiro', 'Motoboy'))
        );

        CREATE TABLE IF NOT EXISTS clientes (
            ID_Cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            endereco TEXT,
            bairro TEXT,
            numero TEXT,
            telefone TEXT UNIQUE NOT NULL,
            Ponto_Ref TEXT,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS Pizza (
            ID_Pizza INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome TEXT NOT NULL,
            Custo_Producao REAL NOT NULL,
            Preco_Venda REAL NOT NULL,
            Ingredientes TEXT
        );

        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            total REAL NOT NULL,
            status TEXT NOT NULL,
            tempo_estimado INTEGER DEFAULT 0,
            observacao TEXT,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes (ID_Cliente)
        );

        CREATE TABLE IF NOT EXISTS itens_pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER,
            produto_id1 INTEGER,
            produto_id2 INTEGER,
            quantidade INTEGER,
            tamanho TEXT,
            preco_unitario REAL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos (id),
            FOREIGN KEY (produto_id1) REFERENCES Pizza (ID_Pizza),
            FOREIGN KEY (produto_id2) REFERENCES Pizza (ID_Pizza)
        );
    """)

    try:
        cursor.execute("""
            INSERT INTO Usuarios (Login, Senha, Perfil)
            VALUES ('fornodoro', 'doro123', 'Administrador')
        """)
        print("Usuário criado com sucesso!")
    except sqlite3.IntegrityError:
        print("Usuário já existe.")

    conn.commit()
    conn.close()
    print("Banco criado com sucesso!")


if __name__ == "__main__":
    criar_banco_sqlite()