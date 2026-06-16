import customtkinter as ctk
from tkinter import messagebox
from database import salvar_cliente, buscar_cliente_por_id, buscar_cliente_por_telefone, atualizar_cliente, excluir_cliente, buscar_cliente_por_cpf
from utils import validar_cpf, limpar_texto, apenas_numeros, formatar_cpf, formatar_telefone


def abrir_janela_cliente():
    janela = ctk.CTkToplevel()
    janela.title("Cadastro de Clientes")
    janela.geometry("850x700") # Aumentado conforme proximospassos.md
    janela.after(10, lambda: janela.focus_force())
    
    NAVY_BLUE = "#1B365D"

    # ---------------- FUNÇÕES ----------------
    def limpar():
        ent_id.configure(state="normal")
        ent_id.delete(0, "end")
        for campo in [ent_nome, ent_cpf, ent_tel, ent_end, ent_bairro, ent_numero, ent_ref]:
            campo.delete(0, "end")
        btn_atualizar.configure(state="disabled")
        btn_excluir.configure(state="disabled")
        lbl_status.configure(text="Formulário limpo.", text_color="gray")
        ent_nome.focus()

    def validar():
        if not limpar_texto(ent_nome.get()):
            return "Nome obrigatório"
        if not validar_cpf(ent_cpf.get()):
            return "CPF inválido (deve conter 11 dígitos numéricos)"
        return None

    def salvar():
        erro = validar()
        if erro:
            messagebox.showwarning("Aviso", erro, parent=janela)
            return

        sucesso = salvar_cliente(
            limpar_texto(ent_nome.get()),
            apenas_numeros(ent_cpf.get()),
            limpar_texto(ent_end.get()),
            limpar_texto(ent_bairro.get()),
            limpar_texto(ent_numero.get()),
            apenas_numeros(ent_tel.get()),
            limpar_texto(ent_ref.get())
        )

        if sucesso:
            messagebox.showinfo("Sucesso", "Cliente cadastrado!", parent=janela)
            limpar()
        else:
            lbl_status.configure(text="Erro ao salvar", text_color="red")

    def buscar(por_telefone=False):
        lbl_status.configure(text="Buscando cliente...", text_color="gray")

        dados = None
        if por_telefone:
            tel = apenas_numeros(ent_tel.get())
            if not tel:
                messagebox.showwarning("Aviso", "Digite o telefone para buscar.", parent=janela)
                return
            dados = buscar_cliente_por_telefone(tel)
        else:
            id_val = ent_id.get()
            if not id_val:
                messagebox.showwarning("Aviso", "Digite um ID para buscar.", parent=janela)
                return
            try:
                dados = buscar_cliente_por_id(int(id_val))
            except ValueError:
                messagebox.showerror("Erro", "O ID deve ser um número.", parent=janela)
                return

        if dados: # type: ignore
            # Limpar e preparar campos
            ent_id.delete(0, "end")
            ent_id.insert(0, dados["ID_Cliente"])
            
            for campo_widget in [ent_nome, ent_cpf, ent_tel, ent_end, ent_bairro, ent_numero, ent_ref]:
                campo_widget.delete(0, "end")

            ent_nome.insert(0, dados["nome"]) # type: ignore
            ent_cpf.insert(0, formatar_cpf(dados["cpf"])) # type: ignore
            ent_tel.insert(0, formatar_telefone(dados["telefone"])) # type: ignore
            ent_end.insert(0, dados["endereco"])
            ent_bairro.insert(0, dados["bairro"])
            ent_numero.insert(0, dados["numero"])
            ent_ref.insert(0, dados["Ponto_Ref"])
            
            btn_atualizar.configure(state="normal")
            btn_excluir.configure(state="normal")
            lbl_status.configure(text="Cliente carregado!", text_color="green")
        else:
            messagebox.showerror("Erro", "Cliente não encontrado.", parent=janela)

    def buscar_por_cpf_cadastro():
        cpf_input = ent_cpf.get()
        cpf_limpo = apenas_numeros(cpf_input)
        
        if not validar_cpf(cpf_limpo):
            messagebox.showwarning("Aviso", "CPF inválido (deve conter 11 dígitos).", parent=janela)
            return
            
        dados = buscar_cliente_por_cpf(cpf_limpo)
        if dados:
            # Limpar e preencher campos automaticamente
            ent_id.delete(0, "end")
            ent_id.insert(0, dados["ID_Cliente"])
            
            for campo_widget in [ent_nome, ent_cpf, ent_tel, ent_end, ent_bairro, ent_numero, ent_ref]:
                campo_widget.delete(0, "end")

            ent_nome.insert(0, dados["nome"])
            ent_cpf.insert(0, formatar_cpf(dados["cpf"]))
            ent_tel.insert(0, formatar_telefone(dados["telefone"]))
            ent_end.insert(0, dados["endereco"])
            ent_bairro.insert(0, dados["bairro"])
            ent_numero.insert(0, dados["numero"])
            ent_ref.insert(0, dados["Ponto_Ref"])
            
            btn_atualizar.configure(state="normal")
            btn_excluir.configure(state="normal")
            lbl_status.configure(text="Cliente carregado!", text_color="green")
        else:
            messagebox.showerror("Erro", "CPF não encontrado", parent=janela)

    def atualizar():
        if not ent_id.get():
            return

        if messagebox.askyesno("Confirmar", "Atualizar cliente?", parent=janela):
            sucesso = atualizar_cliente(
                int(ent_id.get()),
                limpar_texto(ent_nome.get()),
                apenas_numeros(ent_cpf.get()),
                limpar_texto(ent_end.get()),
                limpar_texto(ent_bairro.get()),
                limpar_texto(ent_numero.get()),
                apenas_numeros(ent_tel.get()),
                limpar_texto(ent_ref.get())
            )
            if sucesso:
                messagebox.showinfo("Sucesso", "Atualizado!", parent=janela)
                limpar()

    def excluir():
        if not ent_id.get():
            return
        if messagebox.askyesno("Confirmar", "Excluir cliente?", parent=janela):
            if excluir_cliente(int(ent_id.get())):
                messagebox.showinfo("Sucesso", "Excluído!", parent=janela)
                limpar()

    # ----------------- MÁSCARAS DE ENTRADA ----------------

    def on_key_release_cpf(event):
        current_text = ent_cpf.get()
        formatted_text = formatar_cpf(current_text)
        if current_text != formatted_text:
            ent_cpf.delete(0, "end")
            ent_cpf.insert(0, formatted_text)

    def on_key_release_telefone(event):
        current_text = ent_tel.get()
        formatted_text = formatar_telefone(current_text)
        if current_text != formatted_text:
            ent_tel.delete(0, "end")
            ent_tel.insert(0, formatted_text)

    # ---------------- LAYOUT ----------------
    titulo = ctk.CTkLabel(janela, text="👥 Clientes", font=("Roboto", 24, "bold"))
    titulo.pack(pady=20)

    # Alterado para ScrollableFrame para garantir que todos os campos apareçam
    frame = ctk.CTkScrollableFrame(janela, width=600, height=400)
    frame.pack(padx=20, pady=10, fill="both", expand=True)

    # ID + BUSCA
    linha_id = ctk.CTkFrame(frame, fg_color="transparent") 
    linha_id.pack(fill="x", padx=20, pady=5)
    ent_id = ctk.CTkEntry(linha_id, placeholder_text="ID para busca", width=120)
    ent_id.pack(side="left", padx=5)
    ctk.CTkButton(linha_id, text="Buscar ID", width=120, command=lambda: buscar(False), fg_color=NAVY_BLUE).pack(side="left")

    # CAMPOS
    def campo(label, com_busca=False, tipo_busca="TEL"):
        ctk.CTkLabel(frame, text=label).pack(anchor="w", padx=20)
        linha = ctk.CTkFrame(frame, fg_color="transparent")
        linha.pack(fill="x", padx=20, pady=5)
        entry = ctk.CTkEntry(linha, width=300) # Adicionado largura para campos de entrada
        entry.pack(side="left", fill="x", expand=True)
        if com_busca:
            txt_btn = "Buscar Telefone" if tipo_busca == "TEL" else "Buscar CPF"
            cmd_btn = (lambda: buscar(True)) if tipo_busca == "TEL" else buscar_por_cpf_cadastro
            cor_btn = "#f59e0b" if tipo_busca == "TEL" else "#f59e0b"
            ctk.CTkButton(linha, text=txt_btn, width=150, fg_color=cor_btn, command=cmd_btn).pack(side="left", padx=(5,0))
        return entry

    ent_nome = campo("Nome")
    ent_cpf = campo("CPF", com_busca=True, tipo_busca="CPF")
    ent_tel = campo("Telefone", com_busca=True) # Implementação RF02
    ent_end = campo("Endereço")
    ent_bairro = campo("Bairro")
    ent_numero = campo("Número")
    ent_ref = campo("Ponto de Referência")

    # Bind key release events for masks
    ent_cpf.bind("<KeyRelease>", on_key_release_cpf)
    ent_tel.bind("<KeyRelease>", on_key_release_telefone)

    # BOTÕES
    botoes = ctk.CTkFrame(janela, fg_color="transparent")
    botoes.pack(pady=15)
    ctk.CTkButton(botoes, text="SALVAR", command=salvar, fg_color="#22c55e", hover_color="#16a34a").grid(row=0, column=0, padx=5)
    btn_atualizar = ctk.CTkButton(botoes, text="ATUALIZAR", state="disabled", command=atualizar, fg_color="#3b82f6", hover_color="#2563eb")
    btn_atualizar.grid(row=0, column=1, padx=5)
    btn_excluir = ctk.CTkButton(botoes, text="EXCLUIR", state="disabled", command=excluir, fg_color="#ef4444", hover_color="#dc2626")
    btn_excluir.grid(row=0, column=2, padx=5)
    ctk.CTkButton(botoes, text="LIMPAR", command=limpar, fg_color="#64748b", hover_color="#475569").grid(row=0, column=3, padx=5)

    lbl_status = ctk.CTkLabel(janela, text="Pronto.", text_color="gray")
    lbl_status.pack(pady=10)