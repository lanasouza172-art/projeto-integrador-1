import customtkinter as ctk
from tkinter import messagebox
import os
from PIL import Image

from cliente import abrir_janela_cliente
from pizza import abrir_janela_pizza
from pedidos import abrir_janela_pedidos
from relatorios import abrir_janela_relatorios
from cozinha import abrir_janela_cozinha
from entregas import abrir_janela_entregas  # Garantindo o uso do módulo plural

# ---------------- FUNÇÃO PRINCIPAL ----------------
def abrir_menu(perfil):
    # Configuração Global do Tema Azul Marinho
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    NAVY_BLUE = "#1B365D"

    menu_app = ctk.CTk()
    menu_app.title(f"Forno D'Oro - Sistema de Gestão [{perfil}]")
    menu_app.geometry("1000x600")
    menu_app.resizable(True, True)

    # Logo
    caminho_logo = os.path.join(os.path.dirname(__file__), "logo_fornodoro.png")
    try:
        img_raw = Image.open(caminho_logo)
        # Aumentando para 110px de largura e calculando a altura proporcional
        nova_largura = 110
        nova_altura = int((nova_largura / img_raw.width) * img_raw.height)
        img_logo = ctk.CTkImage(img_raw, size=(nova_largura, nova_altura))
    except:
        img_logo = None

    # ---------------- FUNÇÕES DE NAVEGAÇÃO ----------------
    def fazer_logout():
        if messagebox.askyesno("Sair", "Deseja realmente encerrar a sessão?"):
            menu_app.destroy()

    # ---------------- SIDEBAR ----------------
    sidebar = ctk.CTkFrame(menu_app, width=200, corner_radius=0)
    sidebar.pack(side="left", fill="y")

    if img_logo:
        ctk.CTkLabel(sidebar, image=img_logo, text="").pack(pady=(20,10))
    ctk.CTkLabel(sidebar, text="Forno D'Oro", font=("Roboto", 18, "bold")).pack(pady=10)

    # Botões
    if perfil == "Administrador":
        ctk.CTkButton(sidebar, text="Clientes", command=abrir_janela_cliente,
                       fg_color="transparent", hover_color=NAVY_BLUE).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Pizzas", command=abrir_janela_pizza,
                       fg_color="transparent", hover_color=NAVY_BLUE).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Pedidos", command=abrir_janela_pedidos,
                       fg_color="transparent", hover_color=NAVY_BLUE).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Relatórios", command=abrir_janela_relatorios,
                       fg_color="transparent", hover_color=NAVY_BLUE).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Cozinha", command=abrir_janela_cozinha,
                       fg_color="transparent", hover_color=NAVY_BLUE).pack(pady=5, padx=20, fill="x")
        ctk.CTkButton(sidebar, text="Entregas", command=abrir_janela_entregas,
                       fg_color="transparent", hover_color=NAVY_BLUE).pack(pady=5, padx=20, fill="x")
    
    elif perfil == "Cozinheiro":
        ctk.CTkButton(sidebar, text="Cozinha", command=abrir_janela_cozinha,
                       fg_color="transparent", hover_color=NAVY_BLUE).pack(pady=5, padx=20, fill="x")
    
    elif perfil == "Motoboy":
        ctk.CTkButton(sidebar, text="Entregas", command=abrir_janela_entregas,
                       fg_color="transparent", hover_color=NAVY_BLUE).pack(pady=5, padx=20, fill="x")

    ctk.CTkButton(sidebar, text="Sair do Sistema", command=fazer_logout,
                   fg_color="#ef4444", hover_color="#b91c1c").pack(side="bottom", pady=20, padx=20, fill="x")

    # ---------------- ÁREA CENTRAL ----------------
    conteudo = ctk.CTkFrame(menu_app, corner_radius=15)
    conteudo.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(conteudo, text=f"Bem-vindo(a), {perfil}!", font=("Roboto", 28, "bold")).pack(pady=(50,10))
    ctk.CTkLabel(conteudo, text="Selecione uma opção no menu lateral para começar.", font=("Roboto", 14)).pack(pady=10)

    menu_app.mainloop()