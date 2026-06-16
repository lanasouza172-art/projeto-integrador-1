import customtkinter as ctk
from database import buscar_pedidos_por_status, atualizar_status_pedido, ocultar_pedidos_entrega
from tkinter import messagebox
from utils import formatar_moeda, calcular_tempo_preparo
import datetime

def abrir_janela_entregas():
    janela = ctk.CTkToplevel()
    janela.title("Gerenciamento de Entregas")
    janela.geometry("850x650")
    janela.after(10, lambda: janela.focus_force())
    
    TAXA_ENTREGA_CONST = 10.0

    # Controle para evitar erros ao fechar a janela (after script)
    agendamento = None
    ids_ocultos = set()  # Armazena IDs que foram "limpos" da tela nesta sessão

    def ao_fechar():
        nonlocal agendamento
        if agendamento: janela.after_cancel(agendamento)
        janela.destroy()

    janela.protocol("WM_DELETE_WINDOW", ao_fechar)

    def limpar_concluidos():
        if messagebox.askyesno("Confirmar", "Deseja ocultar os pedidos já entregues desta tela?", parent=janela):
            if ocultar_pedidos_entrega(['Entregue']):
                carregar_entregas()

    def limpar_todos_da_tela():
        if messagebox.askyesno("Confirmar", "Deseja realmente limpar TODOS os pedidos da tela de entregas?", parent=janela):
            if ocultar_pedidos_entrega(['Pronto', 'A Caminho', 'Entregue']):
                carregar_entregas()
                messagebox.showinfo("Sucesso", "A tela foi limpa. Os pedidos continuam salvos no banco de dados para fins de relatório.", parent=janela)

    def carregar_entregas(filtro_status="Todos"):
        nonlocal agendamento
        # Cancela agendamento anterior para evitar múltiplas execuções simultâneas
        if agendamento:
            janela.after_cancel(agendamento)
        try:
            if not janela.winfo_exists():
                return

            for widget in scroll_frame.winfo_children():
                widget.destroy()
            
            # Apenas pedidos prontos (finalizados na cozinha) ou em trânsito/concluídos aparecem aqui
            todos_pedidos = buscar_pedidos_por_status(['Pronto', 'A Caminho', 'Entregue'])
            
            # Regra: Apenas pedidos do tipo 'Entrega' aparecem no fluxo de entregas/motoboy
            pedidos = [p for p in todos_pedidos if p['tipo_pedido'] == 'Entrega']

            # Lista de pedidos que ainda não foram entregues para cálculo de posição
            pedidos_ativos = [p for p in todos_pedidos if p['status'] != 'Entregue']

            # Corrigido para datetime.now() para evitar o erro de 180min
            agora = datetime.datetime.now()
            hoje = agora.date()
            ontem = hoje - datetime.timedelta(days=1)

            # Filtro de Status
            if filtro_status != "Todos":
                pedidos = [p for p in pedidos if (p['status'] if p['status'] != "Pendente" and p['status'] != "Preparando" else "Em preparo") == filtro_status or p['status'] == filtro_status]

            for ped in pedidos:
                entrada = datetime.datetime.strptime(ped['data_hora'], '%Y-%m-%d %H:%M:%S')
                data_pedido = entrada.date()
                
                # Agrupamento visual (Simplificado para o card)
                prefixo_data = ""
                if data_pedido == hoje: prefixo_data = "HOJE"
                elif data_pedido == ontem: prefixo_data = "ONTEM"
                else: prefixo_data = data_pedido.strftime("%d/%m")

                hora_feita = ped['data_hora'].split(" ")[1][:5]
                
                # Ajuste conforme proximospassos.md: Tempos independentes por etapa
                if ped['status'] == 'A Caminho' and ped['data_hora_entrega']:
                    ref_hora = datetime.datetime.strptime(ped['data_hora_entrega'], '%Y-%m-%d %H:%M:%S')
                    decorrido = max(0, int((agora - ref_hora).total_seconds() // 60))
                elif ped['status'] == 'Preparando' and ped['data_hora_preparo']:
                    ref_hora = datetime.datetime.strptime(ped['data_hora_preparo'], '%Y-%m-%d %H:%M:%S')
                    decorrido = max(0, int((agora - ref_hora).total_seconds() // 60))
                else:
                    decorrido = 0
                
                # Item 3: Cálculo automático da estimativa de entrega (posição * 10min)
                minutos_estimados = 0
                if ped['status'] != 'Entregue':
                    try:
                        posicao = pedidos_ativos.index(next(p for p in pedidos_ativos if p['id'] == ped['id'])) + 1
                        minutos_estimados = posicao * 10
                    except (StopIteration, ValueError):
                        minutos_estimados = 0
                
                # Define o status de exibição antes de usá-lo no texto
                status_display = ped['status']

                # Lógica de tempos conforme proximospassos.md
                if ped['status'] == 'Pronto':
                    tempo_txt = "Aguardando Motoboy"
                elif ped['status'] == 'A Caminho':
                    tempo_txt = f"Estimativa: {calcular_tempo_preparo(minutos_estimados)} | A caminho há: {decorrido}min"
                    if decorrido > minutos_estimados:
                        tempo_txt += f" | Atrasado há: {decorrido - minutos_estimados}min"
                elif ped['status'] == 'Entregue':
                    tempo_txt = "Pedido Concluído"
                else: tempo_txt = ped['status']
                
                cores = {
                    "Pronto": "#DAA520",
                    "A Caminho": "#3b82f6",
                    "Entregue": "#22c55e"
                }
                
                # Destaque em vermelho se houver atraso real
                atrasado_real = decorrido > minutos_estimados and ped['status'] not in ['Pendente', 'Entregue']
                cor_atual = "#ef4444" if atrasado_real else cores.get(status_display, "gray")

                card = ctk.CTkFrame(scroll_frame, corner_radius=10, border_width=2, border_color=cor_atual)
                card.pack(padx=10, pady=10, fill="x")

                # Tratamento para garantir que o total seja float, mesmo vindo com vírgula do DB
                try:
                    total_float = float(str(ped['total']).replace(',', '.'))
                except (ValueError, TypeError):
                    total_float = 0.0
                
                subtotal = total_float - TAXA_ENTREGA_CONST

                # Formatação da informação de pagamento
                pag_info = f"Pagamento: {ped['forma_pagamento']}"
                if ped['forma_pagamento'] == "Dinheiro":
                    if ped['troco_para'] and ped['troco_para'].strip():
                        pag_info += f" (Troco para: {formatar_moeda(float(str(ped['troco_para']).replace(',', '.')))})"
                    else:
                        pag_info += " (Sem troco)"

                info_texto = (
                    f"[{prefixo_data}] Pedido #{ped['id']} às {hora_feita} (Entrega)\n"
                    f"{tempo_txt}\n"
                    f"Cliente: {ped['cliente_nome']} | Tel: {ped['telefone']}\n"
                    f"Endereço: {ped['endereco']}, {ped['numero']} - {ped['bairro']} (Ref: {ped['referencia'] if ped['referencia'] else 'N/A'})\n"
                    f"{pag_info}\n"
                    f"Subtotal: {formatar_moeda(subtotal)} | Entrega: {formatar_moeda(TAXA_ENTREGA_CONST)}\n"
                    f"TOTAL A RECEBER: {formatar_moeda(total_float)}"
                )
                
                lbl_info = ctk.CTkLabel(card, text=info_texto, font=("Roboto", 13), 
                                        justify="left", anchor="w", text_color="white")
                lbl_info.pack(side="left", padx=20, pady=15)

                # Container de Botões
                btn_frame = ctk.CTkFrame(card, fg_color="transparent")
                btn_frame.pack(side="right", padx=20)

                def atualizar(p_id=ped['id'], novo_s=""):
                    if atualizar_status_pedido(p_id, novo_s):
                        carregar_entregas()

                # Botão "Sair para Entrega" - Só aparece após finalização da cozinha (Status Pronto)
                if status_display == "Pronto":
                    ctk.CTkButton(
                        btn_frame, text="🚚 SAIR PARA ENTREGA", width=150, fg_color="#3b82f6", 
                        command=lambda p=ped['id']: atualizar(p, "A Caminho")
                    ).pack(pady=5)

                # Botão "Entregue"
                if status_display == "A Caminho":
                    ctk.CTkButton(
                        btn_frame, text="✅ ENTREGUE", width=120, fg_color="#22c55e",
                        command=lambda p=ped['id']: atualizar(p, "Entregue")
                    ).pack(pady=5)
                
                if status_display == "Entregue":
                    ctk.CTkLabel(btn_frame, text="CONCLUÍDO", text_color="#22c55e", font=("Roboto", 12, "bold")).pack(pady=5)

            # Reagenda a atualização automática a cada 10s para uma sensação de "tempo real"
            if janela.winfo_exists():
                agendamento = janela.after(10000, lambda: carregar_entregas(filtro_status))
            
        except Exception as e:
            print(f"Erro nas entregas: {e}")

    ctk.CTkLabel(janela, text="🚚 Gestão de Entregas", font=("Roboto", 24, "bold")).pack(pady=20)
    
    frame_topo = ctk.CTkFrame(janela, fg_color="transparent")
    frame_topo.pack(fill="x", padx=20)

    ctk.CTkButton(frame_topo, text="ATUALIZAR LISTA", command=carregar_entregas).pack(side="left", padx=5)
    ctk.CTkButton(frame_topo, text="LIMPAR TODOS", fg_color="#ef4444", command=limpar_todos_da_tela).pack(side="left", padx=5)

    # Filtros rápidos
    frame_filtros = ctk.CTkFrame(janela, fg_color="transparent")
    frame_filtros.pack(fill="x", padx=20, pady=10)
    
    for f in ["Todos", "Pronto", "A Caminho", "Entregue"]:
        ctk.CTkButton(frame_filtros, text=f.upper(), width=100, height=25, 
                      fg_color="#64748b", command=lambda filt=f: carregar_entregas(filt)).pack(side="left", padx=2)

    scroll_frame = ctk.CTkScrollableFrame(janela, width=800, height=450)
    scroll_frame.pack(padx=20, pady=20, fill="both", expand=True)

    carregar_entregas()