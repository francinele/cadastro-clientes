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
    email = input("E-mail: ").strip()
    telefone = input("Telefone: ").strip()

    if not nome or not email:
        print("Nome e e-mail são obrigatórios.")
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
        print("Já existe um cadastro com esse e-mail.")

    finally:
        conexao.close()


def listar():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, email, telefone
        FROM pessoas
        ORDER BY nome
    """)

    pessoas = cursor.fetchall()
    conexao.close()

    print("\n--- Pessoas cadastradas ---")

    if not pessoas:
        print("Nenhum cadastro encontrado.")
        return []

    for pessoa in pessoas:
        print(f"\nID: {pessoa[0]}")
        print(f"Nome: {pessoa[1]}")
        print(f"E-mail: {pessoa[2]}")
        print(f"Telefone: {pessoa[3] or 'Não informado'}")

    return pessoas


def buscar():
    nome = input("\nDigite o nome que deseja buscar: ").strip()

    if not nome:
        print("Digite um nome para realizar a busca.")
        return

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT id, nome, email, telefone
        FROM pessoas
        WHERE nome LIKE ?
        ORDER BY nome
        """,
        (f"%{nome}%",)
    )

    pessoas = cursor.fetchall()
    conexao.close()

    if not pessoas:
        print("Nenhum cadastro encontrado.")
        return

    print("\n--- Resultado da busca ---")

    for pessoa in pessoas:
        print(f"\nID: {pessoa[0]}")
        print(f"Nome: {pessoa[1]}")
        print(f"E-mail: {pessoa[2]}")
        print(f"Telefone: {pessoa[3] or 'Não informado'}")


def editar():
    pessoas = listar()

    if not pessoas:
        return

    try:
        pessoa_id = int(
            input("\nDigite o ID do cadastro que deseja editar: ")
        )
    except ValueError:
        print("Digite somente números.")
        return

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT id, nome, email, telefone
        FROM pessoas
        WHERE id = ?
        """,
        (pessoa_id,)
    )

    pessoa = cursor.fetchone()

    if not pessoa:
        print("Cadastro não encontrado.")
        conexao.close()
        return

    print("\nPressione Enter para manter a informação atual.")

    novo_nome = input(f"Nome [{pessoa[1]}]: ").strip()
    novo_email = input(f"E-mail [{pessoa[2]}]: ").strip()
    novo_telefone = input(
        f"Telefone [{pessoa[3] or 'Não informado'}]: "
    ).strip()

    nome = novo_nome if novo_nome else pessoa[1]
    email = novo_email if novo_email else pessoa[2]
    telefone = novo_telefone if novo_telefone else pessoa[3]

    try:
        cursor.execute(
            """
            UPDATE pessoas
            SET nome = ?, email = ?, telefone = ?
            WHERE id = ?
            """,
            (nome, email, telefone, pessoa_id)
        )

        conexao.commit()
        print("Cadastro atualizado com sucesso!")

    except sqlite3.IntegrityError:
        print("Esse e-mail já está sendo usado por outro cadastro.")

    finally:
        conexao.close()


def excluir():
    pessoas = listar()

    if not pessoas:
        return

    try:
        pessoa_id = int(
            input("\nDigite o ID do cadastro que deseja excluir: ")
        )
    except ValueError:
        print("Digite somente números.")
        return

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT nome FROM pessoas WHERE id = ?",
        (pessoa_id,)
    )

    pessoa = cursor.fetchone()

    if not pessoa:
        print("Cadastro não encontrado.")
        conexao.close()
        return

    confirmacao = input(
        f"Deseja realmente excluir {pessoa[0]}? (s/n): "
    ).strip().lower()

    if confirmacao == "s":
        cursor.execute(
            "DELETE FROM pessoas WHERE id = ?",
            (pessoa_id,)
        )

        conexao.commit()
        print("Cadastro excluído com sucesso!")
    else:
        print("Exclusão cancelada.")

    conexao.close()


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