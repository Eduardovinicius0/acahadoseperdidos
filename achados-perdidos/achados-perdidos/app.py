from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = "banco.db"


def conectar_banco():
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_banco():
    conexao = conectar_banco()
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            nome TEXT NOT NULL,
            descricao TEXT NOT NULL,
            local TEXT NOT NULL,
            contato TEXT NOT NULL,
            resolvido INTEGER DEFAULT 0
        )
    """)
    conexao.commit()
    conexao.close()


@app.route("/")
def index():
    filtro = request.args.get("filtro", "todos")
    conexao = conectar_banco()

    if filtro == "perdidos":
        itens = conexao.execute(
            "SELECT * FROM itens WHERE tipo = 'Perdido' ORDER BY id DESC"
        ).fetchall()
    elif filtro == "encontrados":
        itens = conexao.execute(
            "SELECT * FROM itens WHERE tipo = 'Encontrado' ORDER BY id DESC"
        ).fetchall()
    else:
        itens = conexao.execute(
            "SELECT * FROM itens ORDER BY id DESC"
        ).fetchall()

    conexao.close()
    return render_template("index.html", itens=itens, filtro=filtro)


@app.route("/adicionar", methods=["POST"])
def adicionar():
    tipo = request.form["tipo"]
    nome = request.form["nome"]
    descricao = request.form["descricao"]
    local = request.form["local"]
    contato = request.form["contato"]

    conexao = conectar_banco()
    conexao.execute("""
        INSERT INTO itens (tipo, nome, descricao, local, contato)
        VALUES (?, ?, ?, ?, ?)
    """, (tipo, nome, descricao, local, contato))
    conexao.commit()
    conexao.close()

    return redirect(url_for("index"))


@app.route("/resolver/<int:id>", methods=["POST"])
def resolver(id):
    conexao = conectar_banco()
    conexao.execute(
        "UPDATE itens SET resolvido = 1 WHERE id = ?",
        (id,)
    )
    conexao.commit()
    conexao.close()
    return redirect(url_for("index"))


@app.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    conexao = conectar_banco()
    conexao.execute(
        "DELETE FROM itens WHERE id = ?",
        (id,)
    )
    conexao.commit()
    conexao.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)
