# utils.py
import re
import datetime
from tkinter import messagebox

# ---------------- LIMPEZA E VALIDAÇÃO ----------------

def limpar_texto(texto):
    """Remove espaços extras do começo/fim e caracteres indesejados."""
    if texto:
        return texto.strip()
    return ""

def apenas_numeros(texto):
    """Retorna apenas os dígitos do texto."""
    return "".join(filter(str.isdigit, str(texto)))

def validar_cpf(cpf):
    """Valida se o CPF tem 11 dígitos e somente números."""
    cpf_limpo = apenas_numeros(cpf)
    return len(cpf_limpo) == 11

def validar_campos_obrigatorios(campos_dict):
    """
    Recebe um dicionário {nome_campo: valor} e retorna o primeiro campo vazio.
    Exemplo: validar_campos_obrigatorios({"Nome": nome, "CPF": cpf})
    """
    for nome, valor in campos_dict.items():
        if not valor or not str(valor).strip():
            return f"{nome} é obrigatório."
    return None

# ---------------- FORMATAÇÃO ----------------

def formatar_moeda(valor):
    """
    Formata número como moeda brasileira.
    Entrada: 25.5
    Saída: 'R$ 25,50'
    """
    try:
        # Garante que o valor seja tratado como float, limpando possíveis vírgulas
        v = float(str(valor).replace(',', '.'))
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

def formatar_cpf(cpf_str):
    """Formata uma string de CPF para o padrão XXX.XXX.XXX-XX."""
    cpf_limpo = apenas_numeros(cpf_str)
    if not cpf_limpo:
        return ""
    
    if len(cpf_limpo) <= 3:
        return cpf_limpo
    elif len(cpf_limpo) <= 6:
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:]}"
    elif len(cpf_limpo) <= 9:
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:]}"
    else:
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:11]}"

def formatar_telefone(tel_str):
    """Formata uma string de telefone para o padrão (XX) XXXXX-XXXX ou (XX) XXXX-XXXX."""
    tel_limpo = apenas_numeros(tel_str)
    if not tel_limpo:
        return ""

    if len(tel_limpo) <= 2:
        return f"({tel_limpo}"
    elif len(tel_limpo) <= 6: # (XX) XXXX
        return f"({tel_limpo[:2]}) {tel_limpo[2:]}"
    elif len(tel_limpo) <= 10: # (XX) XXXX-XXXX
        return f"({tel_limpo[:2]}) {tel_limpo[2:6]}-{tel_limpo[6:]}"
    else: # (XX) XXXXX-XXXX
        return f"({tel_limpo[:2]}) {tel_limpo[2:7]}-{tel_limpo[7:11]}"

# ---------------- PEDIDOS ----------------

def calcular_valor_total(itens):
    """
    Recebe lista de itens de pedido:
    itens = [{"preco": 25.0, "quantidade": 2}, ...]
    Retorna o total do pedido.
    """
    total = 0
    for item in itens:
        try:
            total += float(item["preco"]) * int(item["quantidade"])
        except (KeyError, ValueError, TypeError):
            continue
    return total

def calcular_minutos_preparo(itens):
    """
    Calcula o tempo total de preparo em minutos conforme proximospassos.md.
    Regras: Pequena/Média (20min), Grande/Família (30min).
    Preparo em paralelo (Max) para < 5 pizzas. Teto de 60min para >= 5 pizzas.
    """
    # Normaliza itens (converte sqlite3.Row para dict se necessário)
    itens_data = [dict(i) if not isinstance(i, dict) else i for i in itens]
    
    total_pizzas = sum(int(item.get('quantidade', 1)) for item in itens_data)
    if total_pizzas >= 5:
        return 60

    tempos_por_tamanho = {"Pequena": 20, "Média": 20, "Grande": 30, "Família": 30}
    
    max_tempo = 0
    for item in itens_data:
        tamanho = item.get("tamanho", "Média")
        tempo_item = tempos_por_tamanho.get(tamanho, 20)
        if tempo_item > max_tempo:
            max_tempo = tempo_item
            
    return max_tempo

def calcular_tempo_preparo(minutos_totais):
    """Retorna string formatada 'XhYmin' ou 'Ymin' baseada nos minutos totais."""
    if minutos_totais < 60:
        return f"{minutos_totais}min"
    
    horas = minutos_totais // 60
    minutos = minutos_totais % 60
    
    if minutos > 0:
        return f"{horas}h{minutos}min"
    return f"{horas}h"

# ---------------- MENSAGENS ----------------

def exibir_erro(titulo, mensagem):
    messagebox.showerror(titulo, mensagem)

def exibir_info(titulo, mensagem):
    messagebox.showinfo(titulo, mensagem)

def exibir_aviso(titulo, mensagem):
    messagebox.showwarning(titulo, mensagem)

def gerar_comanda_texto(pedido_id, cliente_info, itens_pedido, total_pedido, taxa_entrega, observacao=""):
    """
    Gera o texto formatado para a comanda de um pedido.
    """
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    comanda = f"""
==================================================
          PIZZARIA FORNO D'ORO - COMANDA
==================================================
Pedido ID: {pedido_id}
Data/Hora: {agora}

Cliente: {cliente_info['nome']}
Telefone: {cliente_info['telefone']}
Endereço: {cliente_info['endereco']}, {cliente_info['numero']} - {cliente_info['bairro']}
Referência: {cliente_info['Ponto_Ref'] if cliente_info['Ponto_Ref'] else 'N/A'}

--------------------------------------------------
ITENS DO PEDIDO:
--------------------------------------------------
"""
    for item in itens_pedido:
        comanda += f"[{item.get('tamanho', 'M')}] {item['nome']} (x{item['quantidade']}) - {formatar_moeda(item['preco'])}/un. = {formatar_moeda(item['preco'] * item['quantidade'])}\n"

    comanda += f"""
--------------------------------------------------
Subtotal: {formatar_moeda(total_pedido - taxa_entrega)}
Taxa de Entrega: {formatar_moeda(taxa_entrega)}
TOTAL GERAL: {formatar_moeda(total_pedido)}
==================================================

OBSERVAÇÕES DO PEDIDO:
{observacao if observacao else 'Nenhuma.'}
==================================================
"""
    return comanda