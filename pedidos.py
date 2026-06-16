import customtkinter as ctk
from tkinter import messagebox, Listbox
from database import salvar_pedido, salvar_itens_pedido, buscar_clientes_para_combobox, buscar_pizzas_para_combobox, buscar_cliente_por_id, get_posicao_na_fila
from utils import formatar_moeda, apenas_numeros, limpar_texto, calcular_valor_total, gerar_comanda_texto, calcular_minutos_preparo, calcular_tempo_preparo

def abrir_janela_pedidos():
    janela = ctk.CTkToplevel()
    janela.title("Gestão de Pedidos")
    janela.geometry("900x850")
    # Permitir minimizar e focar corretamente
    janela.after(10, lambda: janela.focus_force())

    # Constantes de Negócio
    TAXA_ENTREGA = 10.0

    NAVY_BLUE = "#1B365D"

    # ---------------- FUNÇÕES ----------------
    itens = []
    
    # Dados para Autocomplete
    lista_clientes_full = buscar_clientes_para_combobox()
    lista_pizzas_full = ["0 | Nenhum | 0.0"] + buscar_pizzas_para_combobox()

    def verificar_requisitos(event=None):
        # RN02: Validar se cliente e itens estão presentes para habilitar finalização
        if ent_cliente.get() and itens:
            btn_finalizar.configure(state="normal")
        else:
            btn_finalizar.configure(state="disabled")

    def limpar_pedido(confirmar=True):
        if confirmar and itens:
            if not messagebox.askyesno("Confirmar", "Deseja cancelar este pedido?", parent=janela):
                return
        
        itens.clear()
        lst_itens.delete(0, "end")
        txt_obs.delete("1.0", "end")
        # Desbloqueia o cliente para um novo pedido (Requisito 2)
        ent_cliente.configure(state="normal")
        ent_cliente.delete(0, "end")
        ent_pizza1.delete(0, "end")
        ent_pizza2.delete(0, "end")
        ent_qtd.delete(0, "end")
        ent_qtd.insert(0, "1")
        var_pagamento.set("PIX")
        var_tipo_pedido.set("Entrega")
        ent_troco.delete(0, "end")
        toggle_troco()
        atualizar_total()

    def atualizar_total():
        total = calcular_valor_total(itens)
        taxa = TAXA_ENTREGA if var_tipo_pedido.get() == "Entrega" else 0.0
        
        # Cálculo da estimativa conforme proximospassos.md
        total_pizzas = sum(item['quantidade'] for item in itens)
        if total_pizzas <= 3:
            tempo_est = total_pizzas * 20
        else:
            tempo_est = 60 + ((total_pizzas - 3) * 10)
        
        # RF04: Exibir subtotal, taxa e total final
        texto_total = (f"Subtotal: {formatar_moeda(total)}\n"
                       f"Entrega: {formatar_moeda(taxa)}\n"
                       f"TOTAL: {formatar_moeda(total + taxa)}\n"
                       f"ESTIMATIVA: {calcular_tempo_preparo(tempo_est)}")
        lbl_total.configure(text=texto_total)
        verificar_requisitos()
        
    def configurar_busca_dinamica(entry, listbox, lista_dados):
        # Função chamada enquanto o usuário digita
        def ao_digitar(event):
            termo = entry.get().lower().strip()

            # Limpa lista atual
            listbox.delete(0, "end")

            # Sem texto = esconder lista
            if not termo:
                listbox.pack_forget()
                return

            # Filtra resultados
            correspondencias = [
                item for item in lista_dados
                if termo in item.lower()
            ]

            # Se encontrou resultados
            if correspondencias:

                # Ajusta altura automaticamente (Reduzido para 4 conforme solicitado)
                altura = min(len(correspondencias), 4)
                listbox.configure(height=altura)

                # Adiciona resultados
                for item in correspondencias:
                    listbox.insert("end", item)

                # Mostra lista apenas quando necessário
                if not listbox.winfo_ismapped():
                    listbox.pack(fill="x", pady=(0, 5))

                listbox.lift()

            else:
                # Nenhum resultado
                listbox.pack_forget()

        # Quando selecionar item
        def ao_selecionar(event):

            if listbox.curselection():

                selecao = listbox.get(listbox.curselection())

                entry.delete(0, "end")
                entry.insert(0, selecao)

                # Esconde lista após selecionar
                listbox.pack_forget()

                verificar_requisitos()

        # Esconde ao perder foco
        def esconder_lista(event=None):
            janela.after(150, lambda: listbox.pack_forget())

        entry.bind("<KeyRelease>", ao_digitar)
        entry.bind("<FocusOut>", esconder_lista)
        listbox.bind("<<ListboxSelect>>", ao_selecionar)

    def adicionar_item():
        try:
            pizza1 = ent_pizza1.get()
            pizza2 = ent_pizza2.get()
            if not pizza1 or "|" not in pizza1:
                messagebox.showwarning("Aviso", "Selecione pelo menos uma pizza válida da lista.", parent=janela)
                return

            qtd_input = ent_qtd.get()
            if not qtd_input.isdigit() or int(qtd_input) <= 0:
                messagebox.showwarning("Aviso", "Quantidade inválida.", parent=janela)
                return

            # Requisito 4: Trava de quantidade máxima de 10 por vez
            quantidade_total = int(qtd_input)
            qtd_a_adicionar = min(quantidade_total, 10)

            # Extração de dados da Pizza 1
            p1_parts = list(map(str.strip, pizza1.split("|")))
            id_pizza1 = int(p1_parts[0])
            nome1 = p1_parts[1]
            preco1 = float(p1_parts[2])

            # RN: Bloquear se o primeiro sabor for "Nenhum" e não houver segundo sabor válido
            if id_pizza1 == 0 and (not pizza2 or "0 |" in pizza2):
                messagebox.showwarning("Aviso", "Selecione pelo menos um sabor válido.", parent=janela)
                return

            id_pizza2 = None
            nome2 = ""
            preco2 = 0.0

            if pizza2 and "|" in pizza2:
                p2_split = list(map(str.strip, pizza2.split("|")))
                if len(p2_split) >= 3 and p2_split[0] != "0":
                    id_pizza2 = int(p2_split[0])
                    nome2 = p2_split[1]
                    preco2 = float(p2_split[2])

            # RN01: Prevalecer o valor da pizza de maior valor (conforme proximospassos.md)
            preco_base = max(preco1, preco2)

            # RN Passo 1.b: Preço base do sistema é para a GRANDE.
            tamanho = seg_tamanho.get()
            if tamanho == "Pequena":
                preco_ajustado = preco_base * 0.70
            elif tamanho == "Média":
                preco_ajustado = preco_base * 0.85
            elif tamanho == "Família":
                preco_ajustado = preco_base * 1.25
            else: # Grande (100%)
                preco_ajustado = preco_base

            item = {
                "id1": id_pizza1,
                "id2": id_pizza2,
                "nome": nome1 if not id_pizza2 else f"{nome1} / {nome2}",
                "tamanho": tamanho,
                "quantidade": qtd_a_adicionar,
                "preco": preco_ajustado
            }
            itens.append(item)
            lst_itens.insert(
                "end",
                f"[{item['tamanho']}] {item['nome']} x{item['quantidade']} - {formatar_moeda(item['preco']*item['quantidade'])}"
            )
            
            # Bloquear troca de cliente enquanto houver pedido em andamento (Requisito 2)
            ent_cliente.configure(state="disabled")
            
            atualizar_total()
            
            # Lógica de "Continuar" para quantidades > 10 (Requisito 4)
            restante = quantidade_total - qtd_a_adicionar
            ent_qtd.delete(0, "end")
            if restante > 0:
                ent_qtd.insert(0, str(restante))
                # Mantém os nomes das pizzas para o usuário clicar em adicionar novamente
            else:
                ent_qtd.insert(0, "1")
                ent_pizza1.delete(0, "end")
                ent_pizza2.delete(0, "end")
            
        except Exception as e:
            print(e)
            messagebox.showerror("Erro", f"Falha ao adicionar item: {e}", parent=janela)

    def salvar_pedido_completo():
        try:
            cliente_selecionado = ent_cliente.get()
            if not cliente_selecionado or "|" not in cliente_selecionado:
                messagebox.showwarning("Aviso", "Selecione um cliente válido da lista.", parent=janela)
                return
            if not itens:
                messagebox.showwarning("Aviso", "Adicione ao menos um item.", parent=janela)
                return
            
            # RN03: Cálculo automático da estimativa conforme proximospassos.md
            total_pizzas_pedido = sum(item['quantidade'] for item in itens)
            if total_pizzas_pedido <= 3:
                tempo_estimado_total = total_pizzas_pedido * 20
            else:
                tempo_estimado_total = 60 + ((total_pizzas_pedido - 3) * 10)
            
            observacao = txt_obs.get("1.0", "end-1c")
            id_cliente = int(cliente_selecionado.split("|")[0])
            
            tipo_pedido = var_tipo_pedido.get()
            taxa = TAXA_ENTREGA if tipo_pedido == "Entrega" else 0.0
            valor_total = calcular_valor_total(itens) + taxa
            
            forma_pagamento = var_pagamento.get()
            troco_para = ent_troco.get().replace(',', '.') if forma_pagamento == "Dinheiro" else ""
            
            # Requisito 1: Validação do troco
            if forma_pagamento == "Dinheiro":
                try:
                    valor_troco = float(troco_para) if troco_para.strip() else 0.0
                    if valor_troco < valor_total:
                        messagebox.showwarning("Aviso", "O valor do troco não pode ser menor que o valor total do pedido", parent=janela)
                        return
                except ValueError:
                    messagebox.showwarning("Aviso", "Valor de troco inválido.", parent=janela)
                    return

            # Salvar pedido com tempo estimado
            id_ped = salvar_pedido(id_cliente, valor_total, tempo_estimado_total, observacao, forma_pagamento, troco_para, tipo_pedido)

            if id_ped:
                sucesso_itens = salvar_itens_pedido(id_ped, itens)
                if sucesso_itens:
                    cliente_completo = buscar_cliente_por_id(id_cliente)
                    if cliente_completo:
                        comanda_texto = gerar_comanda_texto(id_ped, cliente_completo, itens, valor_total, taxa, observacao)
                        nome_arquivo = f"comanda_pedido_{id_ped}.txt"
                        try:
                            with open(nome_arquivo, "w", encoding="utf-8") as f:
                                f.write(comanda_texto)
                        except Exception as e:
                            print(f"Erro ao gerar arquivo: {e}")

                    # Formatação do tempo utilizando a função utilitária
                    tempo_str = calcular_tempo_preparo(tempo_estimado_total)

                    messagebox.showinfo("Sucesso", f"Pedido #{id_ped} enviado para a cozinha!\nEstimativa: {tempo_str}\nTotal: {formatar_moeda(valor_total)}", parent=janela)
                    
                    # Limpeza após sucesso (reseta campos e desbloqueia cliente)
                    limpar_pedido(confirmar=False)
                else:
                    raise Exception("Erro ao salvar os itens no banco de dados.")
            else:
                raise Exception("Erro ao criar registro do pedido no banco de dados.")
                
        except Exception as e:
            print(e)
            messagebox.showerror("Erro", f"Falha ao finalizar pedido: {e}", parent=janela)

    # Inicialização da interface
    janela.after(100, atualizar_total) # Garante que o valor inicial (taxa) apareça

    # ---------------- LAYOUT ----------------
    frame_topo = ctk.CTkFrame(janela, fg_color="transparent")
    frame_topo.pack(pady=10, padx=20, fill="x")
    
    # Container para busca de cliente (Garante posicionamento do autocomplete)
    container_cliente = ctk.CTkFrame(frame_topo, fg_color="transparent")
    container_cliente.pack(fill="x")

    ctk.CTkLabel(container_cliente, text="Selecione Cliente (Nome ou telefone)").pack(anchor="w")
    ent_cliente = ctk.CTkEntry(container_cliente, width=400, placeholder_text="Nome ou telefone...")
    ent_cliente.pack(pady=5)
    lst_clientes = Listbox(container_cliente)

    configurar_busca_dinamica(
    ent_cliente,
    lst_clientes,
    lista_clientes_full
    )

    # Seleção de Tamanho
    lbl_tamanho = ctk.CTkLabel(janela, text="Selecione o Tamanho", font=("Roboto", 12, "bold"))
    lbl_tamanho.pack(pady=(5, 0))
    seg_tamanho = ctk.CTkSegmentedButton(janela, values=["Pequena", "Média", "Grande", "Família"], width=350, height=30)
    seg_tamanho.set("Média")
    seg_tamanho.pack(pady=5)

    frame_pizzas = ctk.CTkFrame(janela, fg_color="transparent")
    frame_pizzas.pack(fill="x", padx=20)

    # Container Sabor 1
    cont_sabor1 = ctk.CTkFrame(frame_pizzas, fg_color="transparent")
    cont_sabor1.pack(fill="x", pady=2)
    
    ctk.CTkLabel(cont_sabor1, text="Sabor 1").pack(anchor="w")
    ent_pizza1 = ctk.CTkEntry(cont_sabor1, placeholder_text="Digite o sabor...")
    ent_pizza1.pack(pady=2, fill="x")
    lst_pizzas1 = Listbox(cont_sabor1, height=3, bg="#FFF8E7", fg="black", borderwidth=0)
    configurar_busca_dinamica(ent_pizza1, lst_pizzas1, lista_pizzas_full)

    # Container Sabor 2
    cont_sabor2 = ctk.CTkFrame(frame_pizzas, fg_color="transparent")
    cont_sabor2.pack(fill="x", pady=2)

    ctk.CTkLabel(cont_sabor2, text="Sabor 2 (Opcional)").pack(anchor="w")
    ent_pizza2 = ctk.CTkEntry(cont_sabor2, placeholder_text="Digite o segundo sabor...")
    ent_pizza2.pack(pady=2, fill="x")
    lst_pizzas2 = Listbox(cont_sabor2, height=3, bg="#FFF8E7", fg="black", borderwidth=0)
    configurar_busca_dinamica(ent_pizza2, lst_pizzas2, lista_pizzas_full)

    frame_baixon = ctk.CTkFrame(janela, fg_color="transparent")
    frame_baixon.pack(fill="x", padx=20, pady=5)
    
    ctk.CTkLabel(frame_baixon, text="Quantidade:").pack(side="left", padx=5)
    ent_qtd = ctk.CTkEntry(frame_baixon, width=60)
    ent_qtd.insert(0, "1")
    ent_qtd.pack(side="left", padx=5)
    
    ctk.CTkButton(frame_baixon, text="➕ ADICIONAR PIZZA", command=adicionar_item, fg_color=NAVY_BLUE).pack(side="right", padx=5)

    # QUADROS REORGANIZADOS (Passo 4.d)
    # Requisito 3: Ajuste de botões para ficarem sempre visíveis (pack side="bottom")
    frame_botoes_final = ctk.CTkFrame(janela, fg_color="transparent")
    frame_botoes_final.pack(side="bottom", pady=10)

    btn_limpar = ctk.CTkButton(frame_botoes_final, text="❌ LIMPAR", height=40, fg_color="#64748b", command=limpar_pedido)
    btn_limpar.pack(side="left", padx=5)

    btn_finalizar = ctk.CTkButton(frame_botoes_final, text="✅ FINALIZAR PEDIDO", height=40, fg_color="#22c55e", state="disabled", command=salvar_pedido_completo)
    btn_finalizar.pack(side="left", padx=5)

    lbl_total = ctk.CTkLabel(janela, text="Total: R$ 0,00", font=("Roboto", 14, "bold"), justify="right")
    lbl_total.pack(side="bottom", pady=5, padx=20, anchor="e")

    frame_resumo = ctk.CTkFrame(janela, fg_color="transparent")
    frame_resumo.pack(pady=5, padx=20, fill="both", expand=True)

    ctk.CTkLabel(frame_resumo, text="Observações (Sem cebola, borda, etc):", font=("Roboto", 11, "bold"), text_color="white").pack(anchor="w", padx=10)
    txt_obs = ctk.CTkTextbox(frame_resumo, height=40, border_width=1, fg_color="transparent", text_color="white")
    txt_obs.pack(padx=10, pady=(0, 5), fill="x")

    lst_itens = Listbox(frame_resumo, height=4, bg="#FFF8E7", fg="black", font=("Roboto", 10))
    lst_itens.pack(pady=(20, 10), padx=10, fill="x")

    # --- SEÇÃO DE PAGAMENTO ---
    ctk.CTkLabel(frame_resumo, text="Forma de Pagamento:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=10)
    var_pagamento = ctk.StringVar(value="PIX")

    def toggle_troco():
        if var_pagamento.get() == "Dinheiro":
            frame_troco.pack(pady=5, padx=10, fill="x")
        else:
            frame_troco.pack_forget()
            ent_troco.delete(0, "end")

    frame_opcoes_pag = ctk.CTkFrame(frame_resumo, fg_color="transparent")
    frame_opcoes_pag.pack(fill="x", padx=10, pady=5)

    for opcao in ["PIX", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"]:
        ctk.CTkRadioButton(frame_opcoes_pag, text=opcao, variable=var_pagamento, value=opcao, command=toggle_troco).pack(side="left", padx=10)

    # --- SEÇÃO DE TIPO DE PEDIDO ---
    ctk.CTkLabel(frame_resumo, text="Tipo do Pedido:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
    var_tipo_pedido = ctk.StringVar(value="Entrega")
    frame_tipo_pedido = ctk.CTkFrame(frame_resumo, fg_color="transparent")
    frame_tipo_pedido.pack(fill="x", padx=10, pady=5)

    ctk.CTkRadioButton(frame_tipo_pedido, text="Entrega", variable=var_tipo_pedido, value="Entrega", command=atualizar_total).pack(side="left", padx=10)
    ctk.CTkRadioButton(frame_tipo_pedido, text="Retirada no Local", variable=var_tipo_pedido, value="Retirada no Local", command=atualizar_total).pack(side="left", padx=10)

    frame_troco = ctk.CTkFrame(frame_resumo, fg_color="transparent")
    ctk.CTkLabel(frame_troco, text="Troco para quanto:").pack(side="left", padx=(0, 5))
    ent_troco = ctk.CTkEntry(frame_troco, placeholder_text="Ex: 50.00", width=100)
    ent_troco.pack(side="left")