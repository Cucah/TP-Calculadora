import customtkinter as ctk
import tkinter as tk
import os
import json
import math
from datetime import date
from tkinter import messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_DADOS = os.path.join(BASE_DIR, "dados.json")
ICONES = [
    os.path.join(BASE_DIR, "assets", "icon.ico"),
    os.path.join(BASE_DIR, "..", "assets", "icon.ico"),
]

# ---------- paleta: carvão + ouro (tema Tio Patinhas) ----------
BG = "#0f1115"
SIDEBAR = "#14171c"
CARD = "#1a1e25"
CARD2 = "#232831"
BORDA = "#2c323d"
TEXTO = "#e8eaee"
MUDO = "#8b93a1"
OURO = "#F2B84B"
OURO_HOVER = "#d9a13a"
VERDE = "#3DD6A0"
VERMELHO = "#EF6B63"
AMARELO = "#F2B84B"

CATEGORIAS = ["Moradia", "Alimentação", "Transporte", "Lazer", "Saúde", "Educação", "Outros"]

COR_CATEGORIA = {
    "Moradia": "#5B8DEF",
    "Alimentação": "#F2B84B",
    "Transporte": "#3DD6A0",
    "Lazer": "#C084FC",
    "Saúde": "#EF6B63",
    "Educação": "#38BDF8",
    "Outros": "#94A3B8",
}

# Limites recomendados (% do salário) por categoria — baseado na regra 50/30/20 adaptada
LIMITES = {
    "Moradia": 0.30,
    "Alimentação": 0.20,
    "Transporte": 0.15,
    "Lazer": 0.10,
    "Saúde": 0.10,
    "Educação": 0.10,
    "Outros": 0.05,
}

DICAS = {
    "Moradia": [
        "Renegocie o aluguel ou o financiamento; muitas vezes dá para conseguir desconto ou reduzir juros.",
        "Revise contas fixas (luz, água, internet, condomínio) e troque planos caros por opções mais baratas.",
        "Se possível, divida a moradia ou considere um imóvel mais próximo do trabalho para economizar também no transporte.",
    ],
    "Alimentação": [
        "Planeje o cardápio da semana e faça a lista de compras antes de ir ao mercado.",
        "Cozinhe em casa e leve marmita: pedir delivery com frequência pesa muito no orçamento.",
        "Compre alimentos da estação, em feiras e atacarejos, e evite ir ao mercado com fome.",
    ],
    "Transporte": [
        "Compare o custo de app, transporte público e carro próprio; às vezes o bilhete único compensa mais.",
        "Se usa carro, faça a manutenção em dia e use o app de combustível para achar o posto mais barato.",
        "Agrupe compromissos e use carona ou bicicleta em trajetos curtos.",
    ],
    "Lazer": [
        "Defina um teto mensal de lazer e use dinheiro reservado só para isso.",
        "Troque saídas caras por programas gratuitos: parques, eventos culturais e encontros em casa.",
        "Revise assinaturas de streaming e cancele as que você quase não usa.",
    ],
    "Saúde": [
        "Use a rede pública para consultas e exames de rotina, quando possível.",
        "Compre genéricos e compare preços de farmácia; muitos têm desconto com cadastro.",
        "Investir em prevenção (sono, alimentação, exercício) costuma sair mais barato que tratar depois.",
    ],
    "Educação": [
        "Procure cursos gratuitos ou com bolsa (Coursera, edX, Fundação Bradesco, universidades públicas).",
        "Compre livros usados, use bibliotecas e divida materiais com colegas.",
        "Negocie a mensalidade: muitas instituições dão desconto por pagamento antecipado.",
    ],
    "Outros": [
        "Registre esses gastos com mais detalhe; categorias 'Outros' muito altas escondem desperdícios.",
        "Antes de comprar por impulso, espere 48 horas: se ainda fizer sentido, compre.",
        "Evite taxas bancárias desnecessárias e juros de cartão e cheque especial.",
    ],
}


# ---------- funções auxiliares ----------

def moeda(valor):
    """1500.5 -> 'R$ 1.500,50'"""
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def moeda_curta(valor):
    """1500 -> 'R$ 1.500' (para eixos de gráfico)"""
    return "R$ " + f"{valor:,.0f}".replace(",", ".")


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

        self.title("Tio Patinhas · Controle Financeiro")
        self.geometry("1150x720")
        self.minsize(980, 640)
        self.configure(fg_color=BG)

        # CTk redefine o ícone após abrir a janela, então aplicamos com atraso
        self.after(250, self.aplicar_icone)

        self.dados = self.carregar_dados()
        self.tipo_grafico = "Pizza"

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.paginas = {}
        self.botoes_menu = {}

        self.criar_sidebar()

        self.conteudo = ctk.CTkFrame(self, fg_color="transparent")
        self.conteudo.grid(row=0, column=1, sticky="nsew", padx=30, pady=26)
        self.conteudo.grid_columnconfigure(0, weight=1)
        self.conteudo.grid_rowconfigure(0, weight=1)

        self.criar_pagina_inicio()
        self.criar_pagina_gastos()
        self.criar_pagina_grafico()
        self.criar_pagina_dicas()

        self.mostrar("Início")
        self.atualizar()

    def aplicar_icone(self):
        for caminho in ICONES:
            if os.path.exists(caminho):
                try:
                    self.iconbitmap(caminho)
                    return
                except Exception as e:
                    print("Erro ícone:", e)

    # ---------- dados ----------

    def carregar_dados(self):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                dados = json.load(f)
                dados.setdefault("salario", 0.0)
                dados.setdefault("gastos", [])
                return dados
        except (FileNotFoundError, json.JSONDecodeError):
            return {"salario": 0.0, "gastos": []}

    def salvar_dados(self):
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(self.dados, f, ensure_ascii=False, indent=2)

    def total_gastos(self):
        return sum(g["valor"] for g in self.dados["gastos"])

    def gastos_por_categoria(self):
        por_categoria = {}
        for g in self.dados["gastos"]:
            por_categoria[g["categoria"]] = por_categoria.get(g["categoria"], 0) + g["valor"]
        return sorted(por_categoria.items(), key=lambda x: x[1], reverse=True)

    # ---------- layout base ----------

    def criar_sidebar(self):
        barra = ctk.CTkFrame(self, width=210, corner_radius=0, fg_color=SIDEBAR)
        barra.grid(row=0, column=0, sticky="nsw")
        barra.grid_propagate(False)
        barra.grid_columnconfigure(0, weight=1)
        barra.grid_rowconfigure(10, weight=1)

        marca = ctk.CTkFrame(barra, fg_color="transparent")
        marca.grid(row=0, column=0, sticky="ew", padx=18, pady=(28, 4))
        moeda_logo = ctk.CTkLabel(
            marca, text="$", width=38, height=38, corner_radius=19,
            fg_color=OURO, text_color="#1a1405", font=("Arial Black", 20),
        )
        moeda_logo.pack(side="left")
        textos = ctk.CTkFrame(marca, fg_color="transparent")
        textos.pack(side="left", padx=10)
        ctk.CTkLabel(textos, text="Tio Patinhas", font=("Arial Black", 15), text_color=TEXTO).pack(anchor="w")
        ctk.CTkLabel(textos, text="Controle financeiro", font=("Arial", 11), text_color=MUDO).pack(anchor="w")

        ctk.CTkFrame(barra, height=1, fg_color=BORDA).grid(
            row=1, column=0, sticky="ew", padx=18, pady=(22, 18)
        )

        itens = [("Início", "▣  Início"), ("Gastos", "≡  Gastos"), ("Gráfico", "◔  Gráficos"), ("Dicas", "✦  Dicas")]
        for i, (nome, rotulo) in enumerate(itens):
            botao = ctk.CTkButton(
                barra,
                text=rotulo,
                anchor="w",
                height=42,
                corner_radius=10,
                font=("Arial", 14, "bold"),
                fg_color="transparent",
                text_color=MUDO,
                hover_color=CARD2,
                command=lambda n=nome: self.mostrar(n),
            )
            botao.grid(row=2 + i, column=0, sticky="ew", padx=14, pady=3)
            self.botoes_menu[nome] = botao

        ctk.CTkLabel(barra, text="v0.04 private", font=("Arial", 11), text_color=MUDO).grid(
            row=11, column=0, padx=20, pady=18, sticky="sw"
        )

    def nova_pagina(self, nome):
        pagina = ctk.CTkFrame(self.conteudo, fg_color="transparent")
        pagina.grid(row=0, column=0, sticky="nsew")
        self.paginas[nome] = pagina
        return pagina

    def mostrar(self, nome):
        self.paginas[nome].tkraise()
        for n, botao in self.botoes_menu.items():
            ativo = n == nome
            botao.configure(
                fg_color=CARD2 if ativo else "transparent",
                text_color=OURO if ativo else MUDO,
            )
        if nome == "Gráfico":
            self.after(50, self.desenhar_grafico)

    def cabecalho(self, pagina, titulo, subtitulo, colunas=1):
        topo = ctk.CTkFrame(pagina, fg_color="transparent")
        topo.grid(row=0, column=0, columnspan=colunas, sticky="ew", pady=(0, 20))
        topo.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(topo, text=titulo, font=("Arial Black", 28), text_color=TEXTO).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(topo, text=subtitulo, font=("Arial", 13), text_color=MUDO).grid(row=1, column=0, sticky="w")
        return topo

    def criar_card(self, pai, titulo, coluna, cor_destaque):
        card = ctk.CTkFrame(pai, corner_radius=14, fg_color=CARD, border_width=1, border_color=BORDA)
        card.grid(row=1, column=coluna, sticky="ew", padx=6)
        ctk.CTkFrame(card, height=4, corner_radius=2, fg_color=cor_destaque).pack(fill="x", padx=18, pady=(14, 0))
        ctk.CTkLabel(card, text=titulo, font=("Arial", 13), text_color=MUDO).pack(anchor="w", padx=18, pady=(12, 0))
        valor = ctk.CTkLabel(card, text="R$ 0,00", font=("Arial Black", 23), text_color=TEXTO)
        valor.pack(anchor="w", padx=18, pady=(2, 16))
        return valor

    # ---------- página: Início ----------

    def criar_pagina_inicio(self):
        p = self.nova_pagina("Início")
        for c in range(3):
            p.grid_columnconfigure(c, weight=1)

        self.cabecalho(p, "Visão geral", "Como está o seu dinheiro neste mês", colunas=3)

        self.card_salario = self.criar_card(p, "Salário", 0, OURO)
        self.card_gastos = self.criar_card(p, "Total de gastos", 1, VERMELHO)
        self.card_saldo = self.criar_card(p, "Saldo restante", 2, VERDE)

        # barra de comprometimento do salário
        prog = ctk.CTkFrame(p, corner_radius=14, fg_color=CARD, border_width=1, border_color=BORDA)
        prog.grid(row=2, column=0, columnspan=3, sticky="ew", padx=6, pady=(18, 0))
        prog.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(prog, text="Salário comprometido", font=("Arial Black", 14), text_color=TEXTO).grid(
            row=0, column=0, sticky="w", padx=20, pady=(16, 0)
        )
        self.lbl_percentual = ctk.CTkLabel(prog, text="0%", font=("Arial Black", 14), text_color=MUDO)
        self.lbl_percentual.grid(row=0, column=1, sticky="e", padx=20, pady=(16, 0))
        self.barra_salario = ctk.CTkProgressBar(prog, height=14, progress_color=VERDE, fg_color=CARD2)
        self.barra_salario.set(0)
        self.barra_salario.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(10, 18))

        # definir salário
        caixa = ctk.CTkFrame(p, corner_radius=14, fg_color=CARD, border_width=1, border_color=BORDA)
        caixa.grid(row=3, column=0, columnspan=3, sticky="ew", padx=6, pady=(18, 0))
        caixa.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(caixa, text="Definir salário", font=("Arial Black", 14), text_color=TEXTO).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(16, 6)
        )
        self.entrada_salario = ctk.CTkEntry(
            caixa, placeholder_text="Ex.: 3500,00", height=40,
            fg_color=CARD2, border_color=BORDA, corner_radius=10,
        )
        self.entrada_salario.grid(row=1, column=0, sticky="ew", padx=(20, 10), pady=(0, 18))
        self.entrada_salario.bind("<Return>", lambda e: self.salvar_salario())

        ctk.CTkButton(
            caixa, text="Salvar", width=120, height=40, corner_radius=10,
            fg_color=OURO, hover_color=OURO_HOVER, text_color="#1a1405",
            font=("Arial", 13, "bold"), command=self.salvar_salario,
        ).grid(row=1, column=1, padx=(0, 20), pady=(0, 18))

        # dica rápida
        self.caixa_dica = ctk.CTkFrame(p, corner_radius=14, fg_color=CARD, border_width=1, border_color=BORDA)
        self.caixa_dica.grid(row=4, column=0, columnspan=3, sticky="ew", padx=6, pady=(18, 0))
        self.caixa_dica.grid_columnconfigure(1, weight=1)
        self.faixa_dica = ctk.CTkFrame(self.caixa_dica, width=6, corner_radius=3, fg_color=OURO)
        self.faixa_dica.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(14, 0), pady=14)
        self.titulo_dica = ctk.CTkLabel(
            self.caixa_dica, text="", font=("Arial Black", 14), text_color=TEXTO, anchor="w"
        )
        self.titulo_dica.grid(row=0, column=1, sticky="w", padx=16, pady=(14, 0))
        self.texto_dica = ctk.CTkLabel(
            self.caixa_dica, text="", font=("Arial", 13), text_color=MUDO,
            anchor="w", justify="left", wraplength=700,
        )
        self.texto_dica.grid(row=1, column=1, sticky="w", padx=16, pady=(2, 14))
        self.caixa_dica.bind("<Configure>", lambda e: self.texto_dica.configure(wraplength=max(e.width - 70, 200)))

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

        self.cabecalho(p, "Gastos", "Registre e acompanhe cada despesa")

        form = ctk.CTkFrame(p, corner_radius=14, fg_color=CARD, border_width=1, border_color=BORDA)
        form.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        form.grid_columnconfigure(0, weight=3)
        form.grid_columnconfigure(1, weight=1)
        form.grid_columnconfigure(2, weight=1)

        estilo = dict(height=40, fg_color=CARD2, border_color=BORDA, corner_radius=10)

        self.entrada_desc = ctk.CTkEntry(form, placeholder_text="Descrição", **estilo)
        self.entrada_desc.grid(row=0, column=0, sticky="ew", padx=(16, 8), pady=16)

        self.entrada_valor = ctk.CTkEntry(form, placeholder_text="Valor", **estilo)
        self.entrada_valor.grid(row=0, column=1, sticky="ew", padx=8, pady=16)
        self.entrada_valor.bind("<Return>", lambda e: self.adicionar_gasto())

        self.menu_categoria = ctk.CTkOptionMenu(
            form, values=CATEGORIAS, height=40, corner_radius=10,
            fg_color=CARD2, button_color=BORDA, button_hover_color=MUDO,
        )
        self.menu_categoria.grid(row=0, column=2, sticky="ew", padx=8, pady=16)

        ctk.CTkButton(
            form, text="+  Adicionar", width=130, height=40, corner_radius=10,
            fg_color=OURO, hover_color=OURO_HOVER, text_color="#1a1405",
            font=("Arial", 13, "bold"), command=self.adicionar_gasto,
        ).grid(row=0, column=3, padx=(8, 16), pady=16)

        self.lista_gastos = ctk.CTkScrollableFrame(
            p, corner_radius=14, fg_color=CARD, border_width=1, border_color=BORDA
        )
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

        self.dados["gastos"].append({
            "descricao": descricao,
            "valor": valor,
            "categoria": self.menu_categoria.get(),
            "data": date.today().strftime("%d/%m/%Y"),
        })
        self.salvar_dados()
        self.entrada_desc.delete(0, "end")
        self.entrada_valor.delete(0, "end")
        self.atualizar()

    def remover_gasto(self, indice):
        gasto = self.dados["gastos"][indice]
        if not messagebox.askyesno("Remover gasto", f"Remover \"{gasto['descricao']}\"?"):
            return
        del self.dados["gastos"][indice]
        self.salvar_dados()
        self.atualizar()

    def desenhar_lista(self):
        for widget in self.lista_gastos.winfo_children():
            widget.destroy()

        if not self.dados["gastos"]:
            ctk.CTkLabel(
                self.lista_gastos,
                text="Nenhum gasto ainda.\nPreencha os campos acima e clique em Adicionar.",
                text_color=MUDO, font=("Arial", 13), justify="center",
            ).grid(row=0, column=0, pady=50)
            return

        # mostra do mais recente para o mais antigo, mantendo o índice real para remoção
        for pos, i in enumerate(reversed(range(len(self.dados["gastos"])))):
            gasto = self.dados["gastos"][i]
            cor = COR_CATEGORIA.get(gasto["categoria"], MUDO)

            linha = ctk.CTkFrame(self.lista_gastos, fg_color=CARD2, corner_radius=10)
            linha.grid(row=pos, column=0, sticky="ew", pady=4, padx=4)
            linha.grid_columnconfigure(1, weight=1)

            ctk.CTkFrame(linha, width=5, corner_radius=3, fg_color=cor).grid(
                row=0, column=0, rowspan=2, sticky="ns", padx=(10, 0), pady=10
            )
            ctk.CTkLabel(linha, text=gasto["descricao"], font=("Arial", 14, "bold"), text_color=TEXTO, anchor="w").grid(
                row=0, column=1, sticky="w", padx=14, pady=(10, 0)
            )
            subtitulo = gasto["categoria"]
            if gasto.get("data"):
                subtitulo += f"  ·  {gasto['data']}"
            ctk.CTkLabel(linha, text=subtitulo, font=("Arial", 11), text_color=MUDO, anchor="w").grid(
                row=1, column=1, sticky="w", padx=14, pady=(0, 10)
            )
            ctk.CTkLabel(linha, text=moeda(gasto["valor"]), font=("Arial Black", 14), text_color=TEXTO).grid(
                row=0, column=2, rowspan=2, padx=14
            )
            ctk.CTkButton(
                linha, text="✕", width=32, height=32, corner_radius=8,
                fg_color="transparent", text_color=MUDO,
                hover_color=VERMELHO,
                command=lambda idx=i: self.remover_gasto(idx),
            ).grid(row=0, column=3, rowspan=2, padx=(0, 12))

    # ---------- página: Gráficos ----------

    def criar_pagina_grafico(self):
        p = self.nova_pagina("Gráfico")
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(1, weight=1)

        topo = self.cabecalho(p, "Gráficos", "Veja para onde seu dinheiro está indo")
        self.seletor_grafico = ctk.CTkSegmentedButton(
            topo,
            values=["Pizza", "Torres", "Linhas"],
            command=self.trocar_grafico,
            height=36,
            font=("Arial", 13, "bold"),
            fg_color=CARD2,
            selected_color=OURO,
            selected_hover_color=OURO_HOVER,
            unselected_color=CARD2,
            unselected_hover_color=BORDA,
            text_color="#e8eaee",
        )
        self.seletor_grafico.set("Pizza")
        self.seletor_grafico.grid(row=0, column=1, rowspan=2, sticky="e")

        moldura = ctk.CTkFrame(p, corner_radius=14, fg_color=CARD, border_width=1, border_color=BORDA)
        moldura.grid(row=1, column=0, sticky="nsew")
        moldura.grid_columnconfigure(0, weight=1)
        moldura.grid_rowconfigure(1, weight=1)

        self.titulo_grafico = ctk.CTkLabel(moldura, text="", font=("Arial Black", 16), text_color=TEXTO)
        self.titulo_grafico.grid(row=0, column=0, sticky="w", padx=22, pady=(18, 0))

        self.canvas = tk.Canvas(moldura, bg=CARD, highlightthickness=0, bd=0)
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.canvas.bind("<Configure>", lambda e: self.desenhar_grafico())

    def trocar_grafico(self, tipo):
        self.tipo_grafico = tipo
        self.desenhar_grafico()

    def desenhar_grafico(self):
        c = self.canvas
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 80 or h < 80:
            return

        titulos = {
            "Pizza": "Distribuição dos gastos por categoria",
            "Torres": "Valor gasto em cada categoria",
            "Linhas": "Evolução dos gastos acumulados",
        }
        self.titulo_grafico.configure(text=titulos[self.tipo_grafico])

        total = self.total_gastos()
        if total == 0:
            c.create_text(
                w / 2, h / 2, text="Adicione gastos para ver o gráfico.",
                fill=MUDO, font=("Arial", 13),
            )
            return

        dados = self.gastos_por_categoria()
        if self.tipo_grafico == "Pizza":
            self.grafico_pizza(c, w, h, dados, total)
        elif self.tipo_grafico == "Torres":
            self.grafico_torres(c, w, h, dados)
        else:
            self.grafico_linhas(c, w, h)

    def grafico_pizza(self, c, w, h, dados, total):
        largura_legenda = 290
        area_w = max(w - largura_legenda, 200)
        cx, cy = area_w / 2, h / 2
        r = max(min(area_w / 2, h / 2) - 24, 40)
        caixa = (cx - r, cy - r, cx + r, cy + r)

        inicio = 90
        for categoria, valor in dados:
            cor = COR_CATEGORIA.get(categoria, MUDO)
            extensao = -360 * valor / total
            if len(dados) == 1:
                c.create_oval(*caixa, fill=cor, outline=CARD, width=3)
            else:
                c.create_arc(*caixa, start=inicio, extent=extensao, fill=cor, outline=CARD, width=3, style="pieslice")
            inicio += extensao

        # centro vazado (donut) com o total
        furo = r * 0.58
        c.create_oval(cx - furo, cy - furo, cx + furo, cy + furo, fill=CARD, outline=CARD)
        c.create_text(cx, cy - 12, text="Total", fill=MUDO, font=("Arial", 12))
        c.create_text(cx, cy + 12, text=moeda(total), fill=TEXTO, font=("Arial Black", 15))

        # legenda
        x0 = area_w + 20
        altura_item = 38
        y = cy - (len(dados) * altura_item) / 2
        for categoria, valor in dados:
            cor = COR_CATEGORIA.get(categoria, MUDO)
            c.create_rectangle(x0, y + 6, x0 + 14, y + 20, fill=cor, outline=cor)
            c.create_text(x0 + 24, y + 4, text=categoria, fill=TEXTO, font=("Arial", 12, "bold"), anchor="nw")
            c.create_text(
                x0 + 24, y + 22, text=f"{moeda(valor)}  ·  {valor / total * 100:.0f}%",
                fill=MUDO, font=("Arial", 11), anchor="nw",
            )
            y += altura_item

    def eixo_y(self, c, w, h, maximo, esq, dir_, topo, base):
        """Desenha linhas de grade e rótulos do eixo Y."""
        passos = 4
        for k in range(passos + 1):
            valor = maximo * k / passos
            y = base - (base - topo) * k / passos
            c.create_line(esq, y, w - dir_, y, fill=BORDA, dash=(2, 4))
            c.create_text(esq - 10, y, text=moeda_curta(valor), fill=MUDO, font=("Arial", 10), anchor="e")

    def grafico_torres(self, c, w, h, dados):
        esq, dir_, topo, base = 90, 30, 30, h - 60
        if base - topo < 60 or w - esq - dir_ < 100:
            return
        maximo = max(v for _, v in dados) * 1.15
        self.eixo_y(c, w, h, maximo, esq, dir_, topo, base)

        n = len(dados)
        espaco = (w - esq - dir_) / n
        largura = min(espaco * 0.55, 90)
        for i, (categoria, valor) in enumerate(dados):
            cor = COR_CATEGORIA.get(categoria, MUDO)
            cx = esq + espaco * i + espaco / 2
            y = base - (base - topo) * valor / maximo
            c.create_rectangle(cx - largura / 2, y, cx + largura / 2, base, fill=cor, outline=cor)
            c.create_text(cx, y - 10, text=moeda(valor), fill=TEXTO, font=("Arial", 11, "bold"))
            c.create_text(cx, base + 18, text=categoria, fill=MUDO, font=("Arial", 11))
        c.create_line(esq, base, w - dir_, base, fill=MUDO)

    def grafico_linhas(self, c, w, h):
        esq, dir_, topo, base = 90, 40, 30, h - 60
        if base - topo < 60 or w - esq - dir_ < 100:
            return

        gastos = self.dados["gastos"]
        acumulado, soma = [], 0
        for g in gastos:
            soma += g["valor"]
            acumulado.append(soma)

        salario = self.dados["salario"]
        maximo = max(acumulado[-1], salario if salario > 0 else 0) * 1.15
        self.eixo_y(c, w, h, maximo, esq, dir_, topo, base)

        n = len(acumulado)
        largura = w - esq - dir_

        def pos_x(i):
            return esq + largura / 2 if n == 1 else esq + 20 + (largura - 40) * i / (n - 1)

        def pos_y(v):
            return base - (base - topo) * v / maximo

        # linha do salário
        if salario > 0:
            ys = pos_y(salario)
            c.create_line(esq, ys, w - dir_, ys, fill=OURO, dash=(6, 4), width=2)
            c.create_text(w - dir_, ys - 10, text=f"Salário {moeda_curta(salario)}", fill=OURO, font=("Arial", 10, "bold"), anchor="e")

        pontos = [(pos_x(i), pos_y(v)) for i, v in enumerate(acumulado)]

        if n > 1:
            area = [(pontos[0][0], base)] + pontos + [(pontos[-1][0], base)]
            c.create_polygon([coord for p in area for coord in p], fill=VERMELHO, stipple="gray12", outline="")
            c.create_line([coord for p in pontos for coord in p], fill=VERMELHO, width=3, smooth=False)

        passo = max(1, math.ceil(n / 8))
        for i, (x, y) in enumerate(pontos):
            c.create_oval(x - 5, y - 5, x + 5, y + 5, fill=VERMELHO, outline=CARD, width=2)
            if i % passo == 0 or i == n - 1:
                rotulo = gastos[i].get("data", "")[:5] or f"#{i + 1}"
                c.create_text(x, base + 18, text=rotulo, fill=MUDO, font=("Arial", 10))
        c.create_text(
            pontos[-1][0], pontos[-1][1] - 14, text=moeda(acumulado[-1]),
            fill=TEXTO, font=("Arial", 11, "bold"),
        )
        c.create_line(esq, base, w - dir_, base, fill=MUDO)

    # ---------- página: Dicas ----------

    def criar_pagina_dicas(self):
        p = self.nova_pagina("Dicas")
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(1, weight=1)

        self.cabecalho(p, "Dicas de economia", "Sugestões baseadas nos seus gastos em relação ao salário")

        self.lista_dicas = ctk.CTkScrollableFrame(p, corner_radius=14, fg_color="transparent")
        self.lista_dicas.grid(row=1, column=0, sticky="nsew")
        self.lista_dicas.grid_columnconfigure(0, weight=1)

    def gerar_dicas(self):
        """Retorna lista de (nivel, titulo, texto, extras) — nivel: alerta | atencao | ok | info"""
        salario = self.dados["salario"]
        total = self.total_gastos()
        resultado = []

        if not self.dados["gastos"] and salario <= 0:
            return [("info", "Comece por aqui",
                     "Defina seu salário na tela Início e cadastre seus gastos. Assim eu consigo analisar seu orçamento e sugerir onde economizar.", [])]
        if salario <= 0:
            return [("info", "Defina seu salário",
                     "Para saber se algum gasto está exagerado, preciso do seu salário. Cadastre-o na tela Início.", [])]
        if not self.dados["gastos"]:
            return [("info", "Nenhum gasto cadastrado",
                     "Cadastre seus gastos na tela Gastos para receber dicas personalizadas.", [])]

        if total > salario:
            resultado.append((
                "alerta", "Você gastou mais do que ganha",
                f"Seus gastos ({moeda(total)}) superam o salário ({moeda(salario)}) em {moeda(total - salario)}. "
                "Priorize cortar despesas não essenciais e evite usar crédito para cobrir o rombo.",
                [],
            ))

        # categorias acima do limite recomendado
        excessos = []
        for categoria, valor in self.gastos_por_categoria():
            limite = LIMITES.get(categoria, 0.10)
            pct = valor / salario
            if pct > limite:
                excessos.append((valor - limite * salario, categoria, valor, pct, limite))
        excessos.sort(reverse=True)

        for excesso, categoria, valor, pct, limite in excessos:
            nivel = "alerta" if pct > limite * 1.5 else "atencao"
            resultado.append((
                nivel,
                f"{categoria} está acima do ideal",
                f"Você gastou {moeda(valor)} ({pct * 100:.0f}% do salário). O recomendado é até {limite * 100:.0f}% "
                f"({moeda(limite * salario)}). Dá para reduzir cerca de {moeda(excesso)}.",
                DICAS.get(categoria, [])[:3],
            ))

        # reserva / poupança
        saldo = salario - total
        if total <= salario and saldo / salario < 0.20:
            resultado.append((
                "atencao", "Sua reserva está baixa",
                f"Sobram {moeda(saldo)} ({saldo / salario * 100:.0f}% do salário). Tente guardar pelo menos 20% "
                f"({moeda(salario * 0.2)}) todo mês, de preferência assim que receber.",
                ["Programe uma transferência automática para a poupança ou um investimento logo após o pagamento."],
            ))

        if not resultado:
            resultado.append((
                "ok", "Parabéns, seu orçamento está saudável",
                f"Nenhuma categoria passou do limite recomendado e você ainda guarda {moeda(saldo)} "
                f"({saldo / salario * 100:.0f}% do salário). Considere investir esse valor para fazê-lo render.",
                [],
            ))
        return resultado

    def desenhar_dicas(self):
        for widget in self.lista_dicas.winfo_children():
            widget.destroy()

        cores = {"alerta": VERMELHO, "atencao": AMARELO, "ok": VERDE, "info": "#5B8DEF"}
        rotulos = {"alerta": "Atenção máxima", "atencao": "Vale revisar", "ok": "Tudo certo", "info": "Informação"}

        for i, (nivel, titulo, texto, extras) in enumerate(self.gerar_dicas()):
            cor = cores[nivel]
            card = ctk.CTkFrame(self.lista_dicas, corner_radius=14, fg_color=CARD, border_width=1, border_color=BORDA)
            card.grid(row=i, column=0, sticky="ew", pady=7, padx=2)
            card.grid_columnconfigure(1, weight=1)

            ctk.CTkFrame(card, width=6, corner_radius=3, fg_color=cor).grid(
                row=0, column=0, rowspan=3, sticky="ns", padx=(14, 0), pady=14
            )
            ctk.CTkLabel(card, text=titulo, font=("Arial Black", 16), text_color=TEXTO, anchor="w").grid(
                row=0, column=1, sticky="w", padx=16, pady=(14, 0)
            )
            ctk.CTkLabel(
                card, text=rotulos[nivel], font=("Arial", 11, "bold"), text_color=cor,
            ).grid(row=0, column=2, padx=18, pady=(14, 0), sticky="e")

            corpo = ctk.CTkLabel(
                card, text=texto, font=("Arial", 13), text_color=MUDO,
                anchor="w", justify="left", wraplength=700,
            )
            corpo.grid(row=1, column=1, columnspan=2, sticky="w", padx=16, pady=(4, 6 if extras else 14))

            if extras:
                bloco = ctk.CTkFrame(card, fg_color=CARD2, corner_radius=10)
                bloco.grid(row=2, column=1, columnspan=2, sticky="ew", padx=16, pady=(4, 16))
                for dica in extras:
                    ctk.CTkLabel(
                        bloco, text=f"•  {dica}", font=("Arial", 12), text_color=TEXTO,
                        anchor="w", justify="left", wraplength=680,
                    ).pack(anchor="w", padx=14, pady=5)

            card.bind("<Configure>", lambda e, lb=corpo: lb.configure(wraplength=max(e.width - 90, 200)))

    # ---------- atualização geral ----------

    def atualizar(self):
        salario = self.dados["salario"]
        gastos = self.total_gastos()
        saldo = salario - gastos

        self.card_salario.configure(text=moeda(salario))
        self.card_gastos.configure(text=moeda(gastos))
        self.card_saldo.configure(text=moeda(saldo), text_color=VERDE if saldo >= 0 else VERMELHO)

        # barra de comprometimento
        if salario > 0:
            uso = gastos / salario
            self.barra_salario.set(min(uso, 1))
            cor = VERDE if uso < 0.7 else (AMARELO if uso <= 1 else VERMELHO)
            self.barra_salario.configure(progress_color=cor)
            self.lbl_percentual.configure(text=f"{uso * 100:.0f}%", text_color=cor)
        else:
            self.barra_salario.set(0)
            self.lbl_percentual.configure(text="Defina seu salário", text_color=MUDO)

        # dica rápida na tela inicial (a mais importante)
        nivel, titulo, texto, _ = self.gerar_dicas()[0]
        cores = {"alerta": VERMELHO, "atencao": AMARELO, "ok": VERDE, "info": "#5B8DEF"}
        self.faixa_dica.configure(fg_color=cores[nivel])
        self.titulo_dica.configure(text=titulo)
        self.texto_dica.configure(text=texto)

        self.desenhar_lista()
        self.desenhar_grafico()
        self.desenhar_dicas()


if __name__ == "__main__":
    app = App()
    app.mainloop()
