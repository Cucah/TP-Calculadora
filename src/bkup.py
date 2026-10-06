import customtkinter as ctk
import os
import json
from tkinter import messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_DADOS = os.path.join(BASE_DIR, "dados.json")
ICONE = os.path.join(BASE_DIR, "..", "assets", "icon.ico")

CATEGORIAS = ["Moradia", "Alimentação", "Transporte", "Lazer", "Saúde", "Educação", "Outros"]
COR_ATIVO = ("#2CC985", "#2FA572")
COR_POSITIVO = "#2CC985"
COR_NEGATIVO = "#E5534B"


# ---------- funções auxiliares ----------

def moeda(valor):
    """1500.5 -> 'R$ 1.500,50'"""
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def para_float(texto):
    """Aceita '1500', '1500.50', '1.500,50' e 'R$ 1.500,50'."""
    texto = texto.strip().replace("R$", "").replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    return float(texto)


# ---------- aplicação ----------

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TP Calculadora")
        self.geometry("1000x650")
        self.minsize(900, 600)

        self.update()

        try:
            self.iconbitmap(os.path.join(os.path.dirname(__file__), "assets", "icon.ico"))
        except Exception as e:
            print("Erro icone", e)

        self.dados = self.carregar_dados()

        # só a coluna do conteúdo estica; a sidebar mantém largura fixa
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.paginas = {}
        self.botoes_menu = {}

        self.criar_sidebar()

        self.conteudo = ctk.CTkFrame(self, fg_color="transparent")
        self.conteudo.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        self.conteudo.grid_columnconfigure(0, weight=1)
        self.conteudo.grid_rowconfigure(0, weight=1)

        self.criar_pagina_inicio()
        self.criar_pagina_gastos()
        self.criar_pagina_grafico()

        self.mostrar("Início")
        self.atualizar()

    # ---------- dados ----------

    def carregar_dados(self):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"salario": 0.0, "gastos": []}

    def salvar_dados(self):
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(self.dados, f, ensure_ascii=False, indent=2)

    def total_gastos(self):
        return sum(g["valor"] for g in self.dados["gastos"])

    # ---------- layout base ----------

    def criar_sidebar(self):
        barra = ctk.CTkFrame(self, width=190, corner_radius=0, fg_color="#2b2d2d")
        barra.grid(row=0, column=0, sticky="nsw")
        barra.grid_propagate(False)
        barra.grid_rowconfigure(10, weight=1)

        ctk.CTkLabel(barra, text="TIO PATINHAS", font=("Arial Black", 17)).grid(
            row=0, column=0, pady=(25, 5), padx=15
        )
        ctk.CTkLabel(barra, text="Controle financeiro", font=("Arial", 11), text_color="gray").grid(
            row=1, column=0, pady=(0, 15)
        )

        # linha separadora de verdade (no lugar das "----------")
        ctk.CTkFrame(barra, height=2, fg_color="#444746").grid(
            row=2, column=0, sticky="ew", padx=15, pady=(0, 15)
        )

        for i, nome in enumerate(["Início", "Gastos", "Gráfico"]):
            botao = ctk.CTkButton(
                barra,
                text=nome,
                anchor="w",
                height=40,
                corner_radius=10,
                font=("Arial Black", 13),
                fg_color="transparent",
                hover_color="#3d4040",
                command=lambda n=nome: self.mostrar(n),
            )
            botao.grid(row=3 + i, column=0, sticky="ew", padx=12, pady=4)
            self.botoes_menu[nome] = botao

        ctk.CTkLabel(barra, text="v0.03 private", font=("Arial", 11), text_color="gray").grid(
            row=11, column=0, padx=15, pady=15, sticky="sw"
        )

    def nova_pagina(self, nome):
        pagina = ctk.CTkFrame(self.conteudo, fg_color="transparent")
        pagina.grid(row=0, column=0, sticky="nsew")
        self.paginas[nome] = pagina
        return pagina

    def mostrar(self, nome):
        self.paginas[nome].tkraise()
        for n, botao in self.botoes_menu.items():
            botao.configure(fg_color=COR_ATIVO if n == nome else "transparent")

    def criar_card(self, pai, titulo, coluna):
        card = ctk.CTkFrame(pai, corner_radius=12, fg_color="#2b2d2d")
        card.grid(row=1, column=coluna, sticky="ew", padx=6)
        ctk.CTkLabel(card, text=titulo, font=("Arial", 13), text_color="gray").pack(
            anchor="w", padx=18, pady=(15, 0)
        )
        valor = ctk.CTkLabel(card, text="R$ 0,00", font=("Arial Black", 22))
        valor.pack(anchor="w", padx=18, pady=(2, 15))
        return valor

    # ---------- página: Início ----------

    def criar_pagina_inicio(self):
        p = self.nova_pagina("Início")
        for c in range(3):
            p.grid_columnconfigure(c, weight=1)

        ctk.CTkLabel(p, text="Visão geral", font=("Arial Black", 26)).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 20)
        )

        self.card_salario = self.criar_card(p, "Salário", 0)
        self.card_gastos = self.criar_card(p, "Total de gastos", 1)
        self.card_saldo = self.criar_card(p, "Saldo restante", 2)

        caixa = ctk.CTkFrame(p, corner_radius=12, fg_color="#2b2d2d")
        caixa.grid(row=2, column=0, columnspan=3, sticky="ew", padx=6, pady=25)
        caixa.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(caixa, text="Definir salário", font=("Arial Black", 15)).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(15, 5)
        )
        self.entrada_salario = ctk.CTkEntry(caixa, placeholder_text="Ex.: 3500,00", height=38)
        self.entrada_salario.grid(row=1, column=0, sticky="ew", padx=(18, 10), pady=(0, 18))
        self.entrada_salario.bind("<Return>", lambda e: self.salvar_salario())

        ctk.CTkButton(caixa, text="Salvar", width=110, height=38, command=self.salvar_salario).grid(
            row=1, column=1, padx=(0, 18), pady=(0, 18)
        )

    def salvar_salario(self):
        try:
            valor = para_float(self.entrada_salario.get())
            if valor < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Valor inválido", "Digite um salário válido. Ex.: 3500,00")
            return
        self.dados["salario"] = valor
        self.salvar_dados()
        self.entrada_salario.delete(0, "end")
        self.atualizar()

    # ---------- página: Gastos ----------

    def criar_pagina_gastos(self):
        p = self.nova_pagina("Gastos")
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(p, text="Gastos", font=("Arial Black", 26)).grid(
            row=0, column=0, sticky="w", pady=(0, 20)
        )

        form = ctk.CTkFrame(p, corner_radius=12, fg_color="#2b2d2d")
        form.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        form.grid_columnconfigure(0, weight=3)
        form.grid_columnconfigure(1, weight=1)
        form.grid_columnconfigure(2, weight=1)

        self.entrada_desc = ctk.CTkEntry(form, placeholder_text="Descrição", height=38)
        self.entrada_desc.grid(row=0, column=0, sticky="ew", padx=(15, 8), pady=15)

        self.entrada_valor = ctk.CTkEntry(form, placeholder_text="Valor", height=38)
        self.entrada_valor.grid(row=0, column=1, sticky="ew", padx=8, pady=15)
        self.entrada_valor.bind("<Return>", lambda e: self.adicionar_gasto())

        self.menu_categoria = ctk.CTkOptionMenu(form, values=CATEGORIAS, height=38)
        self.menu_categoria.grid(row=0, column=2, sticky="ew", padx=8, pady=15)

        ctk.CTkButton(form, text="Adicionar", width=110, height=38, command=self.adicionar_gasto).grid(
            row=0, column=3, padx=(8, 15), pady=15
        )

        self.lista_gastos = ctk.CTkScrollableFrame(p, corner_radius=12, fg_color="#2b2d2d")
        self.lista_gastos.grid(row=2, column=0, sticky="nsew")
        self.lista_gastos.grid_columnconfigure(0, weight=1)

    def adicionar_gasto(self):
        descricao = self.entrada_desc.get().strip()
        if not descricao:
            messagebox.showerror("Campo vazio", "Escreva uma descrição para o gasto.")
            return
        try:
            valor = para_float(self.entrada_valor.get())
            if valor <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Valor inválido", "Digite um valor maior que zero. Ex.: 49,90")
            return

        self.dados["gastos"].append(
            {"descricao": descricao, "valor": valor, "categoria": self.menu_categoria.get()}
        )
        self.salvar_dados()
        self.entrada_desc.delete(0, "end")
        self.entrada_valor.delete(0, "end")
        self.atualizar()

    def remover_gasto(self, indice):
        del self.dados["gastos"][indice]
        self.salvar_dados()
        self.atualizar()

    def desenhar_lista(self):
        for widget in self.lista_gastos.winfo_children():
            widget.destroy()

        if not self.dados["gastos"]:
            ctk.CTkLabel(self.lista_gastos, text="Nenhum gasto cadastrado ainda.", text_color="gray").grid(
                row=0, column=0, pady=30
            )
            return

        for i, gasto in enumerate(self.dados["gastos"]):
            linha = ctk.CTkFrame(self.lista_gastos, fg_color="#353838", corner_radius=8)
            linha.grid(row=i, column=0, sticky="ew", pady=4, padx=4)
            linha.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(linha, text=gasto["descricao"], font=("Arial", 14), anchor="w").grid(
                row=0, column=0, sticky="w", padx=15, pady=(8, 0)
            )
            ctk.CTkLabel(linha, text=gasto["categoria"], font=("Arial", 11), text_color="gray", anchor="w").grid(
                row=1, column=0, sticky="w", padx=15, pady=(0, 8)
            )
            ctk.CTkLabel(linha, text=moeda(gasto["valor"]), font=("Arial Black", 14)).grid(
                row=0, column=1, rowspan=2, padx=15
            )
            ctk.CTkButton(
                linha, text="✕", width=32, height=32,
                fg_color=COR_NEGATIVO, hover_color="#c0443d",
                command=lambda idx=i: self.remover_gasto(idx),
            ).grid(row=0, column=2, rowspan=2, padx=(0, 12))

    # ---------- página: Gráfico ----------

    def criar_pagina_grafico(self):
        p = self.nova_pagina("Gráfico")
        p.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(p, text="Gastos por categoria", font=("Arial Black", 26)).grid(
            row=0, column=0, sticky="w", pady=(0, 20)
        )
        self.area_grafico = ctk.CTkFrame(p, corner_radius=12, fg_color="#2b2d2d")
        self.area_grafico.grid(row=1, column=0, sticky="nsew")
        self.area_grafico.grid_columnconfigure(1, weight=1)

    def desenhar_grafico(self):
        for widget in self.area_grafico.winfo_children():
            widget.destroy()

        total = self.total_gastos()
        if total == 0:
            ctk.CTkLabel(self.area_grafico, text="Adicione gastos para ver o gráfico.", text_color="gray").grid(
                row=0, column=0, padx=30, pady=40
            )
            return

        por_categoria = {}
        for g in self.dados["gastos"]:
            por_categoria[g["categoria"]] = por_categoria.get(g["categoria"], 0) + g["valor"]

        ordenado = sorted(por_categoria.items(), key=lambda x: x[1], reverse=True)
        for i, (categoria, valor) in enumerate(ordenado):
            proporcao = valor / total
            ctk.CTkLabel(self.area_grafico, text=categoria, font=("Arial", 14), width=110, anchor="w").grid(
                row=i, column=0, padx=(20, 10), pady=12
            )
            barra = ctk.CTkProgressBar(self.area_grafico, height=18)
            barra.set(proporcao)
            barra.grid(row=i, column=1, sticky="ew", pady=12)
            ctk.CTkLabel(
                self.area_grafico,
                text=f"{moeda(valor)}  ({proporcao * 100:.0f}%)",
                font=("Arial", 13), width=170, anchor="e",
            ).grid(row=i, column=2, padx=(10, 20))

    # ---------- atualização geral ----------

    def atualizar(self):
        salario = self.dados["salario"]
        gastos = self.total_gastos()
        saldo = salario - gastos

        self.card_salario.configure(text=moeda(salario))
        self.card_gastos.configure(text=moeda(gastos))
        self.card_saldo.configure(
            text=moeda(saldo), text_color=COR_POSITIVO if saldo >= 0 else COR_NEGATIVO
        )
        self.desenhar_lista()
        self.desenhar_grafico()


if __name__ == "__main__":
    app = App()
    app.mainloop()