import sqlite3

BANCO = "cadastros.db"


def conectar():
    return sqlite3.connect(BANCO)


def criar_tabela():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pessoas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            telefone TEXT
        )
    """)

    conexao.commit()
    conexao.close()


def cadastrar():
    print("\n--- Novo cadastro ---")

    nome = input("Nome: ").strip()
    email = input("E-mail: ").strip().lower()
    telefone = input("Telefone: ").strip()

    if not nome or not email:
        print("Nome e e-mail são obrigatórios.")
        return

    if "@" not in email or "." not in email:
        print("Digite um e-mail válido.")
        return

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO pessoas (nome, email, telefone)
            VALUES (?, ?, ?)
            """,
            (nome, email, telefone)
        )

        conexao.commit()
        print("Cadastro realizado com sucesso!")

    except sqlite3.IntegrityError:
        print("Já existe uma pessoa cadastrada com esse e-mail.")

    finally:
        conexao.close()


def obter_cadastros():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, email, telefone
        FROM pessoas
        ORDER BY nome
    """)

    pessoas = cursor.fetchall()
    conexao.close()

    return pessoas


def listar():
    print("\n--- Pessoas cadastradas ---")

    pessoas = obter_cadastros()

    if not pessoas:
        print("Nenhum cadastro encontrado.")
        return False

    for pessoa in pessoas:
        id_pessoa, nome, email, telefone = pessoa

        print(f"\nCódigo: {id_pessoa}")
        print(f"Nome: {nome}")
        print(f"E-mail: {email}")
        print(f"Telefone: {telefone or 'Não informado'}")

    return True


def buscar():
    termo = input("\nDigite o nome ou e-mail que deseja buscar: ")
    termo = termo.strip()

    if not termo:
        print("Digite alguma informação para realizar a busca.")
        return

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT id, nome, email, telefone
        FROM pessoas
        WHERE nome LIKE ? OR email LIKE ?
        ORDER BY nome
        """,
        (f"%{termo}%", f"%{termo}%")
    )

    pessoas = cursor.fetchall()
    conexao.close()

    if not pessoas:
        print("Nenhum cadastro encontrado.")
        return

    print("\n--- Resultado da busca ---")

    for pessoa in pessoas:
        id_pessoa, nome, email, telefone = pessoa

        print(f"\nCódigo: {id_pessoa}")
        print(f"Nome: {nome}")
        print(f"E-mail: {email}")
        print(f"Telefone: {telefone or 'Não informado'}")


def editar():
    if not listar():
        return

    try:
        id_pessoa = int(
            input("\nDigite o código do cadastro que deseja editar: ")
        )
    except ValueError:
        print("Digite um código válido.")
        return

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT nome, email, telefone
        FROM pessoas
        WHERE id = ?
        """,
        (id_pessoa,)
    )

    pessoa = cursor.fetchone()

    if pessoa is None:
        print("Cadastro não encontrado.")
        conexao.close()
        return

    nome_atual, email_atual, telefone_atual = pessoa

    print("\nPressione Enter para manter a informação atual.")

    novo_nome = input(f"Nome [{nome_atual}]: ").strip()
    novo_email = input(f"E-mail [{email_atual}]: ").strip().lower()
    novo_telefone = input(
        f"Telefone [{telefone_atual or 'Não informado'}]: "
    ).strip()

    nome = novo_nome or nome_atual
    email = novo_email or email_atual
    telefone = novo_telefone or telefone_atual

    if "@" not in email or "." not in email:
        print("Digite um e-mail válido.")
        conexao.close()
        return

    try:
        cursor.execute(
            """
            UPDATE pessoas
            SET nome = ?, email = ?, telefone = ?
            WHERE id = ?
            """,
            (nome, email, telefone, id_pessoa)
        )

        conexao.commit()
        print("Cadastro atualizado com sucesso!")

    except sqlite3.IntegrityError:
        print("Esse e-mail já pertence a outro cadastro.")

    finally:
        conexao.close()


def excluir():
    if not listar():
        return

    try:
        id_pessoa = int(
            input("\nDigite o código do cadastro que deseja excluir: ")
        )
    except ValueError:
        print("Digite um código válido.")
        return

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT nome FROM pessoas WHERE id = ?",
        (id_pessoa,)
    )

    pessoa = cursor.fetchone()

    if pessoa is None:
        print("Cadastro não encontrado.")
        conexao.close()
        return

    nome = pessoa[0]

    confirmacao = input(
        f"Tem certeza que deseja excluir {nome}? (s/n): "
    ).strip().lower()

    if confirmacao != "s":
        print("Exclusão cancelada.")
        conexao.close()
        return

    cursor.execute(
        "DELETE FROM pessoas WHERE id = ?",
        (id_pessoa,)
    )

    conexao.commit()
    conexao.close()

    print("Cadastro excluído com sucesso!")


def exibir_menu():
    print("\n==========================")
    print("   SISTEMA DE CADASTRO")
    print("==========================")
    print("1 - Cadastrar pessoa")
    print("2 - Listar cadastros")
    print("3 - Buscar pessoa")
    print("4 - Editar cadastro")
    print("5 - Excluir cadastro")
    print("6 - Sair")


def executar():
    criar_tabela()

    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            cadastrar()

        elif opcao == "2":
            listar()

        elif opcao == "3":
            buscar()

        elif opcao == "4":
            editar()

        elif opcao == "5":
            excluir()

        elif opcao == "6":
            print("Programa encerrado.")
            break

        else:
            print("Opção inválida. Escolha uma opção de 1 a 6.")


if __name__ == "__main__":
    executar()