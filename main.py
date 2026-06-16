import customtkinter as ctk
from tkinter import messagebox
from database import realizar_login
from menu import abrir_menu
from utils import limpar_texto

import os
from PIL import Image

# ---------------- CONFIGURAÇÃO ----------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ---------------- JANELA ----------------
janela = ctk.CTk()
janela.title("🍕 Forno D'Oro - Login")
janela.geometry("400x520")

# Centralizar janela
janela.update_idletasks()
largura = janela.winfo_width()
altura = janela.winfo_height()
x = (janela.winfo_screenwidth() // 2) - (largura // 2)
y = (janela.winfo_screenheight() // 2) - (altura // 2)
janela.geometry(f"+{x}+{y}")

# ---------------- LOGO ----------------
caminho_logo = os.path.join(os.path.dirname(__file__), "logor.png")
try:
    imagem_logo = ctk.CTkImage(
        light_image=Image.open(caminho_logo),
        dark_image=Image.open(caminho_logo),
        size=(350, 200)
    )
except Exception as e:
    messagebox.showwarning("Aviso", f"Não foi possível carregar a logo:\n{e}")
    imagem_logo = None

# ---------------- FUNÇÕES ----------------
def acao_login(event=None):
    usuario = limpar_texto(ent_usuario.get())
    senha = limpar_texto(ent_senha.get())

    if not usuario or not senha:
        messagebox.showwarning("Atenção", "Preencha usuário e senha.", parent=janela)
        return

    try:
        perfil = realizar_login(usuario, senha)
        if perfil:
            janela.destroy()
            try:
                abrir_menu(perfil)
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao abrir menu:\n{e}")
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos.", parent=janela)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro inesperado:\n{e}", parent=janela)

def toggle_senha():
    ent_senha.configure(show="" if ent_senha.cget("show")=="*" else "*")

# ---------------- LAYOUT ----------------
frame = ctk.CTkFrame(master=janela, corner_radius=15)
frame.pack(pady=30, padx=30, fill="both", expand=True)

if imagem_logo:
    ctk.CTkLabel(frame, image=imagem_logo, text="").pack(pady=(20,10))

ctk.CTkLabel(frame, text="Forno D'Oro", font=("Roboto", 26, "bold")).pack(pady=10)

ent_usuario = ctk.CTkEntry(frame, placeholder_text="Usuário", height=45)
ent_usuario.pack(pady=12, padx=30, fill="x")

ent_senha = ctk.CTkEntry(frame, placeholder_text="Senha", show="*", height=45)
ent_senha.pack(pady=12, padx=30, fill="x")

ctk.CTkCheckBox(frame, text="Mostrar senha", command=toggle_senha).pack(pady=5)

ctk.CTkButton(frame, text="ENTRAR", height=45, command=acao_login).pack(pady=20, padx=30, fill="x")

# ---------------- UX ----------------
ent_usuario.focus()
janela.bind("<Return>", acao_login)

# ---------------- RODAR ----------------
janela.mainloop()