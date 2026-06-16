import customtkinter as ctk
from tkinter import messagebox
import datetime
import os
import csv
# Importações para geração de PDF real
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
except ImportError:
    pass
from database import get_relatorio_vendas
from utils import formatar_moeda

def abrir_janela_relatorios():
    janela = ctk.CTkToplevel()
    janela.title("Relatórios e Indicadores - Forno D'Oro")
    janela.geometry("900x900")
    janela.after(10, lambda: janela.focus_force())

    # Controle de atualização automática
    agendamento = None

    def ao_fechar():
        nonlocal agendamento
        if agendamento: janela.after_cancel(agendamento)
        janela.destroy()

    janela.protocol("WM_DELETE_WINDOW", ao_fechar)

    ctk.CTkLabel(janela, text="📊 Relatórios de Gestão", font=("Roboto", 24, "bold")).pack(pady=(20, 10))

    # Filtro de Período
    frame_filtro_main = ctk.CTkFrame(janela, fg_color="transparent")
    frame_filtro_main.pack(fill="x", padx=30, pady=5)
    
    ctk.CTkLabel(frame_filtro_main, text="Selecione o Período:", font=("Roboto", 12, "bold")).pack(side="left", padx=10)
    
    opcoes_periodo = ["Hoje", "Ontem", "Últimos 7 dias", "Este mês", "Mês passado", "Últimos 30 dias", "Período personalizado"]
    menu_periodo = ctk.CTkOptionMenu(frame_filtro_main, values=opcoes_periodo, 
                                     command=lambda v: gerenciar_campos_data(v))
    menu_periodo.pack(side="left", padx=10)

    def obter_datas_atuais():
        """Helper para obter as datas de início e fim baseadas no menu de período."""
        periodo_selecionado = menu_periodo.get()
        hoje = datetime.date.today()
        inicio = fim = hoje

        if periodo_selecionado == "Ontem":
            inicio = fim = hoje - datetime.timedelta(days=1)
        elif periodo_selecionado == "Últimos 7 dias":
            inicio = hoje - datetime.timedelta(days=7)
            fim = hoje
        elif periodo_selecionado == "Este mês":
            inicio = hoje.replace(day=1)
            fim = hoje
        elif periodo_selecionado == "Mês passado":
            fim = hoje.replace(day=1) - datetime.timedelta(days=1)
            inicio = fim.replace(day=1)
        elif periodo_selecionado == "Últimos 30 dias":
            inicio = hoje - datetime.timedelta(days=30)
            fim = hoje
        elif periodo_selecionado == "Período personalizado":
            inicio = converter_data(ent_inicio.get())
            fim = converter_data(ent_fim.get())
        
        return inicio, fim

    def exportar_csv():
        try:
            inicio, fim = obter_datas_atuais()
            if not inicio or not fim:
                messagebox.showwarning("Aviso", "Por favor, defina um período válido antes de exportar.", parent=janela)
                return

            dados = get_relatorio_vendas(inicio.strftime('%Y-%m-%d'), fim.strftime('%Y-%m-%d'))
            caminho = "Relatorio_Vendas_FornoDoro.csv"
            
            # Gerar CSV com BOM para reconhecimento automático de acentos no Excel
            with open(caminho, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(["FORNO D'ORO - RELATÓRIO DE GESTÃO"])
                writer.writerow(["Período", f"{inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}"])
                writer.writerow([])
                writer.writerow(["INDICADOR", "VALOR"])
                writer.writerow(["Faturamento", formatar_moeda(dados['vendas'])])
                writer.writerow(["Lucro Estimado", formatar_moeda(dados['lucro'])])
                writer.writerow(["Total de Pedidos", dados['pedidos']])
                writer.writerow(["Ticket Médio", formatar_moeda(dados['ticket_medio'])])
                writer.writerow(["Pizzas Vendidas", dados['pizzas']])
                writer.writerow(["Horário de Pico", dados['pico_horario']])

            if os.path.exists(caminho):
                try:
                    os.startfile(os.path.abspath(caminho))
                    messagebox.showinfo("Sucesso", "Relatório Excel (CSV) gerado e aberto com sucesso!", parent=janela)
                except Exception as e:
                    messagebox.showwarning("Aviso", f"Relatório gerado em '{caminho}', mas não foi possível abrir automaticamente.\nErro: {e}", parent=janela)
            else:
                raise Exception("Falha na criação")
        except Exception as e:
            messagebox.showerror(
                "Erro ao exportar Excel",
                str(e),
                parent=janela
            )

    def exportar_pdf():
        """Gera um PDF real utilizando ReportLab conforme proximospassos.md"""
        caminho = os.path.abspath("Relatorio_Gerencial_FornoDoro.pdf")
        
        try:
            # 1. Verificação de Dependência
            if 'SimpleDocTemplate' not in globals():
                messagebox.showerror("Erro de Dependência", 
                    "A biblioteca 'reportlab' é necessária para gerar PDFs reais.\n\n"
                    "Por favor, execute o comando abaixo no seu terminal:\n"
                    "pip install reportlab", parent=janela)
                return

            # 2. Obtenção e Validação de Dados
            inicio, fim = obter_datas_atuais()
            if not inicio or not fim:
                messagebox.showwarning("Aviso", "Por favor, selecione um período válido antes de exportar.", parent=janela)
                return

            dados = get_relatorio_vendas(inicio.strftime('%Y-%m-%d'), fim.strftime('%Y-%m-%d'))
            
            # 3. Configuração do Documento
            doc = SimpleDocTemplate(caminho, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []

            # Estilos Adicionais
            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=1, spaceAfter=20, fontSize=18)
            subtitle_style = ParagraphStyle('SubStyle', parent=styles['Heading2'], spaceBefore=15, spaceAfter=10, fontSize=14, textColor=colors.navy)
            normal_style = styles['Normal']

            # --- Cabeçalho ---
            elements.append(Paragraph("RELATÓRIO GERENCIAL - FORNO D'ORO", title_style))
            elements.append(Paragraph(f"<b>Período:</b> {inicio.strftime('%d/%m/%Y')} até {fim.strftime('%d/%m/%Y')}", normal_style))
            elements.append(Paragraph(f"<b>Data de Emissão:</b> {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
            elements.append(Spacer(1, 15))

            # --- Tabela de Indicadores (9 indicadores conforme proximospassos.md) ---
            elements.append(Paragraph("Indicadores de Desempenho", subtitle_style))
            data_indicadores = [
                ["INDICADOR", "VALOR"],
                ["Faturamento", formatar_moeda(dados['vendas'])],
                ["Lucro Estimado", formatar_moeda(dados['lucro'])],
                ["Total de Pedidos", str(dados['pedidos'])],
                ["Ticket Médio", formatar_moeda(dados['ticket_medio'])],
                ["Pizzas Vendidas", str(dados['pizzas'])],
                ["Clientes Ativos", str(dados['clientes_ativos'])],
                ["Novos Clientes", str(dados['clientes_novos'])],
                ["Maior Venda", formatar_moeda(dados['maior_venda'])],
                ["Horário Pico", dados['pico_horario']]
            ]
            
            table_ind = Table(data_indicadores, colWidths=[200, 200])
            table_ind.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            elements.append(table_ind)

            # --- Formas de Pagamento ---
            elements.append(Paragraph("Distribuição de Pagamentos", subtitle_style))
            data_pag = [["Forma de Pagamento", "Qtd Pedidos", "Total"]]
            for p in dados['pagamentos']:
                data_pag.append([p['forma_pagamento'], str(p['COUNT(*)']), formatar_moeda(p['SUM(total)'])])
            
            table_pag = Table(data_pag, colWidths=[150, 100, 150])
            table_pag.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            elements.append(table_pag)

            # --- Top Sabores ---
            elements.append(Paragraph("Top Sabores mais Vendidos", subtitle_style))
            data_sab = [["Sabor", "Quantidade Vendida"]]
            for s in dados['sabores']:
                data_sab.append([s['nome'], str(s['total'])])
            
            table_sab = Table(data_sab, colWidths=[300, 100])
            table_sab.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.chocolate),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            elements.append(table_sab)

            # --- Top Clientes ---
            if dados.get('top_clientes'):
                elements.append(Paragraph("Melhores Clientes do Período", subtitle_style))
                data_cli = [["Cliente", "Pedidos", "Total Gasto"]]
                for c in dados['top_clientes']:
                    data_cli.append([c['nome'], str(c['qtd_pedidos']), formatar_moeda(c['total_gasto'])])
                
                table_cli = Table(data_cli, colWidths=[180, 100, 120])
                table_cli.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.goldenrod),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
                ]))
                elements.append(table_cli)

            # Constrói o PDF
            doc.build(elements)

            if os.path.exists(caminho):
                try:
                    # Abre com o leitor padrão do Windows
                    os.startfile(caminho)
                    messagebox.showinfo("Sucesso", "Relatório PDF gerado e aberto com sucesso!", parent=janela)
                except Exception:
                    messagebox.showwarning("Aviso", f"PDF gerado com sucesso em:\n{caminho}\n\nAbra-o manualmente no seu leitor de PDF.", parent=janela)
            else:
                raise Exception("Falha na criação")

        except PermissionError:
            messagebox.showerror("Erro de Acesso", "Não foi possível gerar o PDF. Feche o arquivo PDF se ele estiver aberto em outro programa e tente novamente.", parent=janela)
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao gerar o relatório PDF:\n{str(e)}", parent=janela)

    btn_excel = ctk.CTkButton(frame_filtro_main, text="Excel", width=60, fg_color="#15803d", command=exportar_csv)
    btn_excel.pack(side="right", padx=5)
    btn_pdf = ctk.CTkButton(frame_filtro_main, text="PDF", width=60, fg_color="#b91c1c", command=exportar_pdf)
    btn_pdf.pack(side="right", padx=5)

    def gerenciar_campos_data(valor):
        print(f"Opção selecionada: {valor}") # Debug conforme proximospassos.md
        if valor == "Período personalizado":
            # Força a exibição do frame de datas antes do wrapper do dashboard
            frame_custom.pack(pady=10, before=frame_dashboard_wrapper)
        else:
            frame_custom.pack_forget()
            atualizar_indicadores()

    def aplicar_mascara_data(event):
        if event.keysym == "BackSpace":
            return
        
        entry = event.widget
        # Remove tudo que não é dígito e limita a 8 números (ddmmyyyy)
        valor = "".join(filter(str.isdigit, entry.get()))[:8]
        
        formatado = ""
        if len(valor) > 0:
            formatado = valor[:2]
            if len(valor) > 2:
                formatado += "/" + valor[2:4]
                if len(valor) > 4:
                    formatado += "/" + valor[4:]
        
        # Atualiza o campo apenas se o valor formatado for diferente do atual
        if entry.get() != formatado:
            entry.delete(0, "end")
            entry.insert(0, formatado)

    # --- FRAME DE DATAS PERSONALIZADAS ---
    frame_custom = ctk.CTkFrame(janela, fg_color="transparent")

    # Container interno para garantir centralização e alinhamento em linha
    container_datas = ctk.CTkFrame(frame_custom, fg_color="transparent")
    container_datas.pack(anchor="center")

    ctk.CTkLabel(container_datas, text="Data inicial:", font=("Roboto", 12, "bold")).pack(side="left", padx=5)
    ent_inicio = ctk.CTkEntry(container_datas, placeholder_text="DD/MM/YYYY", width=110)
    ent_inicio.pack(side="left", padx=5)
    ent_inicio.bind("<KeyRelease>", aplicar_mascara_data)
    
    ctk.CTkLabel(container_datas, text="Data final:", font=("Roboto", 12, "bold")).pack(side="left", padx=5)
    ent_fim = ctk.CTkEntry(container_datas, placeholder_text="DD/MM/YYYY", width=110)
    ent_fim.pack(side="left", padx=5)
    ent_fim.bind("<KeyRelease>", aplicar_mascara_data)
    
    btn_aplicar = ctk.CTkButton(container_datas, text="Filtrar", width=80, fg_color="#1B365D",
                                 command=lambda: atualizar_indicadores(alertar=True))
    btn_aplicar.pack(side="left", padx=10)

    def converter_data(data_str):
        try:
            d, m, y = data_str.split('/')
            return datetime.date(int(y), int(m), int(d))
        except:
            return None

    # Wrapper para o Dashboard (Resolve erro de packing com CTkScrollableFrame)
    frame_dashboard_wrapper = ctk.CTkFrame(janela, fg_color="transparent")
    frame_dashboard_wrapper.pack(fill="both", expand=True, padx=20, pady=10)

    scroll_dashboard = ctk.CTkScrollableFrame(frame_dashboard_wrapper, fg_color="transparent")
    scroll_dashboard.pack(fill="both", expand=True)

    # Container para Grid de Cards
    frame_grid = ctk.CTkFrame(scroll_dashboard, fg_color="transparent")
    frame_grid.pack(fill="x", pady=10)
    frame_grid.columnconfigure((0, 1, 2), weight=1, pad=10)

    def criar_card(parent, row, col, titulo, cor, icon=""):
        card = ctk.CTkFrame(parent, corner_radius=10, border_width=1, border_color=cor)
        card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(card, text=f"{icon} {titulo}", font=("Roboto", 10, "bold")).pack(pady=(10, 0))
        lbl_val = ctk.CTkLabel(card, text="---", font=("Roboto", 18, "bold"), text_color=cor)
        lbl_val.pack(pady=(0, 10))
        return lbl_val

    # Definição dos Cards na Grade
    lbl_vendas = criar_card(frame_grid, 0, 0, "FATURAMENTO", "#22c55e", "💰")
    lbl_lucro = criar_card(frame_grid, 0, 1, "LUCRO ESTIMADO", "#3b82f6", "📈")
    lbl_pedidos = criar_card(frame_grid, 0, 2, "TOTAL PEDIDOS", "#a855f7", "📦")
    
    lbl_ticket = criar_card(frame_grid, 1, 0, "TICKET MÉDIO", "#06b6d4", "🎫")
    lbl_pizzas = criar_card(frame_grid, 1, 1, "PIZZAS VENDIDAS", "#f97316", "🍕")
    lbl_ativos = criar_card(frame_grid, 1, 2, "CLIENTES ATIVOS", "#eab308", "👥")

    lbl_novos = criar_card(frame_grid, 2, 0, "NOVOS CLIENTES", "#10b981", "✨")
    lbl_maior = criar_card(frame_grid, 2, 1, "MAIOR VENDA", "#f43f5e", "🏆")
    lbl_pico = criar_card(frame_grid, 2, 2, "HORÁRIO PICO", "#6366f1", "🕒")

    # Seções de Listas e Detalhes
    frame_detalhes = ctk.CTkFrame(scroll_dashboard, fg_color="transparent")
    frame_detalhes.pack(fill="x", pady=10)
    frame_detalhes.columnconfigure((0, 1, 2), weight=1)

    # Coluna Esquerda: Pagamentos e Tipos
    col_esq = ctk.CTkFrame(frame_detalhes, fg_color="transparent")
    col_esq.grid(row=0, column=0, sticky="nsew", padx=5)
    
    ctk.CTkLabel(col_esq, text="💳 Formas de Pagamento", font=("Roboto", 14, "bold")).pack(anchor="w")
    scroll_pag = ctk.CTkFrame(col_esq, height=150)
    scroll_pag.pack(fill="x", pady=5)

    # Coluna Direita: Sabores Top 10
    col_dir = ctk.CTkFrame(frame_detalhes, fg_color="transparent")
    col_dir.grid(row=0, column=1, sticky="nsew", padx=5)

    ctk.CTkLabel(col_dir, text="🥇 Top 10 Sabores", font=("Roboto", 14, "bold")).pack(anchor="w")
    scroll_sabores = ctk.CTkFrame(col_dir, height=150)
    scroll_sabores.pack(fill="x", pady=5)

    # Coluna Direita (Nova): Top Clientes
    col_top = ctk.CTkFrame(frame_detalhes, fg_color="transparent")
    col_top.grid(row=0, column=2, sticky="nsew", padx=5)

    ctk.CTkLabel(col_top, text="🏆 Top Clientes", font=("Roboto", 14, "bold")).pack(anchor="w")
    scroll_top_clientes = ctk.CTkFrame(col_top, height=150)
    scroll_top_clientes.pack(fill="x", pady=5)

    def atualizar_indicadores(alertar=False):
        nonlocal agendamento
        inicio, fim = obter_datas_atuais()

        if menu_periodo.get() == "Período personalizado":
            data_i, data_f = inicio, fim
            if not data_i or not data_f:
                if alertar:
                    messagebox.showwarning("Campos Vazios", "Por favor, preencha as datas no formato DD/MM/AAAA.", parent=janela)
                return

            # RN: Validar se a data final não é menor que a inicial
            if data_f < data_i:
                if alertar:
                    messagebox.showwarning("Período Inválido", "A data final não pode ser menor que a data inicial.", parent=janela)
                return
            
            inicio, fim = data_i, data_f

        str_inicio = inicio.strftime('%Y-%m-%d')
        str_fim = fim.strftime('%Y-%m-%d')

        # Busca dados no banco
        dados = get_relatorio_vendas(str_inicio, str_fim)
        
        # Atualiza Cards
        lbl_vendas.configure(text=formatar_moeda(dados['vendas']))
        lbl_lucro.configure(text=formatar_moeda(dados['lucro']))
        lbl_pedidos.configure(text=str(dados['pedidos']))
        lbl_ticket.configure(text=formatar_moeda(dados['ticket_medio']))
        lbl_pizzas.configure(text=str(dados['pizzas']))
        lbl_ativos.configure(text=str(dados['clientes_ativos']))
        lbl_novos.configure(text=str(dados['clientes_novos']))
        lbl_maior.configure(text=formatar_moeda(dados['maior_venda']))
        lbl_pico.configure(text=dados['pico_horario'])

        # Atualiza Pagamentos
        for w in scroll_pag.winfo_children(): w.destroy()
        for p in dados['pagamentos']:
            row = ctk.CTkFrame(scroll_pag, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=f"{p['forma_pagamento']}:", font=("Roboto", 11)).pack(side="left")
            ctk.CTkLabel(row, text=f"{p['COUNT(*)']} ped. | {formatar_moeda(p['SUM(total)'])}", font=("Roboto", 11, "bold")).pack(side="right")

        # Atualiza Sabores
        for w in scroll_sabores.winfo_children(): w.destroy()
        medals = ["🥇", "🥈", "🥉"] + ["🔹"]*7
        for i, s in enumerate(dados['sabores']):
            row = ctk.CTkFrame(scroll_sabores, fg_color="transparent")
            row.pack(fill="x", pady=1)
            txt = f"{medals[i]} {s['nome']}"
            ctk.CTkLabel(row, text=txt, font=("Roboto", 11)).pack(side="left")
            ctk.CTkLabel(row, text=str(s['total']), font=("Roboto", 11, "bold")).pack(side="right")

        # Atualiza Top Clientes
        for w in scroll_top_clientes.winfo_children(): w.destroy()
        for i, c in enumerate(dados['top_clientes']):
            row = ctk.CTkFrame(scroll_top_clientes, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=f"{i+1}º {c['nome']}", font=("Roboto", 11)).pack(side="left")
            ctk.CTkLabel(row, text=f"{c['qtd_pedidos']} ped. | {formatar_moeda(c['total_gasto'])}", font=("Roboto", 10, "bold")).pack(side="right")

        # Agendamento para atualização automática (a cada 30 segundos)
        if janela.winfo_exists():
            agendamento = janela.after(30000, atualizar_indicadores)

    # --- INICIALIZAÇÃO FINAL ---
    # Definimos o valor inicial e chamamos a atualização após todos os componentes estarem criados
    menu_periodo.set("Hoje")
    atualizar_indicadores()