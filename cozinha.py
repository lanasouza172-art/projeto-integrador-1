import customtkinter as ctk
import datetime
from database import buscar_pedidos_por_status, atualizar_status_pedido, buscar_itens_com_detalhes
from tkinter import messagebox
from utils import calcular_tempo_preparo

def abrir_janela_cozinha():
    janela = ctk.CTkToplevel()
    janela.title("Fila de Produção - Cozinha")
    janela.geometry("1000x800")
    # Sprint 1.1: Garantir que a janela abra na frente e em primeiro plano
    janela.attributes("-topmost", True)
    janela.after(500, lambda: janela.attributes("-topmost", False)) # Libera após garantir foco
    janela.focus_force()

    # Controle para evitar erros ao fechar a janela
    agendamento = None

    def ao_fechar():
        nonlocal agendamento
        if agendamento: janela.after_cancel(agendamento)
        janela.destroy()

    def carregar_pedidos():
        nonlocal agendamento
        # Cancela agendamento anterior para evitar múltiplas execuções (Manual + Automática)
        if agendamento:
            janela.after_cancel(agendamento)
            
        try:
            # Verifica se a janela ainda existe para evitar erro "invalid command name"
            if not janela.winfo_exists():
                return
            
            # Limpa a fila atual
            for widget in scroll_frame.winfo_children():
                widget.destroy()
            
            pedidos = buscar_pedidos_por_status(['Pendente', 'Preparando'])
            # Corrigido para datetime.now() para evitar o erro de 180min (conflito UTC vs Local)
            agora = datetime.datetime.now()

            for i, ped in enumerate(pedidos, start=1):
                # RN: Cálculo do tempo de preparo baseado na quantidade (conforme proximospassos.md)
                qtd = ped['total_pizzas'] or 0
                if qtd <= 3:
                    minutos_estimados = qtd * 20
                else:
                    minutos_estimados = 60 + ((qtd - 3) * 10)
                
                card = ctk.CTkFrame(scroll_frame, corner_radius=10, border_width=2)
                card.pack(padx=10, pady=10, fill="x")
                
                cor_status = "#DAA520" if ped['status'] in ['Pendente', 'Preparando'] else "#3b82f6"
                
                # Lógica individual de cálculo de tempo
                minutos = 0
                status_texto = f"Estimativa: {calcular_tempo_preparo(minutos_estimados)}"
                
                if ped['status'] == 'Preparando' and ped['data_hora_preparo']:
                    hora_inicio = datetime.datetime.strptime(ped['data_hora_preparo'], '%Y-%m-%d %H:%M:%S')
                    minutos = max(0, int((agora - hora_inicio).total_seconds() // 60))
                    
                    # Proteção conforme proximospassos.md
                    if minutos > 120 or minutos < 0:
                        minutos = 0

                    status_texto += f" | Em preparo há: {minutos}min"
                    
                    if minutos > minutos_estimados:
                        atraso = minutos - minutos_estimados
                        status_texto += f" | Atrasado há: {atraso}min"
                
                itens = buscar_itens_com_detalhes(ped['id'])
                
                # Cabeçalho do Pedido
                header_frame = ctk.CTkFrame(card, fg_color="transparent")
                header_frame.pack(fill="x", padx=20, pady=(10, 5))

                ctk.CTkLabel(header_frame, text=f"Pedido #{ped['id']}", font=("Roboto", 18, "bold"), text_color=cor_status).pack(side="left")
                ctk.CTkLabel(header_frame, text=status_texto, font=("Roboto", 13), text_color="#e11d48" if minutos > minutos_estimados else "white").pack(side="right")

                # Informações exigidas no proximospassos.md
                ctk.CTkLabel(card, text=f"Cliente: {ped['cliente_nome']}", font=("Roboto", 14, "bold"), anchor="w").pack(fill="x", padx=20)
                ctk.CTkLabel(card, text=f"Quantidade de pizzas: {ped['total_pizzas']}", font=("Roboto", 14), anchor="w").pack(fill="x", padx=20)

                itens_frame = ctk.CTkFrame(card, fg_color="transparent")
                itens_frame.pack(fill="x", padx=20, pady=5)
                
                for item in itens:
                    txt_item = f"• [{item['tamanho']}] {item['nome1']}"
                    if item['nome2']: txt_item += f" / {item['nome2']}"
                    ctk.CTkLabel(itens_frame, text=txt_item, font=("Roboto", 13, "bold"), anchor="w").pack(fill="x")

                if ped['observacao'] and ped['observacao'].strip():
                    ctk.CTkLabel(card, text=f"📝 Obs: {ped['observacao']}", 
                                font=("Roboto", 12, "italic"), text_color="#cbd5e1").pack(anchor="w", padx=40, pady=(0,10))

                def mudar_status(p_id=ped['id'], s_atual=ped['status']):
                    # Sprint 3.1: Alterar status final da cozinha para "Pronto"
                    # Isso faz o pedido aparecer na área de entregas
                    novo = "Preparando" if s_atual == "Pendente" else "Pronto"
                    if atualizar_status_pedido(p_id, novo):
                        carregar_pedidos()

                texto_btn = "COMEÇAR" if ped['status'] == 'Pendente' else "FINALIZAR"
                btn_acao = ctk.CTkButton(card, text=texto_btn, width=120, command=mudar_status, fg_color="#22c55e" if texto_btn == "FINALIZAR" else "#3b82f6")
                btn_acao.pack(side="right", padx=20, pady=(0, 15)) # Subir levemente o botão

            # Reagenda a atualização automática a cada 10s para uma sensação de "tempo real"
            if janela.winfo_exists():
                agendamento = janela.after(10000, carregar_pedidos)
            
        except Exception as e:
            print(f"Erro na cozinha: {e}")
            # Apenas exibe erro se a janela ainda existir
            if janela.winfo_exists():
                messagebox.showerror("Erro na Cozinha", f"Falha ao carregar fila: {e}")

    janela.protocol("WM_DELETE_WINDOW", ao_fechar)

    ctk.CTkLabel(janela, text="👨‍🍳 Fila de Pizzas", font=("Roboto", 24, "bold")).pack(pady=20)
    
    btn_refresh = ctk.CTkButton(janela, text="ATUALIZAR FILA", command=carregar_pedidos)
    btn_refresh.pack(pady=5)

    scroll_frame = ctk.CTkScrollableFrame(janela, width=750, height=450)
    scroll_frame.pack(padx=20, pady=20, fill="both", expand=True)

    carregar_pedidos()