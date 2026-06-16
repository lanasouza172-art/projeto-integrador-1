# Documentação de Desenvolvimento - Sistema Pizzaria Forno D'Oro

Este documento detalha as especificações técnicas, requisitos e roteiro de implementação para o software de gestão da **Pizzaria Forno D'Oro**.

## 1. Visão Geral
A solução visa resolver gargalos operacionais no controle de pedidos e estoque, eliminando erros manuais e atrasos em horários de pico.

* **Tecnologia Principal:** Python 3.x
* **Interface Gráfica:** `customtkinter` (Modern UI)
* **Banco de Dados:** SQLite (arquivo local via `database.py`)
* **Identidade Visual:** Utilizar `logo_fornodoro.png` no cabeçalho das telas.

---

## 2. Perfis de Acesso e Segurança
O sistema deve implementar uma tela de login validando as seguintes credenciais:

| Perfil | Usuário | Senha | Permissões |
| :--- | :--- | :--- | :--- |
| **Administrador** | `fornodoro` | `doro123` | Acesso total: Cadastros, Pedidos, Financeiro e Status. |
| **Cozinheiro** | `cozinha` | `forno123` | Visualização da fila de produção (Sem dados financeiros). |
| **Motoboy** | `entrega` | `moto123` | Visualização de endereços e valores a receber. |

---

## 3. Sprint 1: Refatoração e Layout (Interface)
* **Objetivo:** Analisar o código existente e migrar para uma estrutura de classes (POO) utilizando `customtkinter`.
* **Melhorias Propostas:**
    * Implementação de um sistema de "Cards" para pedidos na fila.
    * Uso de `CTkTabview` para separar áreas de Cadastro, Pedidos e Relatórios no perfil Atendente.
    * Padronização de cores baseada na logo (Tons de dourado/terracota).

---

## 4. Sprint 2: Regras de Negócio e Funcionalidades (RF/RN)

### Requisitos Funcionais (RF)
* **RF01 (Pizza Meio a Meio):** Interface para seleção de dois sabores em um único item.
* **RF02 (Busca por Telefone):** Agilizar o atendimento recuperando dados de clientes já cadastrados via input de telefone.
* **RF03 (Gestão de Status):** Botões de ação rápida para alterar o estado do pedido (*Pendente -> Preparando -> Saiu para Entrega -> Entregue*).
* **RF04 (Cálculo de Total):** Soma automática dos itens + Taxa de entrega fixa.

### Regras de Negócio (RN)
* **RN01 (Preço Meio a Meio):** Se selecionados dois sabores, o valor unitário será o da pizza de maior valor.
* **RN02 (Validação de Dados):** O botão "Finalizar Pedido" deve permanecer desabilitado até que Nome, Telefone e Endereço sejam preenchidos.
* **RN03 (Taxa de Entrega):** Valor fixo configurado no banco de dados ou constante no código.

---

## 5. Sugestões de Melhorias (Backlog Futuro)
Para tornar o software ainda mais robusto, sugere-se:
1.  **Controle de Estoque Automatizado:** Subtrair ingredientes (ex: massa, queijo) do banco de dados a cada pedido finalizado.
2.  **Impressão de Comanda:** Gerar um arquivo `.txt` ou PDF formatado para impressoras térmicas (cozinha e motoboy).
3.  **Relatório de Vendas:** Uma aba para o administrador ver o faturamento diário/mensal.
4.  **Notificações Visuais:** Alerta sonoro ou visual quando um novo pedido entrar na fila da cozinha.

---

## 6. Estrutura do Banco de Dados (`database.py`)
Certifique-se de que as tabelas sigam esta lógica mínima:
* `clientes`: id, nome, telefone, endereco, referencia.
* `pedidos`: id, cliente_id, itens, total, status, data_hora.
* `produtos`: id, nome, preco, categoria.