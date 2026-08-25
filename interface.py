import re
import sqlite3
import tkinter as tk
from datetime import datetime, timedelta, timezone
from tkinter import messagebox, ttk

BANCO = "cadastros.db"
FUSO_BRASILIA = timezone(timedelta(hours=-3))

CORES = {
    "principal": "#008C85",
    "principal_escura": "#006B66",
    "fundo": "#F2F5F5",
    "branco": "#FFFFFF",
    "texto": "#263238",
    "vermelho": "#C62828",
}


# Banco de dados
def conectar():
    return sqlite3.connect(BANCO)


def data_hora_atual():
    return datetime.now(FUSO_BRASILIA).strftime("%Y-%m-%d %H:%M:%S")


def criar_tabela():
    with conectar() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS pessoas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                telefone TEXT,
                data_cadastro TEXT
            )
        """)

        colunas = conexao.execute("PRAGMA table_info(pessoas)").fetchall()
        nomes_colunas = [coluna[1] for coluna in colunas]

        if "data_cadastro" not in nomes_colunas:
            conexao.execute("ALTER TABLE pessoas ADD COLUMN data_cadastro TEXT")

        conexao.execute(
            """
            UPDATE pessoas
            SET data_cadastro = ?
            WHERE data_cadastro IS NULL
            """,
            (data_hora_atual(),),
        )


# Validação
def email_valido(email):
    padrao = r"^[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}$"
    return re.fullmatch(padrao, email) is not None


def formatar_telefone(telefone):
    numeros = re.sub(r"\D", "", telefone)

    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    if len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    return None


def obter_dados_formulario():
    nome = entrada_nome.get().strip()
    email = entrada_email.get().strip().lower()
    telefone_digitado = entrada_telefone.get().strip()

    if not nome:
        messagebox.showwarning("Campo obrigatório", "Informe o nome do cliente.")
        entrada_nome.focus()
        return None

    if not email_valido(email):
        messagebox.showwarning("E-mail inválido", "Digite um e-mail válido.")
        entrada_email.focus()
        return None

    telefone = ""
    if telefone_digitado:
        telefone = formatar_telefone(telefone_digitado)
        if not telefone:
            messagebox.showwarning(
                "Telefone inválido",
                "Digite um telefone com DDD e 10 ou 11 números.",
            )
            entrada_telefone.focus()
            return None

    return nome, email, telefone


def aplicar_formato_telefone(evento=None):
    telefone = formatar_telefone(entrada_telefone.get())
    if telefone:
        entrada_telefone.delete(0, tk.END)
        entrada_telefone.insert(0, telefone)


# Funções do sistema
def limpar_campos():
    for campo in (entrada_nome, entrada_email, entrada_telefone):
        campo.delete(0, tk.END)
    tabela.selection_remove(*tabela.selection())
    entrada_nome.focus()


def preencher_tabela(registros):
    tabela.delete(*tabela.get_children())
    for registro in registros:
        tabela.insert("", tk.END, values=registro)


def listar():
    with conectar() as conexao:
        registros = conexao.execute("""
            SELECT id, nome, email, telefone,
                   strftime('%d/%m/%Y %H:%M', data_cadastro)
            FROM pessoas
            ORDER BY nome
        """).fetchall()
    preencher_tabela(registros)


def buscar(evento=None):
    texto = entrada_busca.get().strip()
    with conectar() as conexao:
        registros = conexao.execute(
            """
            SELECT id, nome, email, telefone,
                   strftime('%d/%m/%Y %H:%M', data_cadastro)
            FROM pessoas
            WHERE nome LIKE ? OR email LIKE ?
            ORDER BY nome
            """,
            (f"%{texto}%", f"%{texto}%"),
        ).fetchall()
    preencher_tabela(registros)


def cadastrar():
    dados = obter_dados_formulario()
    if not dados:
        return

    try:
        data_cadastro = data_hora_atual()
        with conectar() as conexao:
            conexao.execute(
                """
                INSERT INTO pessoas (nome, email, telefone, data_cadastro)
                VALUES (?, ?, ?, ?)
                """,
                (*dados, data_cadastro),
            )
    except sqlite3.IntegrityError:
        messagebox.showerror("E-mail já cadastrado", "Esse e-mail já está em uso.")
        entrada_email.focus()
        return

    messagebox.showinfo("Cadastro concluído", "Cliente cadastrado com sucesso.")
    limpar_campos()
    listar()


def preencher_campos(evento=None):
    selecionado = tabela.selection()
    if not selecionado:
        return

    valores = tabela.item(selecionado[0], "values")
    campos = (entrada_nome, entrada_email, entrada_telefone)
    for campo, valor in zip(campos, valores[1:4]):
        campo.delete(0, tk.END)
        campo.insert(0, valor)


def editar():
    selecionado = tabela.selection()
    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione um cliente para editar.")
        return

    dados = obter_dados_formulario()
    if not dados:
        return

    cliente_id = tabela.item(selecionado[0], "values")[0]
    try:
        with conectar() as conexao:
            conexao.execute(
                """
                UPDATE pessoas SET nome = ?, email = ?, telefone = ?
                WHERE id = ?
                """,
                (*dados, cliente_id),
            )
    except sqlite3.IntegrityError:
        messagebox.showerror("E-mail já cadastrado", "Esse e-mail já está em uso.")
        return

    messagebox.showinfo("Cadastro atualizado", "Dados atualizados com sucesso.")
    limpar_campos()
    listar()


def excluir():
    selecionado = tabela.selection()
    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione um cliente para excluir.")
        return

    valores = tabela.item(selecionado[0], "values")
    cliente_id, nome = valores[0], valores[1]
    if not messagebox.askyesno("Confirmar exclusão", f"Excluir o cadastro de {nome}?"):
        return

    with conectar() as conexao:
        conexao.execute("DELETE FROM pessoas WHERE id = ?", (cliente_id,))

    messagebox.showinfo("Cadastro excluído", "Cliente excluído com sucesso.")
    limpar_campos()
    listar()


# Aparência da interface
def configurar_estilos():
    estilo = ttk.Style()
    estilo.theme_use("clam")

    estilo.configure("Card.TFrame", background=CORES["branco"])
    estilo.configure(
        "Titulo.TLabel", background=CORES["branco"],
        foreground=CORES["principal_escura"], font=("Arial", 24, "bold")
    )
    estilo.configure(
        "Texto.TLabel", background=CORES["branco"],
        foreground=CORES["texto"], font=("Arial", 10)
    )
    estilo.configure("TEntry", padding=7, font=("Arial", 10))
    estilo.configure(
        "Principal.TButton", background=CORES["principal"],
        foreground=CORES["branco"], padding=(14, 8), font=("Arial", 10, "bold")
    )
    estilo.configure("Secundario.TButton", padding=(14, 8), font=("Arial", 10))
    estilo.configure(
        "Excluir.TButton", background=CORES["vermelho"],
        foreground=CORES["branco"], padding=(14, 8), font=("Arial", 10, "bold")
    )
    estilo.map("Principal.TButton", background=[("active", CORES["principal_escura"])])
    estilo.map("Excluir.TButton", background=[("active", "#8E0000")])
    estilo.configure(
        "Treeview", rowheight=30, background=CORES["branco"],
        fieldbackground=CORES["branco"], foreground=CORES["texto"], font=("Arial", 10)
    )
    estilo.configure(
        "Treeview.Heading", background=CORES["principal"],
        foreground=CORES["branco"], padding=8, font=("Arial", 10, "bold")
    )


def criar_campo(pai, texto, linha):
    ttk.Label(pai, text=texto, style="Texto.TLabel").grid(
        row=linha, column=0, sticky="w", padx=(0, 12), pady=7
    )
    campo = ttk.Entry(pai)
    campo.grid(row=linha, column=1, sticky="ew", pady=7)
    return campo


# Montagem da janela
criar_tabela()

janela = tk.Tk()
janela.title("Cadastro de Clientes")
janela.geometry("950x650")
janela.minsize(800, 550)
janela.configure(bg=CORES["fundo"])
configurar_estilos()

cabecalho = ttk.Frame(janela, style="Card.TFrame", padding=20)
cabecalho.pack(fill="x", padx=25, pady=(25, 10))
ttk.Label(cabecalho, text="Cadastro de Clientes", style="Titulo.TLabel").pack(anchor="w")
ttk.Label(
    cabecalho, text="Cadastre, consulte e organize seus clientes.",
    style="Texto.TLabel"
).pack(anchor="w", pady=(4, 0))

formulario = ttk.Frame(janela, style="Card.TFrame", padding=20)
formulario.pack(fill="x", padx=25, pady=10)
formulario.columnconfigure(1, weight=1)

entrada_nome = criar_campo(formulario, "Nome", 0)
entrada_email = criar_campo(formulario, "E-mail", 1)
entrada_telefone = criar_campo(formulario, "Telefone", 2)
entrada_telefone.bind("<FocusOut>", aplicar_formato_telefone)

area_botoes = ttk.Frame(formulario, style="Card.TFrame")
area_botoes.grid(row=3, column=0, columnspan=2, sticky="w", pady=(12, 0))

botoes = (
    ("Cadastrar", cadastrar, "Principal.TButton"),
    ("Editar", editar, "Secundario.TButton"),
    ("Limpar", limpar_campos, "Secundario.TButton"),
    ("Excluir", excluir, "Excluir.TButton"),
)
for coluna, (texto, comando, estilo) in enumerate(botoes):
    ttk.Button(area_botoes, text=texto, command=comando, style=estilo).grid(
        row=0, column=coluna, padx=(0, 8)
    )

area_busca = ttk.Frame(janela, style="Card.TFrame", padding=15)
area_busca.pack(fill="x", padx=25, pady=10)
ttk.Label(area_busca, text="Pesquisar", style="Texto.TLabel").pack(side="left")

entrada_busca = ttk.Entry(area_busca)
entrada_busca.pack(side="left", fill="x", expand=True, padx=12)
entrada_busca.bind("<Return>", buscar)

ttk.Button(area_busca, text="Buscar", command=buscar, style="Principal.TButton").pack(
    side="left", padx=4
)
ttk.Button(
    area_busca, text="Mostrar todos", command=listar, style="Secundario.TButton"
).pack(side="left", padx=4)

area_tabela = ttk.Frame(janela, style="Card.TFrame", padding=15)
area_tabela.pack(fill="both", expand=True, padx=25, pady=(10, 25))

colunas = ("id", "nome", "email", "telefone", "data_cadastro")
tabela = ttk.Treeview(area_tabela, columns=colunas, show="headings")

for coluna, titulo, largura in zip(
    colunas,
    ("ID", "Nome", "E-mail", "Telefone", "Cadastrado em"),
    (50, 180, 240, 140, 140),
):
    tabela.heading(coluna, text=titulo)
    tabela.column(coluna, width=largura, minwidth=50)

tabela.column("id", anchor="center", stretch=False)
tabela.bind("<<TreeviewSelect>>", preencher_campos)

barra_rolagem = ttk.Scrollbar(area_tabela, orient="vertical", command=tabela.yview)
tabela.configure(yscrollcommand=barra_rolagem.set)
tabela.pack(side="left", fill="both", expand=True)
barra_rolagem.pack(side="right", fill="y")

listar()
entrada_nome.focus()
janela.mainloop()
