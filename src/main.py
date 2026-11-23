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
TEXTO_OURO = "#1a1405"
VERDE = "#3DD6A0"
VERMELHO = "#EF6B63"
AMARELO = "#F2B84B"
AZUL = "#5B8DEF"

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

# Limites recomendados (% do salário) por categoria — regra 50/30/20 adaptada
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

DICAS_GERAIS = [
    "Pague-se primeiro: separe a parte da poupança assim que o salário cair, antes de gastar com qualquer outra coisa.",
    "Anote todo gasto, até os pequenos. Cafezinhos e assinaturas esquecidas somam bastante no fim do mês.",
    "Monte uma reserva de emergência equivalente a 3 a 6 meses do seu custo de vida.",
    "Evite parcelar o que não é essencial: parcelas pequenas viram um orçamento comprometido.",
    "Compare preços antes de comprar e espere 48 horas em compras por impulso.",
    "Revise suas assinaturas e planos fixos a cada trimestre; cancele o que não usa.",
    "Defina metas por categoria. Um limite claro ajuda a decidir na hora da compra.",
    "Tenha um dia fixo da semana para revisar seus gastos; leva menos de 10 minutos.",
    "Aumento de renda não precisa significar aumento de gastos: guarde pelo menos metade do que sobrar a mais.",
    "Pagar a fatura do cartão integralmente evita os juros mais altos do mercado.",
]

MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
         "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]


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


def mes_atual():
    return date.today().strftime("%Y-%m")


def mes_de(gasto):
    """Retorna 'AAAA-MM' a partir da data 'dd/mm/aaaa' do gasto."""
    try:
        _, mes, ano = gasto.get("data", "").split("/")
        return f"{int(ano):04d}-{int(mes):02d}"
    except ValueError:
        return mes_atual()


def nome_mes(m, curto=False):
    ano, mes = m.split("-")
    nome = MESES[int(mes) - 1]
    return f"{nome[:3]}/{ano[2:]}" if curto else f"{nome} de {ano}"


# ---------- conquistas ----------
# "ok": recebe o dicionário de estatísticas e diz se foi desbloqueada
# "prog": (atual, alvo, tipo) para mostrar a barra de progresso; tipo "n" = número, "$" = dinheiro

CONQUISTAS = [
    {"id": "primeiro_gasto", "icone": "🏁", "nome": "Primeiro passo",
     "desc": "Registre seu primeiro gasto.",
     "ok": lambda s: s["n_gastos"] >= 1},
    {"id": "salario", "icone": "💼", "nome": "Orçamento ativo",
     "desc": "Defina o seu salário.",
     "ok": lambda s: s["salario_definido"]},
    {"id": "dez_gastos", "icone": "📒", "nome": "Organizado",
     "desc": "Registre 10 gastos.",
     "ok": lambda s: s["n_gastos"] >= 10,
     "prog": lambda s: (s["n_gastos"], 10, "n")},
    {"id": "cinq_gastos", "icone": "📚", "nome": "Contador nato",
     "desc": "Registre 50 gastos.",
     "ok": lambda s: s["n_gastos"] >= 50,
     "prog": lambda s: (s["n_gastos"], 50, "n")},
    {"id": "primeira_meta", "icone": "🎯", "nome": "Mirando alto",
     "desc": "Defina sua primeira meta de gasto.",
     "ok": lambda s: s["n_metas"] >= 1},
    {"id": "todas_metas", "icone": "🧭", "nome": "Planejador",
     "desc": "Defina metas para todas as categorias.",
     "ok": lambda s: s["n_metas"] >= len(CATEGORIAS),
     "prog": lambda s: (s["n_metas"], len(CATEGORIAS), "n")},
    {"id": "categorias_5", "icone": "🌈", "nome": "Visão completa",
     "desc": "Registre gastos em 5 categorias diferentes.",
     "ok": lambda s: s["n_cats"] >= 5,
     "prog": lambda s: (s["n_cats"], 5, "n")},
    {"id": "dentro_metas", "icone": "🛡", "nome": "Disciplina de ferro",
     "desc": "Tenha 3 ou mais metas e nenhuma estourada no mês atual.",
     "ok": lambda s: s["dentro_metas"]},
    {"id": "fechou_azul", "icone": "📈", "nome": "Fechou no azul",
     "desc": "Termine um mês sem gastar mais do que ganhou.",
     "ok": lambda s: s["fechou_azul"]},
    {"id": "poupador20", "icone": "🐖", "nome": "Poupador nato",
     "desc": "Economize 20% ou mais do salário em um mês encerrado.",
     "ok": lambda s: s["poupador20"]},
    {"id": "meta_economia", "icone": "🏆", "nome": "Meta batida",
     "desc": "Alcance sua meta de economia em um mês encerrado.",
     "ok": lambda s: s["meta_eco_batida"]},
    {"id": "tres_meses", "icone": "🔥", "nome": "Em chamas",
     "desc": "Feche 3 meses seguidos no azul.",
     "ok": lambda s: s["streak"] >= 3,
     "prog": lambda s: (min(s["streak"], 3), 3, "n")},
    {"id": "cofrinho", "icone": "💎", "nome": "Cofrinho cheio",
     "desc": "Acumule R$ 1.000 de economia em meses encerrados.",
     "ok": lambda s: s["acumulado"] >= 1000,
     "prog": lambda s: (min(s["acumulado"], 1000), 1000, "$")},
    {"id": "tio_patinhas", "icone": "🦆", "nome": "Tio Patinhas",
     "desc": "Acumule R$ 5.000 de economia em meses encerrados.",
     "ok": lambda s: s["acumulado"] >= 5000,
     "prog": lambda s: (min(s["acumulado"], 5000), 5000, "$")},
]

NIVEIS = [(0, "Iniciante"), (3, "Aprendiz"), (6, "Poupador"), (9, "Estrategista"), (12, "Tio Patinhas")]


# ---------- aplicação ----------

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Tio Patinhas · Controle Financeiro")
        self.geometry("1200x780")
        self.minsize(1020, 700)
        self.configure(fg_color=BG)

        # CTk redefine o ícone após abrir a janela, então aplicamos com atraso
        self.after(250, self.aplicar_icone)

        self.dados = self.carregar_dados()
        self.tipo_grafico = "Pizza"
        self.filtro_dicas = "Todas"
        self.stats = {}
        self.fila_toast = []
        self.toast_ativo = False
        self.linhas_meta = {}
        self.dialogo_salario = None

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
        self.criar_pagina_metas()
        self.criar_pagina_grafico()
        self.criar_pagina_historico()
        self.criar_pagina_conquistas()
        self.criar_pagina_dicas()

        self.mostrar("Início")
        self.atualizar()

        if self.salario_atual() <= 0:
            self.after(700, self.abrir_dialogo_salario)

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
        except (FileNotFoundError, json.JSONDecodeError):
            dados = {}

        dados.setdefault("salario", 0.0)
        dados.setdefault("gastos", [])
        dados.setdefault("salarios", {})        # salário por mês: {"2026-11": 3500.0}
        dados.setdefault("metas", {})           # meta por categoria
        dados.setdefault("meta_economia", 0.0)  # quanto guardar por mês
        dados.setdefault("conquistas", {})      # {id: data de desbloqueio}

        # migração de arquivos antigos: gastos sem data e salário único
        hoje = date.today().strftime("%d/%m/%Y")
        for g in dados["gastos"]:
            if not g.get("data"):
                g["data"] = hoje
        if not dados["salarios"] and dados["salario"] > 0:
            meses = [mes_de(g) for g in dados["gastos"]] + [mes_atual()]
            dados["salarios"][min(meses)] = dados["salario"]
        return dados

    def salvar_dados(self):
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(self.dados, f, ensure_ascii=False, indent=2)

    def salario_do_mes(self, mes):
        """Salário vigente em um mês: o último definido até aquele mês."""
        anteriores = [m for m in self.dados["salarios"] if m <= mes]
        if not anteriores:
            return 0.0
        return self.dados["salarios"][max(anteriores)]

    def salario_atual(self):
        return self.salario_do_mes(mes_atual())

    def gastos_do_mes(self, mes=None):
        mes = mes or mes_atual()
        return [g for g in self.dados["gastos"] if mes_de(g) == mes]

    def total_gastos(self, mes=None):
        return sum(g["valor"] for g in self.gastos_do_mes(mes))

    def gastos_por_categoria(self, mes=None):
        por_categoria = {}
        for g in self.gastos_do_mes(mes):
            por_categoria[g["categoria"]] = por_categoria.get(g["categoria"], 0) + g["valor"]
        return sorted(por_categoria.items(), key=lambda x: x[1], reverse=True)

    def historico(self):
        """Resumo mensal: salário, gastos e economia de cada mês com lançamentos (mais o mês atual)."""
        por_mes = {}
        for g in self.dados["gastos"]:
            por_mes.setdefault(mes_de(g), []).append(g)
        atual = mes_atual()
        resultado = []
        for m in sorted(set(por_mes) | {atual}):
            gs = por_mes.get(m, [])
            total = sum(g["valor"] for g in gs)
            salario = self.salario_do_mes(m)
            economia = salario - total
            cats = {}
            for g in gs:
                cats[g["categoria"]] = cats.get(g["categoria"], 0) + g["valor"]
            top = max(cats.items(), key=lambda x: x[1])[0] if cats else None
            resultado.append({
                "mes": m, "salario": salario, "gastos": total, "economia": economia,
                "pct": (economia / salario * 100) if salario > 0 else 0,
                "fechado": m < atual, "n": len(gs), "top": top,
            })
        return resultado

    def estado_meta_economia(self):
        salario = self.salario_atual()
        saldo = salario - self.total_gastos()
        meta = self.dados["meta_economia"]
        if meta <= 0:
            return saldo, 0, 0, MUDO
        ratio = max(saldo, 0) / meta
        cor = VERDE if saldo >= meta else (AMARELO if ratio >= 0.5 else VERMELHO)
        return saldo, meta, min(ratio, 1), cor

    # ---------- avisos (toast) ----------

    def toast(self, titulo, texto, cor=OURO):
        self.fila_toast.append((titulo, texto, cor))
        if not self.toast_ativo:
            self._proximo_toast()

    def _proximo_toast(self):
        if not self.fila_toast:
            self.toast_ativo = False
            return
        self.toast_ativo = True
        titulo, texto, cor = self.fila_toast.pop(0)
        card = ctk.CTkFrame(self, corner_radius=12, fg_color=CARD2, border_width=2, border_color=cor)
        ctk.CTkLabel(card, text=titulo, font=("Arial Black", 13), text_color=cor, anchor="w").pack(
            anchor="w", padx=18, pady=(12, 0)
        )
        ctk.CTkLabel(card, text=texto, font=("Arial", 12), text_color=TEXTO, anchor="w",
                     justify="left", wraplength=300).pack(anchor="w", padx=18, pady=(2, 12))
        card.place(relx=1.0, rely=1.0, x=-24, y=-24, anchor="se")
        card.lift()

        def fechar():
            card.destroy()
            self.after(250, self._proximo_toast)

        self.after(3800, fechar)

    # ---------- layout base ----------

    def criar_sidebar(self):
        barra = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=SIDEBAR)
        barra.grid(row=0, column=0, sticky="nsw")
        barra.grid_propagate(False)
        barra.grid_columnconfigure(0, weight=1)
        barra.grid_rowconfigure(10, weight=1)

        marca = ctk.CTkFrame(barra, fg_color="transparent")
        marca.grid(row=0, column=0, sticky="ew", padx=18, pady=(26, 4))
        ctk.CTkLabel(
            marca, text="$", width=38, height=38, corner_radius=19,
            fg_color=OURO, text_color=TEXTO_OURO, font=("Arial Black", 20),
        ).pack(side="left")
        textos = ctk.CTkFrame(marca, fg_color="transparent")
        textos.pack(side="left", padx=10)
        ctk.CTkLabel(textos, text="Tio Patinhas", font=("Arial Black", 15), text_color=TEXTO).pack(anchor="w")
        ctk.CTkLabel(textos, text="Controle financeiro", font=("Arial", 11), text_color=MUDO).pack(anchor="w")

        ctk.CTkFrame(barra, height=1, fg_color=BORDA).grid(
            row=1, column=0, sticky="ew", padx=18, pady=(18, 12)
        )

        itens = [
            ("Início", "▣  Início"),
            ("Gastos", "≡  Gastos"),
            ("Metas", "◎  Metas"),
            ("Gráfico", "◔  Gráficos"),
            ("Histórico", "◷  Histórico"),
            ("Conquistas", "★  Conquistas"),
            ("Dicas", "✦  Dicas"),
        ]
        for i, (nome, rotulo) in enumerate(itens):
            botao = ctk.CTkButton(
                barra, text=rotulo, anchor="w", height=40, corner_radius=10,
                font=("Arial", 14, "bold"), fg_color="transparent",
                text_color=MUDO, hover_color=CARD2,
                command=lambda n=nome: self.mostrar(n),
            )
            botao.grid(row=2 + i, column=0, sticky="ew", padx=14, pady=2)
            self.botoes_menu[nome] = botao

        # salário: fica no rodapé da barra lateral e abre um diálogo para editar
        chip = ctk.CTkFrame(barra, fg_color=CARD, corner_radius=12, border_width=1, border_color=BORDA)
        chip.grid(row=11, column=0, sticky="ew", padx=14, pady=(0, 6))
        ctk.CTkLabel(chip, text="Salário do mês", font=("Arial", 11), text_color=MUDO).pack(
            anchor="w", padx=14, pady=(10, 0)
        )
        self.lbl_salario_chip = ctk.CTkLabel(chip, text="R$ 0,00", font=("Arial Black", 16), text_color=OURO)
        self.lbl_salario_chip.pack(anchor="w", padx=14)
        ctk.CTkButton(
            chip, text="✎  Alterar", height=28, corner_radius=8, fg_color=CARD2,
            hover_color=BORDA, text_color=TEXTO, font=("Arial", 12),
            command=self.abrir_dialogo_salario,
        ).pack(fill="x", padx=12, pady=(6, 12))

        ctk.CTkLabel(barra, text="v0.5 public", font=("Arial", 11), text_color=MUDO).grid(
            row=12, column=0, padx=20, pady=(4, 14), sticky="sw"
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
        elif nome == "Histórico":
            self.after(50, self.desenhar_historico_grafico)

    def cabecalho(self, pagina, titulo, subtitulo, colunas=1):
        topo = ctk.CTkFrame(pagina, fg_color="transparent")
        topo.grid(row=0, column=0, columnspan=colunas, sticky="ew", pady=(0, 18))
        topo.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(topo, text=titulo, font=("Arial Black", 28), text_color=TEXTO).grid(row=0, column=0, sticky="w")
        topo.lbl_sub = ctk.CTkLabel(topo, text=subtitulo, font=("Arial", 13), text_color=MUDO)
        topo.lbl_sub.grid(row=1, column=0, sticky="w")
        return topo

    def criar_card(self, pai, titulo, coluna, cor_destaque, acao=None, linha=1):
        card = ctk.CTkFrame(pai, corner_radius=14, fg_color=CARD, border_width=1, border_color=BORDA)
        card.grid(row=linha, column=coluna, sticky="ew", padx=6)
        ctk.CTkFrame(card, height=4, corner_radius=2, fg_color=cor_destaque).pack(fill="x", padx=18, pady=(14, 0))
        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=18, pady=(10, 0))
        lbl_titulo = ctk.CTkLabel(topo, text=titulo, font=("Arial", 13), text_color=MUDO)
        lbl_titulo.pack(side="left")
        if acao:
            ctk.CTkButton(
                topo, text="✎ Alterar", width=70, height=24, corner_radius=8, fg_color=CARD2,
                hover_color=BORDA, text_color=TEXTO, font=("Arial", 11), command=acao,
            ).pack(side="right")
        valor = ctk.CTkLabel(card, text="R$ 0,00", font=("Arial Black", 23), text_color=TEXTO)
        valor.pack(anchor="w", padx=18, pady=(2, 16))
        valor.lbl_titulo = lbl_titulo
        return valor

    def caixa(self, pai, **grid):
        c = ctk.CTkFrame(pai, corner_radius=14, fg_color=CARD, border_width=1, border_color=BORDA)
        c.grid(**grid)
        return c

    # ---------- diálogo do salário ----------

    def abrir_dialogo_salario(self):
        if self.dialogo_salario is not None and self.dialogo_salario.winfo_exists():
            self.dialogo_salario.focus()
            return

        dlg = ctk.CTkToplevel(self)
        self.dialogo_salario = dlg
        dlg.title("Definir salário")
        largura, altura = 430, 290
        x = self.winfo_x() + (self.winfo_width() - largura) // 2
        y = self.winfo_y() + (self.winfo_height() - altura) // 2
        dlg.geometry(f"{largura}x{altura}+{x}+{y}")
        dlg.resizable(False, False)
        dlg.configure(fg_color=BG)
        dlg.transient(self)

        ctk.CTkLabel(dlg, text="Seu salário", font=("Arial Black", 22), text_color=TEXTO).pack(
            anchor="w", padx=28, pady=(26, 0)
        )
        ctk.CTkLabel(
            dlg, text=f"Vale para {nome_mes(mes_atual())} e para os próximos meses,\naté você alterar de novo.",
            font=("Arial", 12), text_color=MUDO, justify="left",
        ).pack(anchor="w", padx=28, pady=(2, 14))

        entrada = ctk.CTkEntry(
            dlg, placeholder_text="Ex.: 3500,00", height=42,
            fg_color=CARD2, border_color=BORDA, corner_radius=10, font=("Arial", 15),
        )
        entrada.pack(fill="x", padx=28)
        atual = self.salario_atual()
        if atual > 0:
            entrada.insert(0, f"{atual:.2f}".replace(".", ","))

        def salvar():
            try:
                valor = para_float(entrada.get())
                if valor <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Valor inválido", "Digite um salário maior que zero. Ex.: 3500,00", parent=dlg)
                return
            self.definir_salario(valor)
            dlg.destroy()

        botoes = ctk.CTkFrame(dlg, fg_color="transparent")
        botoes.pack(fill="x", padx=28, pady=22)
        botoes.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(
            botoes, text="Cancelar", height=40, corner_radius=10, fg_color=CARD2,
            hover_color=BORDA, text_color=TEXTO, command=dlg.destroy,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(
            botoes, text="Salvar salário", height=40, corner_radius=10, fg_color=OURO,
            hover_color=OURO_HOVER, text_color=TEXTO_OURO, font=("Arial", 13, "bold"), command=salvar,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        entrada.bind("<Return>", lambda e: salvar())
        dlg.after(150, lambda: (dlg.grab_set(), entrada.focus()))

    def definir_salario(self, valor):
        self.dados["salarios"][mes_atual()] = valor
        self.dados["salario"] = valor
        self.salvar_dados()
        self.atualizar()

    # ---------- página: Início ----------

    def criar_pagina_inicio(self):
        p = self.nova_pagina("Início")
        for c in range(3):
            p.grid_columnconfigure(c, weight=1)

        self.topo_inicio = self.cabecalho(p, "Visão geral", "", colunas=3)

        self.card_salario = self.criar_card(p, "Salário", 0, OURO, acao=self.abrir_dialogo_salario)
        self.card_gastos = self.criar_card(p, "Total de gastos", 1, VERMELHO)
        self.card_saldo = self.criar_card(p, "Saldo restante", 2, VERDE)

        # salário comprometido
        prog = self.caixa(p, row=2, column=0, columnspan=2, sticky="nsew", padx=6, pady=(16, 0))
        prog.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(prog, text="Salário comprometido", font=("Arial Black", 14), text_color=TEXTO).grid(
            row=0, column=0, sticky="w", padx=20, pady=(16, 0)
        )
        self.lbl_percentual = ctk.CTkLabel(prog, text="0%", font=("Arial Black", 14), text_color=MUDO)
        self.lbl_percentual.grid(row=0, column=1, sticky="e", padx=20, pady=(16, 0))
        self.barra_salario = ctk.CTkProgressBar(prog, height=14, progress_color=VERDE, fg_color=CARD2)
        self.barra_salario.set(0)
        self.barra_salario.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(10, 18))

        # resumo de conquistas
        conq = self.caixa(p, row=2, column=2, sticky="nsew", padx=6, pady=(16, 0))
        ctk.CTkLabel(conq, text="Conquistas", font=("Arial", 13), text_color=MUDO).pack(anchor="w", padx=18, pady=(14, 0))
        self.lbl_conq_inicio = ctk.CTkLabel(conq, text="0/0", font=("Arial Black", 20), text_color=OURO)
        self.lbl_conq_inicio.pack(anchor="w", padx=18)
        self.lbl_nivel_inicio = ctk.CTkLabel(conq, text="Iniciante", font=("Arial", 12), text_color=MUDO)
        self.lbl_nivel_inicio.pack(anchor="w", padx=18, pady=(0, 14))

        # dica em destaque
        self.caixa_dica = self.caixa(p, row=3, column=0, columnspan=3, sticky="ew", padx=6, pady=(16, 0))
        self.caixa_dica.grid_columnconfigure(1, weight=1)
        self.faixa_dica = ctk.CTkFrame(self.caixa_dica, width=6, corner_radius=3, fg_color=OURO)
        self.faixa_dica.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(14, 0), pady=14)
        self.titulo_dica = ctk.CTkLabel(self.caixa_dica, text="", font=("Arial Black", 14), text_color=TEXTO, anchor="w")
        self.titulo_dica.grid(row=0, column=1, sticky="w", padx=16, pady=(14, 0))
        self.texto_dica = ctk.CTkLabel(
            self.caixa_dica, text="", font=("Arial", 13), text_color=MUDO,
            anchor="w", justify="left", wraplength=700,
        )
        self.texto_dica.grid(row=1, column=1, sticky="w", padx=16, pady=(2, 14))
        ctk.CTkButton(
            self.caixa_dica, text="Ver todas as dicas", width=140, height=32, corner_radius=8,
            fg_color=CARD2, hover_color=BORDA, text_color=TEXTO, font=("Arial", 12),
            command=lambda: self.mostrar("Dicas"),
        ).grid(row=0, column=2, rowspan=2, padx=16)
        self.caixa_dica.bind("<Configure>", lambda e: self.texto_dica.configure(wraplength=max(e.width - 260, 200)))

        # meta de economia
        eco = self.caixa(p, row=4, column=0, columnspan=3, sticky="ew", padx=6, pady=(16, 0))
        eco.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(eco, text="Meta de economia do mês", font=("Arial Black", 14), text_color=TEXTO).grid(
            row=0, column=0, sticky="w", padx=20, pady=(16, 0)
        )
        self.lbl_eco_inicio = ctk.CTkLabel(eco, text="", font=("Arial", 12), text_color=MUDO)
        self.lbl_eco_inicio.grid(row=0, column=1, sticky="e", padx=20, pady=(16, 0))
        self.barra_eco_inicio = ctk.CTkProgressBar(eco, height=14, progress_color=VERDE, fg_color=CARD2)
        self.barra_eco_inicio.set(0)
        self.barra_eco_inicio.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(10, 18))

    # ---------- página: Gastos ----------

    def criar_pagina_gastos(self):
        p = self.nova_pagina("Gastos")
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(2, weight=1)

        self.topo_gastos = self.cabecalho(p, "Gastos", "")

        form = self.caixa(p, row=1, column=0, sticky="ew", pady=(0, 16))
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
            fg_color=OURO, hover_color=OURO_HOVER, text_color=TEXTO_OURO,
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

        categoria = self.menu_categoria.get()
        self.dados["gastos"].append({
            "descricao": descricao,
            "valor": valor,
            "categoria": categoria,
            "data": date.today().strftime("%d/%m/%Y"),
        })
        self.salvar_dados()
        self.entrada_desc.delete(0, "end")
        self.entrada_valor.delete(0, "end")

        # avisa se o gasto encostou ou passou da meta da categoria
        meta = self.dados["metas"].get(categoria, 0)
        if meta > 0:
            gasto_cat = dict(self.gastos_por_categoria()).get(categoria, 0)
            if gasto_cat > meta:
                self.toast("Meta estourada", f"{categoria}: {moeda(gasto_cat)} de {moeda(meta)} "
                           f"(+{moeda(gasto_cat - meta)}).", VERMELHO)
            elif gasto_cat >= 0.9 * meta:
                self.toast("Quase no limite", f"{categoria}: você já usou {gasto_cat / meta * 100:.0f}% da meta.", AMARELO)
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

        mes = mes_atual()
        indices = [i for i, g in enumerate(self.dados["gastos"]) if mes_de(g) == mes]

        if not indices:
            ctk.CTkLabel(
                self.lista_gastos,
                text="Nenhum gasto neste mês.\nPreencha os campos acima e clique em Adicionar.",
                text_color=MUDO, font=("Arial", 13), justify="center",
            ).grid(row=0, column=0, pady=50)
            return

        for pos, i in enumerate(reversed(indices)):
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
            ctk.CTkLabel(
                linha, text=f"{gasto['categoria']}  ·  {gasto.get('data', '')}",
                font=("Arial", 11), text_color=MUDO, anchor="w",
            ).grid(row=1, column=1, sticky="w", padx=14, pady=(0, 10))
            ctk.CTkLabel(linha, text=moeda(gasto["valor"]), font=("Arial Black", 14), text_color=TEXTO).grid(
                row=0, column=2, rowspan=2, padx=14
            )
            ctk.CTkButton(
                linha, text="✕", width=32, height=32, corner_radius=8,
                fg_color="transparent", text_color=MUDO, hover_color=VERMELHO,
                command=lambda idx=i: self.remover_gasto(idx),
            ).grid(row=0, column=3, rowspan=2, padx=(0, 12))

    # ---------- página: Metas ----------

    def criar_pagina_metas(self):
        p = self.nova_pagina("Metas")
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(1, weight=1)

        self.cabecalho(p, "Metas", "Defina limites mensais e acompanhe o quanto já usou")

        rolagem = ctk.CTkScrollableFrame(p, fg_color="transparent")
        rolagem.grid(row=1, column=0, sticky="nsew")
        rolagem.grid_columnconfigure(0, weight=1)

        estilo = dict(height=38, fg_color=CARD2, border_color=BORDA, corner_radius=10)

        # --- meta de economia ---
        eco = self.caixa(rolagem, row=0, column=0, sticky="ew", padx=2, pady=(0, 14))
        eco.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(eco, text="Meta de economia mensal", font=("Arial Black", 15), text_color=TEXTO).grid(
            row=0, column=0, sticky="w", padx=20, pady=(16, 0)
        )
        self.lbl_meta_eco = ctk.CTkLabel(eco, text="", font=("Arial", 12), text_color=MUDO)
        self.lbl_meta_eco.grid(row=0, column=1, columnspan=2, sticky="e", padx=20, pady=(16, 0))
        self.barra_meta_eco = ctk.CTkProgressBar(eco, height=14, progress_color=VERDE, fg_color=CARD2)
        self.barra_meta_eco.set(0)
        self.barra_meta_eco.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20, pady=(10, 12))

        self.entrada_meta_eco = ctk.CTkEntry(eco, placeholder_text="Quanto quer guardar por mês? Ex.: 500,00", **estilo)
        self.entrada_meta_eco.grid(row=2, column=0, sticky="ew", padx=(20, 8), pady=(0, 18))
        self.entrada_meta_eco.bind("<Return>", lambda e: self.definir_meta_economia())
        ctk.CTkButton(
            eco, text="Salvar meta", width=110, height=38, corner_radius=10, fg_color=OURO,
            hover_color=OURO_HOVER, text_color=TEXTO_OURO, font=("Arial", 12, "bold"),
            command=self.definir_meta_economia,
        ).grid(row=2, column=1, padx=4, pady=(0, 18))
        ctk.CTkButton(
            eco, text="Remover", width=80, height=38, corner_radius=10, fg_color=CARD2,
            hover_color=BORDA, text_color=TEXTO, font=("Arial", 12),
            command=lambda: self.definir_meta_economia(remover=True),
        ).grid(row=2, column=2, padx=(4, 20), pady=(0, 18))

        # --- metas por categoria ---
        cat = self.caixa(rolagem, row=1, column=0, sticky="ew", padx=2, pady=(0, 14))
        cat.grid_columnconfigure(2, weight=1)

        topo = ctk.CTkFrame(cat, fg_color="transparent")
        topo.grid(row=0, column=0, columnspan=7, sticky="ew", padx=20, pady=(16, 6))
        topo.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(topo, text="Limite por categoria", font=("Arial Black", 15), text_color=TEXTO).grid(
            row=0, column=0, sticky="w"
        )
        ctk.CTkButton(
            topo, text="Sugerir metas", width=120, height=30, corner_radius=8, fg_color=CARD2,
            hover_color=BORDA, text_color=OURO, font=("Arial", 12, "bold"), command=self.sugerir_metas,
        ).grid(row=0, column=1, padx=(0, 6))
        ctk.CTkButton(
            topo, text="Limpar tudo", width=100, height=30, corner_radius=8, fg_color=CARD2,
            hover_color=BORDA, text_color=TEXTO, font=("Arial", 12), command=self.limpar_metas,
        ).grid(row=0, column=2)

        for i, nome in enumerate(CATEGORIAS):
            r = 1 + i
            ctk.CTkFrame(cat, width=12, height=12, corner_radius=6, fg_color=COR_CATEGORIA[nome]).grid(
                row=r, column=0, padx=(20, 8), pady=10
            )
            ctk.CTkLabel(cat, text=nome, font=("Arial", 13, "bold"), text_color=TEXTO, width=100, anchor="w").grid(
                row=r, column=1, sticky="w"
            )
            barra = ctk.CTkProgressBar(cat, height=12, progress_color=BORDA, fg_color=CARD2)
            barra.set(0)
            barra.grid(row=r, column=2, sticky="ew", padx=10)
            texto = ctk.CTkLabel(cat, text="", font=("Arial", 11), text_color=MUDO, width=230, anchor="e")
            texto.grid(row=r, column=3, padx=(4, 8))
            entrada = ctk.CTkEntry(cat, placeholder_text="R$", width=90, height=32, fg_color=CARD2,
                                   border_color=BORDA, corner_radius=8)
            entrada.grid(row=r, column=4, padx=4)
            entrada.bind("<Return>", lambda e, c=nome: self.definir_meta(c))
            ctk.CTkButton(
                cat, text="Definir", width=64, height=32, corner_radius=8, fg_color=OURO,
                hover_color=OURO_HOVER, text_color=TEXTO_OURO, font=("Arial", 12, "bold"),
                command=lambda c=nome: self.definir_meta(c),
            ).grid(row=r, column=5, padx=4)
            ctk.CTkButton(
                cat, text="✕", width=30, height=32, corner_radius=8, fg_color="transparent",
                text_color=MUDO, hover_color=VERMELHO,
                command=lambda c=nome: self.definir_meta(c, remover=True),
            ).grid(row=r, column=6, padx=(0, 16))
            self.linhas_meta[nome] = {"barra": barra, "texto": texto, "entrada": entrada}

        ctk.CTkLabel(cat, text="", height=6).grid(row=len(CATEGORIAS) + 1, column=0)

    def definir_meta(self, categoria, remover=False):
        if remover:
            self.dados["metas"].pop(categoria, None)
        else:
            try:
                valor = para_float(self.linhas_meta[categoria]["entrada"].get())
                if valor <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Valor inválido", "Digite um limite maior que zero. Ex.: 800,00")
                return
            self.dados["metas"][categoria] = valor
        self.linhas_meta[categoria]["entrada"].delete(0, "end")
        self.salvar_dados()
        self.atualizar()

    def definir_meta_economia(self, remover=False):
        if remover:
            self.dados["meta_economia"] = 0.0
        else:
            try:
                valor = para_float(self.entrada_meta_eco.get())
                if valor <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Valor inválido", "Digite um valor maior que zero. Ex.: 500,00")
                return
            self.dados["meta_economia"] = valor
        self.entrada_meta_eco.delete(0, "end")
        self.salvar_dados()
        self.atualizar()

    def sugerir_metas(self):
        salario = self.salario_atual()
        if salario <= 0:
            messagebox.showinfo("Defina o salário", "Defina seu salário para eu sugerir metas proporcionais a ele.")
            return
        if not messagebox.askyesno(
            "Sugerir metas",
            "Preencher todas as categorias com os limites recomendados para o seu salário?\n"
            "Metas já definidas serão substituídas.",
        ):
            return
        for cat in CATEGORIAS:
            self.dados["metas"][cat] = round(LIMITES[cat] * salario, 2)
        self.salvar_dados()
        self.atualizar()

    def limpar_metas(self):
        if not self.dados["metas"]:
            return
        if messagebox.askyesno("Limpar metas", "Remover todas as metas por categoria?"):
            self.dados["metas"] = {}
            self.salvar_dados()
            self.atualizar()

    def atualizar_metas(self):
        por_cat = dict(self.gastos_por_categoria())
        salario = self.salario_atual()
        for cat, w in self.linhas_meta.items():
            gasto = por_cat.get(cat, 0.0)
            meta = self.dados["metas"].get(cat, 0)
            if meta > 0:
                r = gasto / meta
                cor = VERDE if r <= 0.75 else (AMARELO if r <= 1 else VERMELHO)
                w["barra"].configure(progress_color=cor)
                w["barra"].set(min(r, 1))
                w["texto"].configure(
                    text=f"{moeda(gasto)} de {moeda(meta)}  ·  {r * 100:.0f}%",
                    text_color=cor if r > 0.75 else MUDO,
                )
            else:
                w["barra"].configure(progress_color=BORDA)
                w["barra"].set(0)
                sugestao = f"  ·  sugestão {moeda(LIMITES[cat] * salario)}" if salario > 0 else ""
                w["texto"].configure(text=f"Sem meta{sugestao}", text_color=MUDO)

        saldo, meta, ratio, cor = self.estado_meta_economia()
        if meta > 0:
            self.barra_meta_eco.configure(progress_color=cor)
            self.barra_meta_eco.set(ratio)
            self.lbl_meta_eco.configure(text=f"Sobram {moeda(max(saldo, 0))} de {moeda(meta)}", text_color=cor)
        else:
            self.barra_meta_eco.configure(progress_color=BORDA)
            self.barra_meta_eco.set(0)
            self.lbl_meta_eco.configure(text="Nenhuma meta definida", text_color=MUDO)

    # ---------- página: Gráficos ----------

    def criar_pagina_grafico(self):
        p = self.nova_pagina("Gráfico")
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(1, weight=1)

        topo = self.cabecalho(p, "Gráficos", "")
        self.topo_grafico = topo
        self.seletor_grafico = ctk.CTkSegmentedButton(
            topo, values=["Pizza", "Torres", "Linhas"], command=self.trocar_grafico,
            height=36, font=("Arial", 13, "bold"), fg_color=CARD2,
            selected_color=OURO, selected_hover_color=OURO_HOVER,
            unselected_color=CARD2, unselected_hover_color=BORDA, text_color=TEXTO,
        )
        self.seletor_grafico.set("Pizza")
        self.seletor_grafico.grid(row=0, column=1, rowspan=2, sticky="e")

        moldura = self.caixa(p, row=1, column=0, sticky="nsew")
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
            "Linhas": "Evolução dos gastos acumulados no mês",
        }
        self.titulo_grafico.configure(text=titulos[self.tipo_grafico])

        gastos = self.gastos_do_mes()
        total = sum(g["valor"] for g in gastos)
        if total == 0:
            c.create_text(w / 2, h / 2, text="Adicione gastos neste mês para ver o gráfico.",
                          fill=MUDO, font=("Arial", 13))
            return

        dados = self.gastos_por_categoria()
        if self.tipo_grafico == "Pizza":
            self.grafico_pizza(c, w, h, dados, total)
        elif self.tipo_grafico == "Torres":
            self.grafico_torres(c, w, h, dados)
        else:
            self.grafico_linhas(c, w, h, gastos)

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

        furo = r * 0.58
        c.create_oval(cx - furo, cy - furo, cx + furo, cy + furo, fill=CARD, outline=CARD)
        c.create_text(cx, cy - 12, text="Total", fill=MUDO, font=("Arial", 12))
        c.create_text(cx, cy + 12, text=moeda(total), fill=TEXTO, font=("Arial Black", 15))

        x0 = area_w + 20
        altura_item = 38
        y = cy - (len(dados) * altura_item) / 2
        for categoria, valor in dados:
            cor = COR_CATEGORIA.get(categoria, MUDO)
            c.create_rectangle(x0, y + 6, x0 + 14, y + 20, fill=cor, outline=cor)
            c.create_text(x0 + 24, y + 4, text=categoria, fill=TEXTO, font=("Arial", 12, "bold"), anchor="nw")
            c.create_text(x0 + 24, y + 22, text=f"{moeda(valor)}  ·  {valor / total * 100:.0f}%",
                          fill=MUDO, font=("Arial", 11), anchor="nw")
            y += altura_item

    def eixo_y(self, c, w, minimo, maximo, esq, dir_, topo, base):
        passos = 4
        for k in range(passos + 1):
            valor = minimo + (maximo - minimo) * k / passos
            y = base - (base - topo) * k / passos
            c.create_line(esq, y, w - dir_, y, fill=BORDA, dash=(2, 4))
            c.create_text(esq - 10, y, text=moeda_curta(valor), fill=MUDO, font=("Arial", 10), anchor="e")

    def grafico_torres(self, c, w, h, dados):
        esq, dir_, topo, base = 90, 30, 30, h - 60
        if base - topo < 60 or w - esq - dir_ < 100:
            return
        maximo = max(v for _, v in dados) * 1.15
        self.eixo_y(c, w, 0, maximo, esq, dir_, topo, base)

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
            meta = self.dados["metas"].get(categoria, 0)
            if 0 < meta <= maximo:  # marca a meta da categoria sobre a torre
                ym = base - (base - topo) * meta / maximo
                c.create_line(cx - largura / 2 - 6, ym, cx + largura / 2 + 6, ym, fill=OURO, width=2, dash=(4, 3))
        c.create_line(esq, base, w - dir_, base, fill=MUDO)
        if any(0 < self.dados["metas"].get(cat, 0) for cat, _ in dados):
            c.create_text(w - dir_, topo - 14, text="- - -  meta da categoria", fill=OURO, font=("Arial", 10), anchor="e")

    def grafico_linhas(self, c, w, h, gastos):
        esq, dir_, topo, base = 90, 40, 30, h - 60
        if base - topo < 60 or w - esq - dir_ < 100:
            return

        acumulado, soma = [], 0
        for g in gastos:
            soma += g["valor"]
            acumulado.append(soma)

        salario = self.salario_atual()
        maximo = max(acumulado[-1], salario if salario > 0 else 0) * 1.15
        self.eixo_y(c, w, 0, maximo, esq, dir_, topo, base)

        n = len(acumulado)
        largura = w - esq - dir_

        def pos_x(i):
            return esq + largura / 2 if n == 1 else esq + 20 + (largura - 40) * i / (n - 1)

        def pos_y(v):
            return base - (base - topo) * v / maximo

        if salario > 0:
            ys = pos_y(salario)
            c.create_line(esq, ys, w - dir_, ys, fill=OURO, dash=(6, 4), width=2)
            c.create_text(w - dir_, ys - 10, text=f"Salário {moeda_curta(salario)}", fill=OURO,
                          font=("Arial", 10, "bold"), anchor="e")

        pontos = [(pos_x(i), pos_y(v)) for i, v in enumerate(acumulado)]

        if n > 1:
            area = [(pontos[0][0], base)] + pontos + [(pontos[-1][0], base)]
            c.create_polygon([coord for p in area for coord in p], fill=VERMELHO, stipple="gray12", outline="")
            c.create_line([coord for p in pontos for coord in p], fill=VERMELHO, width=3)

        passo = max(1, math.ceil(n / 8))
        for i, (x, y) in enumerate(pontos):
            c.create_oval(x - 5, y - 5, x + 5, y + 5, fill=VERMELHO, outline=CARD, width=2)
            if i % passo == 0 or i == n - 1:
                rotulo = gastos[i].get("data", "")[:5] or f"#{i + 1}"
                c.create_text(x, base + 18, text=rotulo, fill=MUDO, font=("Arial", 10))
        c.create_text(pontos[-1][0], pontos[-1][1] - 14, text=moeda(acumulado[-1]),
                      fill=TEXTO, font=("Arial", 11, "bold"))
        c.create_line(esq, base, w - dir_, base, fill=MUDO)

    # ---------- página: Histórico ----------

    def criar_pagina_historico(self):
        p = self.nova_pagina("Histórico")
        for c in range(3):
            p.grid_columnconfigure(c, weight=1)
        p.grid_rowconfigure(3, weight=1)

        self.cabecalho(p, "Histórico mensal", "Quanto você economizou em cada mês de uso do app", colunas=3)

        self.card_hist_acum = self.criar_card(p, "Economia acumulada", 0, VERDE)
        self.card_hist_melhor = self.criar_card(p, "Melhor mês", 1, OURO)
        self.card_hist_azul = self.criar_card(p, "Meses no azul", 2, AZUL)

        moldura = self.caixa(p, row=2, column=0, columnspan=3, sticky="ew", padx=6, pady=(14, 0))
        moldura.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(moldura, text="Economia por mês", font=("Arial Black", 14), text_color=TEXTO).grid(
            row=0, column=0, sticky="w", padx=20, pady=(14, 0)
        )
        self.canvas_hist = tk.Canvas(moldura, bg=CARD, highlightthickness=0, bd=0, height=230)
        self.canvas_hist.grid(row=1, column=0, sticky="ew", padx=10, pady=(4, 10))
        self.canvas_hist.bind("<Configure>", lambda e: self.desenhar_historico_grafico())

        self.lista_hist = ctk.CTkScrollableFrame(p, corner_radius=14, fg_color=CARD, border_width=1, border_color=BORDA)
        self.lista_hist.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=6, pady=(14, 0))
        self.lista_hist.grid_columnconfigure(0, weight=1)

    def desenhar_historico_grafico(self):
        c = self.canvas_hist
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 80 or h < 80:
            return

        dados = [x for x in self.historico() if x["salario"] > 0][-12:]
        if not dados:
            c.create_text(w / 2, h / 2, text="Defina seu salário e registre gastos para ver o histórico.",
                          fill=MUDO, font=("Arial", 13))
            return

        esq, dir_, topo, base = 90, 30, 22, h - 36
        vmax = max(0, max(d["economia"] for d in dados))
        vmin = min(0, min(d["economia"] for d in dados))
        if vmax == vmin:
            vmax = 1
        folga = (vmax - vmin) * 0.12
        vmax += folga
        if vmin < 0:
            vmin -= folga
        span = vmax - vmin

        def pos_y(v):
            return topo + (vmax - v) / span * (base - topo)

        self.eixo_y(c, w, vmin, vmax, esq, dir_, topo, base)
        c.create_line(esq, pos_y(0), w - dir_, pos_y(0), fill=MUDO)

        n = len(dados)
        espaco = (w - esq - dir_) / n
        largura = min(espaco * 0.55, 70)
        for i, d in enumerate(dados):
            cx = esq + espaco * i + espaco / 2
            y, y0 = pos_y(d["economia"]), pos_y(0)
            cor = VERDE if d["economia"] >= 0 else VERMELHO
            c.create_rectangle(
                cx - largura / 2, min(y, y0), cx + largura / 2, max(y, y0),
                fill=cor, outline=cor, stipple="gray50" if not d["fechado"] else "",
            )
            ytexto = y - 10 if d["economia"] >= 0 else y + 10
            c.create_text(cx, ytexto, text=moeda_curta(d["economia"]), fill=TEXTO, font=("Arial", 10, "bold"))
            rotulo = nome_mes(d["mes"], curto=True) + ("*" if not d["fechado"] else "")
            c.create_text(cx, base + 18, text=rotulo, fill=MUDO, font=("Arial", 10))
        c.create_text(w - dir_, 8, text="* mês em andamento (parcial)", fill=MUDO, font=("Arial", 9), anchor="e")

    def desenhar_historico(self):
        hist = self.historico()
        com_salario = [h for h in hist if h["salario"] > 0]
        fechados = [h for h in com_salario if h["fechado"]]

        acumulado = sum(max(h["economia"], 0) for h in fechados)
        self.card_hist_acum.configure(text=moeda(acumulado))

        if com_salario:
            melhor = max(com_salario, key=lambda h: h["economia"])
            self.card_hist_melhor.configure(text=moeda(melhor["economia"]))
            self.card_hist_melhor.lbl_titulo.configure(text=f"Melhor mês · {nome_mes(melhor['mes'], curto=True)}")
        else:
            self.card_hist_melhor.configure(text="—")
            self.card_hist_melhor.lbl_titulo.configure(text="Melhor mês")

        azuis = sum(1 for h in fechados if h["economia"] >= 0)
        self.card_hist_azul.configure(text=f"{azuis} de {len(fechados)}" if fechados else "—")

        for widget in self.lista_hist.winfo_children():
            widget.destroy()

        for i, h in enumerate(reversed(hist)):
            linha = ctk.CTkFrame(self.lista_hist, fg_color=CARD2, corner_radius=10)
            linha.grid(row=i, column=0, sticky="ew", pady=4, padx=4)
            linha.grid_columnconfigure(0, weight=1)

            esq = ctk.CTkFrame(linha, fg_color="transparent")
            esq.grid(row=0, column=0, sticky="w", padx=16, pady=10)
            titulo = nome_mes(h["mes"]) + ("   · em andamento" if not h["fechado"] else "")
            ctk.CTkLabel(esq, text=titulo, font=("Arial", 14, "bold"), text_color=TEXTO, anchor="w").pack(anchor="w")
            partes = [f"Salário {moeda(h['salario'])}", f"Gastos {moeda(h['gastos'])}", f"{h['n']} lançamentos"]
            if h["top"]:
                partes.append(f"maior gasto: {h['top']}")
            ctk.CTkLabel(esq, text="  ·  ".join(partes), font=("Arial", 11), text_color=MUDO, anchor="w").pack(anchor="w")

            if h["salario"] > 0:
                cor = VERDE if h["economia"] >= 0 else VERMELHO
                direita = ctk.CTkFrame(linha, fg_color="transparent")
                direita.grid(row=0, column=1, padx=18)
                ctk.CTkLabel(direita, text=moeda(h["economia"]), font=("Arial Black", 15), text_color=cor).pack(anchor="e")
                rotulo = "economizado" if h["economia"] >= 0 else "no vermelho"
                ctk.CTkLabel(direita, text=f"{h['pct']:.0f}% do salário · {rotulo}", font=("Arial", 11),
                             text_color=MUDO).pack(anchor="e")
            else:
                ctk.CTkLabel(linha, text="Sem salário definido", font=("Arial", 12), text_color=MUDO).grid(
                    row=0, column=1, padx=18
                )

        self.desenhar_historico_grafico()

    # ---------- conquistas ----------

    def calcular_stats(self):
        gastos = self.dados["gastos"]
        hist = self.historico()
        fechados = [h for h in hist if h["fechado"] and h["salario"] > 0]

        seq = melhor = 0
        for h in fechados:
            if h["economia"] >= 0:
                seq += 1
                melhor = max(melhor, seq)
            else:
                seq = 0

        metas = {c: v for c, v in self.dados["metas"].items() if v > 0}
        por_cat = dict(self.gastos_por_categoria())
        meta_eco = self.dados["meta_economia"]

        return {
            "n_gastos": len(gastos),
            "salario_definido": any(v > 0 for v in self.dados["salarios"].values()),
            "n_metas": len(metas),
            "n_cats": len({g["categoria"] for g in gastos}),
            "dentro_metas": len(metas) >= 3 and bool(self.gastos_do_mes())
                            and all(por_cat.get(c, 0) <= v for c, v in metas.items()),
            "fechou_azul": any(h["economia"] >= 0 for h in fechados),
            "poupador20": any(h["pct"] >= 20 for h in fechados),
            "meta_eco_batida": meta_eco > 0 and any(h["economia"] >= meta_eco for h in fechados),
            "streak": melhor,
            "acumulado": sum(max(h["economia"], 0) for h in fechados),
        }

    def verificar_conquistas(self):
        self.stats = self.calcular_stats()
        hoje = date.today().strftime("%d/%m/%Y")
        novas = []
        for cq in CONQUISTAS:
            if cq["id"] not in self.dados["conquistas"] and cq["ok"](self.stats):
                self.dados["conquistas"][cq["id"]] = hoje
                novas.append(cq)
        if novas:
            self.salvar_dados()
            if len(novas) > 3:
                self.toast("🏆 Conquistas desbloqueadas", f"{len(novas)} novas conquistas! Veja na aba Conquistas.")
            else:
                for cq in novas:
                    self.toast("🏆 Conquista desbloqueada", f"{cq['icone']}  {cq['nome']}")

    def nivel_atual(self):
        n = len(self.dados["conquistas"])
        return [nome for minimo, nome in NIVEIS if n >= minimo][-1]

    def criar_pagina_conquistas(self):
        p = self.nova_pagina("Conquistas")
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(2, weight=1)

        self.cabecalho(p, "Conquistas", "Desbloqueie medalhas ao cuidar bem do seu dinheiro")

        resumo = self.caixa(p, row=1, column=0, sticky="ew", pady=(0, 14))
        resumo.grid_columnconfigure(1, weight=1)
        self.lbl_nivel = ctk.CTkLabel(resumo, text="Iniciante", font=("Arial Black", 20), text_color=OURO)
        self.lbl_nivel.grid(row=0, column=0, sticky="w", padx=20, pady=(16, 0))
        self.lbl_conq_total = ctk.CTkLabel(resumo, text="", font=("Arial", 13), text_color=MUDO)
        self.lbl_conq_total.grid(row=0, column=1, sticky="e", padx=20, pady=(16, 0))
        self.barra_conq = ctk.CTkProgressBar(resumo, height=12, progress_color=OURO, fg_color=CARD2)
        self.barra_conq.set(0)
        self.barra_conq.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(8, 16))

        self.lista_conquistas = ctk.CTkScrollableFrame(p, fg_color="transparent")
        self.lista_conquistas.grid(row=2, column=0, sticky="nsew")
        self.lista_conquistas.grid_columnconfigure((0, 1), weight=1, uniform="cq")

    def desenhar_conquistas(self):
        total = len(CONQUISTAS)
        n = len(self.dados["conquistas"])
        self.lbl_nivel.configure(text=f"Nível: {self.nivel_atual()}")
        self.lbl_conq_total.configure(text=f"{n} de {total} conquistas")
        self.barra_conq.set(n / total)

        for widget in self.lista_conquistas.winfo_children():
            widget.destroy()

        for i, cq in enumerate(CONQUISTAS):
            data = self.dados["conquistas"].get(cq["id"])
            ok = data is not None
            linha, col = divmod(i, 2)

            card = ctk.CTkFrame(self.lista_conquistas, corner_radius=14, fg_color=CARD,
                                border_width=1, border_color=OURO if ok else BORDA)
            card.grid(row=linha, column=col, sticky="nsew", padx=6, pady=6)
            card.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                card, text=cq["icone"] if ok else "🔒", width=56, height=56, corner_radius=28,
                fg_color=OURO if ok else CARD2, text_color=TEXTO_OURO if ok else MUDO, font=("Arial", 24),
            ).grid(row=0, column=0, rowspan=3, padx=16, pady=16)

            ctk.CTkLabel(card, text=cq["nome"], font=("Arial Black", 14),
                         text_color=TEXTO if ok else MUDO, anchor="w").grid(
                row=0, column=1, sticky="w", padx=(0, 14), pady=(16, 0))
            ctk.CTkLabel(card, text=cq["desc"], font=("Arial", 12), text_color=MUDO, anchor="w",
                         justify="left", wraplength=260).grid(row=1, column=1, sticky="w", padx=(0, 14))

            if ok:
                ctk.CTkLabel(card, text=f"Desbloqueada em {data}", font=("Arial", 11, "bold"),
                             text_color=OURO, anchor="w").grid(row=2, column=1, sticky="w", padx=(0, 14), pady=(2, 16))
            elif "prog" in cq and self.stats:
                atual, alvo, tipo = cq["prog"](self.stats)
                barra = ctk.CTkProgressBar(card, height=8, progress_color=OURO, fg_color=CARD2)
                barra.set(min(atual / alvo, 1))
                barra.grid(row=2, column=1, sticky="ew", padx=(0, 14), pady=(6, 2))
                texto = f"{moeda(atual)} / {moeda(alvo)}" if tipo == "$" else f"{int(atual)} / {int(alvo)}"
                ctk.CTkLabel(card, text=texto, font=("Arial", 11), text_color=MUDO, anchor="w").grid(
                    row=3, column=1, sticky="w", padx=(0, 14), pady=(0, 14))
            else:
                ctk.CTkLabel(card, text="Bloqueada", font=("Arial", 11), text_color=MUDO, anchor="w").grid(
                    row=2, column=1, sticky="w", padx=(0, 14), pady=(2, 16))

        # resumo na tela inicial
        self.lbl_conq_inicio.configure(text=f"{n}/{total}")
        self.lbl_nivel_inicio.configure(text=f"Nível: {self.nivel_atual()}")

    # ---------- página: Dicas ----------

    def criar_pagina_dicas(self):
        p = self.nova_pagina("Dicas")
        p.grid_columnconfigure((0, 1, 2), weight=1)
        p.grid_rowconfigure(4, weight=1)

        self.cabecalho(p, "Dicas de economia", "Análise do mês com base no seu salário, nas metas e nos seus gastos", colunas=3)

        # saúde financeira (com anel de pontuação)
        saude = self.caixa(p, row=1, column=0, sticky="nsew", padx=6)
        self.canvas_anel = tk.Canvas(saude, width=90, height=90, bg=CARD, highlightthickness=0, bd=0)
        self.canvas_anel.pack(side="left", padx=(16, 8), pady=14)
        txt = ctk.CTkFrame(saude, fg_color="transparent")
        txt.pack(side="left", padx=(0, 12))
        ctk.CTkLabel(txt, text="Saúde financeira", font=("Arial", 13), text_color=MUDO).pack(anchor="w")
        self.lbl_saude = ctk.CTkLabel(txt, text="—", font=("Arial Black", 18), text_color=TEXTO)
        self.lbl_saude.pack(anchor="w")

        pot = self.caixa(p, row=1, column=1, sticky="nsew", padx=6)
        ctk.CTkLabel(pot, text="Economia potencial", font=("Arial", 13), text_color=MUDO).pack(anchor="w", padx=18, pady=(18, 0))
        self.lbl_potencial = ctk.CTkLabel(pot, text="R$ 0,00", font=("Arial Black", 22), text_color=VERDE)
        self.lbl_potencial.pack(anchor="w", padx=18)
        ctk.CTkLabel(pot, text="se voltar aos limites neste mês", font=("Arial", 11), text_color=MUDO).pack(
            anchor="w", padx=18, pady=(0, 16))

        ale = self.caixa(p, row=1, column=2, sticky="nsew", padx=6)
        ctk.CTkLabel(ale, text="Pontos de atenção", font=("Arial", 13), text_color=MUDO).pack(anchor="w", padx=18, pady=(18, 0))
        self.lbl_alertas = ctk.CTkLabel(ale, text="0", font=("Arial Black", 22), text_color=TEXTO)
        self.lbl_alertas.pack(anchor="w", padx=18)
        self.lbl_alertas_sub = ctk.CTkLabel(ale, text="", font=("Arial", 11), text_color=MUDO)
        self.lbl_alertas_sub.pack(anchor="w", padx=18, pady=(0, 16))

        # dica do dia
        dia = self.caixa(p, row=2, column=0, columnspan=3, sticky="ew", padx=6, pady=(14, 0))
        dia.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(dia, text="💡", font=("Arial", 26), width=50).grid(row=0, column=0, rowspan=2, padx=(14, 0), pady=14)
        ctk.CTkLabel(dia, text="Dica do dia", font=("Arial Black", 13), text_color=OURO, anchor="w").grid(
            row=0, column=1, sticky="w", padx=10, pady=(12, 0))
        self.lbl_dica_dia = ctk.CTkLabel(dia, text="", font=("Arial", 13), text_color=TEXTO, anchor="w",
                                         justify="left", wraplength=800)
        self.lbl_dica_dia.grid(row=1, column=1, sticky="w", padx=10, pady=(0, 14))
        dia.bind("<Configure>", lambda e: self.lbl_dica_dia.configure(wraplength=max(e.width - 110, 200)))

        # filtro
        filtro = ctk.CTkSegmentedButton(
            p, values=["Todas", "Alertas", "Atenção", "Positivas"], command=self.trocar_filtro_dicas,
            height=34, font=("Arial", 12, "bold"), fg_color=CARD2,
            selected_color=OURO, selected_hover_color=OURO_HOVER,
            unselected_color=CARD2, unselected_hover_color=BORDA, text_color=TEXTO,
        )
        filtro.set("Todas")
        filtro.grid(row=3, column=0, columnspan=3, sticky="w", padx=6, pady=(14, 8))

        self.lista_dicas = ctk.CTkScrollableFrame(p, fg_color="transparent")
        self.lista_dicas.grid(row=4, column=0, columnspan=3, sticky="nsew")
        self.lista_dicas.grid_columnconfigure(0, weight=1)

    def trocar_filtro_dicas(self, valor):
        self.filtro_dicas = valor
        self.desenhar_dicas()

    def gerar_dicas(self):
        """Lista de dicas do mês atual, da mais urgente para a menos urgente.
        Cada item: nivel (alerta | atencao | ok | info), titulo, texto, extras, economia."""
        salario = self.salario_atual()
        gs = self.gastos_do_mes()
        total = sum(g["valor"] for g in gs)
        metas = {c: v for c, v in self.dados["metas"].items() if v > 0}
        meta_eco = self.dados["meta_economia"]

        def item(nivel, titulo, texto, extras=None, economia=0.0):
            return {"nivel": nivel, "titulo": titulo, "texto": texto, "extras": extras or [], "economia": economia}

        if salario <= 0:
            return [item("info", "Defina seu salário",
                         "Para saber se algum gasto está exagerado, preciso do seu salário. "
                         "Use o botão Alterar, no rodapé do menu lateral.")]
        if not gs:
            return [item("info", "Nenhum gasto neste mês",
                         "Cadastre seus gastos na tela Gastos para receber dicas personalizadas.")]

        itens = []
        if total > salario:
            itens.append(item(
                "alerta", "Você gastou mais do que ganha",
                f"Seus gastos ({moeda(total)}) superam o salário ({moeda(salario)}) em {moeda(total - salario)}. "
                "Priorize cortar despesas não essenciais e evite usar crédito para cobrir a diferença.",
                economia=total - salario,
            ))

        metas_ok = bool(metas)
        for categoria, valor in self.gastos_por_categoria():
            meta = metas.get(categoria)
            limite = meta if meta else LIMITES.get(categoria, 0.10) * salario
            if valor > limite:
                excesso = valor - limite
                nivel = "alerta" if valor > limite * 1.25 else "atencao"
                if meta:
                    metas_ok = False
                    titulo = f"Meta de {categoria} estourada"
                    texto = (f"Você gastou {moeda(valor)} e sua meta era {moeda(meta)}: passou {moeda(excesso)}, "
                             f"o que representa {valor / salario * 100:.0f}% do salário.")
                else:
                    titulo = f"{categoria} está acima do ideal"
                    texto = (f"Você gastou {moeda(valor)} ({valor / salario * 100:.0f}% do salário). "
                             f"O recomendado é até {LIMITES.get(categoria, 0.10) * 100:.0f}% ({moeda(limite)}). "
                             f"Dá para reduzir cerca de {moeda(excesso)}.")
                itens.append(item(nivel, titulo, texto, DICAS.get(categoria, [])[:3], excesso))
            elif meta and valor >= 0.9 * meta:
                itens.append(item(
                    "atencao", f"{categoria} está perto do limite",
                    f"Você já usou {valor / meta * 100:.0f}% da meta ({moeda(valor)} de {moeda(meta)}). "
                    f"Restam {moeda(meta - valor)} neste mês.",
                    DICAS.get(categoria, [])[:1],
                ))

        saldo = salario - total
        if 0 <= saldo and saldo / salario < 0.20:
            itens.append(item(
                "atencao", "Sua reserva está baixa",
                f"Sobram {moeda(saldo)} ({saldo / salario * 100:.0f}% do salário). Tente guardar pelo menos 20% "
                f"({moeda(salario * 0.2)}) todo mês, de preferência assim que receber.",
                ["Programe uma transferência automática para a poupança ou um investimento logo após o pagamento."],
                salario * 0.2 - saldo,
            ))

        if meta_eco > 0 and saldo < meta_eco:
            faltam = meta_eco - max(saldo, 0)
            itens.append(item(
                "atencao", "Meta de economia em risco",
                f"Sua meta é guardar {moeda(meta_eco)} por mês, mas hoje sobram {moeda(max(saldo, 0))}. "
                f"Faltam {moeda(faltam)}.",
            ))

        if metas and metas_ok:
            itens.append(item("ok", "Metas em dia",
                              f"Todas as suas {len(metas)} metas por categoria estão dentro do limite neste mês. Continue assim!"))

        if not any(i["nivel"] in ("alerta", "atencao") for i in itens):
            itens.append(item(
                "ok", "Orçamento saudável",
                f"Nenhuma categoria passou do limite e você ainda guarda {moeda(saldo)} "
                f"({saldo / salario * 100:.0f}% do salário). Considere investir esse valor para fazê-lo render.",
            ))

        ordem = {"alerta": 0, "atencao": 1, "info": 2, "ok": 3}
        itens.sort(key=lambda i: (ordem[i["nivel"]], -i["economia"]))
        return itens

    def pontuacao(self, itens):
        if all(i["nivel"] == "info" for i in itens):
            return None
        pontos = 100
        for i in itens:
            pontos -= 20 if i["nivel"] == "alerta" else (10 if i["nivel"] == "atencao" else 0)
        return max(0, pontos)

    def desenhar_anel(self, score):
        c = self.canvas_anel
        c.delete("all")
        c.create_arc(10, 10, 80, 80, start=0, extent=359.9, style="arc", outline=CARD2, width=9)
        if score is None:
            c.create_text(45, 45, text="—", fill=MUDO, font=("Arial Black", 18))
            return
        cor = VERDE if score >= 70 else (AMARELO if score >= 40 else VERMELHO)
        if score > 0:
            c.create_arc(10, 10, 80, 80, start=90, extent=-min(359.9, 3.6 * score), style="arc", outline=cor, width=9)
        c.create_text(45, 45, text=str(score), fill=TEXTO, font=("Arial Black", 18))

    def desenhar_dicas(self, itens=None):
        itens = itens if itens is not None else self.gerar_dicas()

        # resumo
        score = self.pontuacao(itens)
        self.desenhar_anel(score)
        if score is None:
            self.lbl_saude.configure(text="—", text_color=MUDO)
        else:
            rotulo, cor = (("Excelente", VERDE) if score >= 80 else ("Boa", VERDE) if score >= 60
                           else ("Atenção", AMARELO) if score >= 40 else ("Crítica", VERMELHO))
            self.lbl_saude.configure(text=rotulo, text_color=cor)
        self.lbl_potencial.configure(text=moeda(sum(i["economia"] for i in itens)))
        n_alertas = sum(1 for i in itens if i["nivel"] == "alerta")
        n_atencao = sum(1 for i in itens if i["nivel"] == "atencao")
        self.lbl_alertas.configure(text=str(n_alertas + n_atencao),
                                   text_color=VERMELHO if n_alertas else (AMARELO if n_atencao else VERDE))
        self.lbl_alertas_sub.configure(text=f"{n_alertas} alerta(s) · {n_atencao} atenção")
        self.lbl_dica_dia.configure(text=DICAS_GERAIS[date.today().toordinal() % len(DICAS_GERAIS)])

        # lista filtrada
        filtros = {"Todas": None, "Alertas": "alerta", "Atenção": "atencao", "Positivas": "ok"}
        nivel_filtro = filtros[self.filtro_dicas]
        visiveis = [i for i in itens if nivel_filtro is None or i["nivel"] == nivel_filtro]

        for widget in self.lista_dicas.winfo_children():
            widget.destroy()

        if not visiveis:
            ctk.CTkLabel(self.lista_dicas, text="Nada por aqui neste filtro.", text_color=MUDO,
                         font=("Arial", 13)).grid(row=0, column=0, pady=40)
            return

        cores = {"alerta": VERMELHO, "atencao": AMARELO, "ok": VERDE, "info": AZUL}
        rotulos = {"alerta": "Alerta", "atencao": "Atenção", "ok": "Tudo certo", "info": "Informação"}

        for i, it in enumerate(visiveis):
            cor = cores[it["nivel"]]
            card = ctk.CTkFrame(self.lista_dicas, corner_radius=14, fg_color=CARD, border_width=1, border_color=BORDA)
            card.grid(row=i, column=0, sticky="ew", pady=6, padx=2)
            card.grid_columnconfigure(1, weight=1)

            ctk.CTkFrame(card, width=6, corner_radius=3, fg_color=cor).grid(
                row=0, column=0, rowspan=3, sticky="ns", padx=(14, 0), pady=14)
            ctk.CTkLabel(card, text=it["titulo"], font=("Arial Black", 15), text_color=TEXTO, anchor="w").grid(
                row=0, column=1, sticky="w", padx=16, pady=(14, 0))
            ctk.CTkLabel(card, text=rotulos[it["nivel"]], width=86, height=22, corner_radius=11, fg_color=cor,
                         text_color=TEXTO_OURO, font=("Arial", 11, "bold")).grid(
                row=0, column=2, padx=(8, 16), pady=(14, 0), sticky="e")

            corpo = ctk.CTkLabel(card, text=it["texto"], font=("Arial", 13), text_color=MUDO,
                                 anchor="w", justify="left", wraplength=700)
            corpo.grid(row=1, column=1, columnspan=2, sticky="w", padx=16, pady=(4, 6))
            card.bind("<Configure>", lambda e, lb=corpo: lb.configure(wraplength=max(e.width - 90, 200)))

            if it["economia"] > 0 and it["nivel"] != "ok":
                ctk.CTkLabel(card, text=f"Economia possível: {moeda(it['economia'])}", font=("Arial", 12, "bold"),
                             text_color=VERDE, anchor="w").grid(row=2, column=1, sticky="w", padx=16, pady=(0, 6))

            if it["extras"]:
                estado = {"aberto": i == 0}
                bloco = ctk.CTkFrame(card, fg_color=CARD2, corner_radius=10)
                bloco.grid(row=3, column=1, columnspan=2, sticky="ew", padx=16, pady=(2, 8))
                for dica in it["extras"]:
                    ctk.CTkLabel(bloco, text=f"•  {dica}", font=("Arial", 12), text_color=TEXTO, anchor="w",
                                 justify="left", wraplength=640).pack(anchor="w", padx=14, pady=5)
                botao = ctk.CTkButton(card, text="", height=28, corner_radius=8, fg_color="transparent",
                                      hover_color=CARD2, text_color=cor, font=("Arial", 12, "bold"), anchor="w")
                botao.grid(row=4, column=1, sticky="w", padx=10, pady=(0, 10))

                def alternar(est=estado, bl=bloco, bt=botao):
                    est["aberto"] = not est["aberto"]
                    if est["aberto"]:
                        bl.grid()
                        bt.configure(text="Ocultar dicas  ▴")
                    else:
                        bl.grid_remove()
                        bt.configure(text="Ver dicas  ▾")

                botao.configure(command=alternar)
                if estado["aberto"]:
                    botao.configure(text="Ocultar dicas  ▴")
                else:
                    bloco.grid_remove()
                    botao.configure(text="Ver dicas  ▾")
            else:
                ctk.CTkLabel(card, text="", height=4).grid(row=4, column=1)

    # ---------- atualização geral ----------

    def atualizar(self):
        mes = mes_atual()
        salario = self.salario_atual()
        gastos = self.total_gastos()
        saldo = salario - gastos

        self.topo_inicio.lbl_sub.configure(text=f"Como está o seu dinheiro em {nome_mes(mes)}")
        self.topo_gastos.lbl_sub.configure(
            text=f"Lançamentos de {nome_mes(mes)}  ·  meses anteriores ficam no Histórico")
        self.topo_grafico.lbl_sub.configure(text=f"Dados de {nome_mes(mes)}")

        self.lbl_salario_chip.configure(text=moeda(salario))
        self.card_salario.configure(text=moeda(salario))
        self.card_gastos.configure(text=moeda(gastos))
        self.card_saldo.configure(text=moeda(saldo), text_color=VERDE if saldo >= 0 else VERMELHO)

        if salario > 0:
            uso = gastos / salario
            cor = VERDE if uso < 0.7 else (AMARELO if uso <= 1 else VERMELHO)
            self.barra_salario.set(min(uso, 1))
            self.barra_salario.configure(progress_color=cor)
            self.lbl_percentual.configure(text=f"{uso * 100:.0f}%", text_color=cor)
        else:
            self.barra_salario.set(0)
            self.lbl_percentual.configure(text="Defina seu salário", text_color=MUDO)

        # meta de economia na tela inicial
        saldo_eco, meta, ratio, cor_eco = self.estado_meta_economia()
        if meta > 0:
            self.barra_eco_inicio.configure(progress_color=cor_eco)
            self.barra_eco_inicio.set(ratio)
            self.lbl_eco_inicio.configure(text=f"Sobram {moeda(max(saldo_eco, 0))} de {moeda(meta)}", text_color=cor_eco)
        else:
            self.barra_eco_inicio.configure(progress_color=BORDA)
            self.barra_eco_inicio.set(0)
            self.lbl_eco_inicio.configure(text="Defina uma meta na tela Metas", text_color=MUDO)

        # dica em destaque (a mais urgente)
        itens = self.gerar_dicas()
        cores = {"alerta": VERMELHO, "atencao": AMARELO, "ok": VERDE, "info": AZUL}
        destaque = itens[0]
        self.faixa_dica.configure(fg_color=cores[destaque["nivel"]])
        self.titulo_dica.configure(text=destaque["titulo"])
        self.texto_dica.configure(text=destaque["texto"])

        self.verificar_conquistas()

        self.desenhar_lista()
        self.desenhar_grafico()
        self.atualizar_metas()
        self.desenhar_historico()
        self.desenhar_conquistas()
        self.desenhar_dicas(itens)


if __name__ == "__main__":
    app = App()
    app.mainloop()
