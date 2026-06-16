import customtkinter as ctk
from tkinter import messagebox
from database import salvar_pizza, buscar_pizza, atualizar_pizza, excluir_pizza
from utils import limpar_texto, apenas_numeros, formatar_moeda

def abrir_janela_pizza():
    janela = ctk.CTkToplevel()
    janela.title("Gestão de Pizzas")
    janela.geometry("600x700")
    janela.after(10, lambda: janela.focus_force())

    # ---------------- FUNÇÕES ----------------
    def limpar():
        ent_id.configure(state="normal")
        ent_id.delete(0, "end")
        ent_id.configure(state="disabled") # Keep ID disabled after clearing
        for campo in [ent_nome, ent_custo, ent_preco]:
            campo.delete(0, "end")
        # Special handling for CTkTextbox
        ent_ingredientes.delete("1.0", "end")
        btn_atualizar.configure(state="disabled")
        btn_excluir.configure(state="disabled")
        lbl_status.configure(text="Pronto para cadastro.", text_color="gray")

    def validar():
        if not limpar_texto(ent_nome.get()):
            return "Nome obrigatório"
        if not ent_custo.get() or not ent_preco.get():
            return "Custo e preço são obrigatórios"
        try:
            float(ent_custo.get().replace(",", "."))
            float(ent_preco.get().replace(",", "."))
        except ValueError:
            return "Custo e preço devem ser números válidos"
        return None

    def salvar():
        erro = validar()
        if erro:
            messagebox.showwarning("Aviso", erro, parent=janela)
            return

        sucesso = salvar_pizza(
            limpar_texto(ent_nome.get()),
            float(ent_custo.get().replace(",", ".")),
            float(ent_preco.get().replace(",", ".")),
            ent_ingredientes.get("1.0", "end-1c")
        )
        if sucesso:
            messagebox.showinfo("Sucesso", "Pizza cadastrada!", parent=janela)
            limpar()
        else:
            lbl_status.configure(text="Erro ao salvar pizza.", text_color="red")

    def buscar():
        if ent_id.cget("state") == "disabled":
            ent_id.configure(state="normal")
            ent_id.focus()
            return

        id_busca = ent_id.get()
        if not id_busca.isdigit():
            messagebox.showwarning("Aviso", "Digite um ID válido", parent=janela)
            return

        resultado = buscar_pizza(int(id_busca))
        if resultado:
            limpar()
            ent_id.configure(state="normal")
            ent_id.insert(0, resultado[0])
            ent_id.configure(state="disabled")

            ent_nome.insert(0, resultado[1])
            ent_custo.insert(0, resultado[2])
            ent_preco.insert(0, resultado[3])
            ent_ingredientes.delete("1.0", "end")
            ent_ingredientes.insert("1.0", resultado[4] if resultado[4] else "")

            btn_atualizar.configure(state="normal")
            btn_excluir.configure(state="normal")
            lbl_status.configure(text=f"Pizza '{resultado[1]}' carregada.", text_color="green")
        else:
            messagebox.showerror("Erro", "Pizza não encontrada", parent=janela)

    def atualizar():
        ent_id.configure(state="normal")
        id_pizza = ent_id.get()
        ent_id.configure(state="disabled")
        if not id_pizza:
            messagebox.showwarning("Aviso", "Busque uma pizza antes de atualizar!", parent=janela)
            return

        erro = validar()
        if erro:
            messagebox.showwarning("Aviso", erro, parent=janela)
            return

        sucesso = atualizar_pizza(
            int(id_pizza),
            limpar_texto(ent_nome.get()),
            float(ent_custo.get().replace(",", ".")),
            float(ent_preco.get().replace(",", ".")),
            ent_ingredientes.get("1.0", "end-1c")
        )
        if sucesso:
            messagebox.showinfo("Sucesso", "Pizza atualizada!", parent=janela)
            limpar()
        else:
            lbl_status.configure(text="Erro ao atualizar pizza.", text_color="red")

    def excluir():
        ent_id.configure(state="normal")
        id_pizza = ent_id.get()
        ent_id.configure(state="disabled")
        if not id_pizza:
            messagebox.showwarning("Aviso", "Busque uma pizza antes de excluir!", parent=janela)
            return

        if messagebox.askyesno("Confirmar", f"Excluir pizza ID {id_pizza}?", parent=janela):
            sucesso = excluir_pizza(int(id_pizza))
            if sucesso:
                messagebox.showinfo("Sucesso", "Pizza excluída!", parent=janela)
                limpar()
            else:
                lbl_status.configure(text="Erro ao excluir pizza.", text_color="red")

    # ---------------- LAYOUT ----------------
    ctk.CTkLabel(janela, text="Gestão de Pizzas", font=("Roboto", 24, "bold")).pack(pady=20)

    frame_form = ctk.CTkFrame(janela, corner_radius=10)
    frame_form.pack(padx=30, pady=10, fill="both", expand=True)

    # ID e Botão Buscar
    ctk.CTkLabel(frame_form, text="ID Pizza (Auto):").pack(anchor="w", padx=20, pady=(10, 0))
    frame_id = ctk.CTkFrame(frame_form, fg_color="transparent")
    frame_id.pack(fill="x", padx=20, pady=5)
    ent_id = ctk.CTkEntry(frame_id, placeholder_text="ID", state="disabled")
    ent_id.pack(side="left", fill="x", expand=True)
    ctk.CTkButton(frame_id, text="Buscar", fg_color="#f59e0b", command=buscar).pack(side="right", padx=5)

    # Campos
    def campo(label, parent):
        ctk.CTkLabel(parent, text=label).pack(anchor="w", padx=20)
        entry = ctk.CTkEntry(parent)
        entry.pack(fill="x", padx=20, pady=5)
        return entry

    ent_nome = campo("Nome da Pizza:", frame_form)
    ent_custo = campo("Custo de Produção (R$):", frame_form)
    ent_preco = campo("Preço de Venda (R$):", frame_form)
    
    ctk.CTkLabel(frame_form, text="Ingredientes:").pack(anchor="w", padx=20)
    ent_ingredientes = ctk.CTkTextbox(frame_form, height=100)
    ent_ingredientes.pack(fill="x", padx=20, pady=5)

    # Botões
    frame_botoes = ctk.CTkFrame(janela, fg_color="transparent")
    frame_botoes.pack(fill="x", padx=30, pady=15)
    frame_botoes.grid_columnconfigure((0,1,2,3), weight=1)

    ctk.CTkButton(frame_botoes, text="SALVAR", fg_color="#22c55e", command=salvar).grid(row=0, column=0, padx=5)
    btn_atualizar = ctk.CTkButton(frame_botoes, text="ATUALIZAR", fg_color="#3b82f6", state="disabled", command=atualizar)
    btn_atualizar.grid(row=0, column=1, padx=5)
    btn_excluir = ctk.CTkButton(frame_botoes, text="EXCLUIR", fg_color="#ef4444", state="disabled", command=excluir)
    btn_excluir.grid(row=0, column=2, padx=5)
    ctk.CTkButton(frame_botoes, text="LIMPAR", fg_color="#64748b", command=limpar).grid(row=0, column=3, padx=5)

    lbl_status = ctk.CTkLabel(janela, text="Pronto para cadastro.", text_color="gray")
    lbl_status.pack(side="bottom", pady=10)