
import os
import sqlite3
import secrets

from pathlib import Path
from datetime import datetime
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for, abort
from werkzeug.security import check_password_hash, generate_password_hash


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "alterar-esta-chave")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

DB_PATH = Path(__file__).resolve().parent / "voluntariado360.db"


# Ligar à base de dados
def db():
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


# Consultar dados
def query(sql, args=(), one=False):
    con = db()

    try:
        cur = con.execute(sql, args)

        if one:
            row = cur.fetchone()
            return dict(row) if row else None

        return [dict(row) for row in cur.fetchall()]

    finally:
        con.close()


# Guardar alterações
def execute(sql, args=()):
    con = db()

    try:
        cur = con.execute(sql, args)
        con.commit()
        return cur.lastrowid

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


# Criar as tabelas se ainda não existirem
def criar_base_dados():
    con = db()

    try:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS utilizadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                telefone TEXT,
                password_hash TEXT NOT NULL,
                perfil TEXT NOT NULL DEFAULT 'voluntario',
                ativo INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS sessoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                data_sessao TEXT NOT NULL,
                hora_inicio TEXT NOT NULL,
                hora_fim TEXT NOT NULL,
                vagas INTEGER NOT NULL CHECK(vagas > 0),
                estado TEXT NOT NULL DEFAULT 'ativa'
            );

            CREATE TABLE IF NOT EXISTS inscricoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                utilizador_id INTEGER NOT NULL,
                sessao_id INTEGER NOT NULL,
                estado TEXT NOT NULL DEFAULT 'ativa',
                UNIQUE(utilizador_id, sessao_id),
                FOREIGN KEY(utilizador_id) REFERENCES utilizadores(id),
                FOREIGN KEY(sessao_id) REFERENCES sessoes(id)
            );

            CREATE TABLE IF NOT EXISTS presencas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inscricao_id INTEGER NOT NULL UNIQUE,
                presente INTEGER NOT NULL,
                FOREIGN KEY(inscricao_id) REFERENCES inscricoes(id)
            );
        """)

        con.commit()

    finally:
        con.close()


# Verificar se o utilizador iniciou sessão
def login_required(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        if not session.get("uid"):
            flash("Inicie sessão para continuar.", "error")
            return redirect(url_for("login"))

        return fn(*args, **kwargs)

    return inner


# Restringir o acesso à associação
def admin_required(fn):
    @wraps(fn)
    @login_required
    def inner(*args, **kwargs):
        if session.get("perfil") != "admin":
            flash("Acesso reservado à associação.", "error")
            return redirect(url_for("index"))

        return fn(*args, **kwargs)

    return inner


# Proteger os formulários
def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(24)

    return session["csrf"]


@app.context_processor
def inject():
    return {"csrf_token": csrf_token}


@app.before_request
def check_csrf():
    if request.method == "POST":
        recebido = request.form.get("csrf_token", "")
        esperado = session.get("csrf", "")

        if not esperado or not secrets.compare_digest(recebido, esperado):
            abort(400, "Formulário expirado. Atualize a página.")


# Página inicial
@app.route("/")
def index():
    return render_template("index.html")


# Iniciar sessão
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = query(
            "SELECT * FROM utilizadores WHERE email=? AND ativo=1",
            (email,),
            one=True
        )

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["uid"] = user["id"]
            session["nome"] = user["nome"]
            session["perfil"] = user["perfil"]

            csrf_token()

            flash("Bem-vindo ao Voluntariado 360!", "success")
            return redirect(url_for("sessoes"))

        flash("Email ou palavra-passe inválidos.", "error")

    return render_template("login.html")


# Terminar sessão
@app.post("/logout")
@login_required
def logout():
    session.clear()
    flash("Sessão terminada.", "success")
    return redirect(url_for("index"))


# Mostrar sessões disponíveis
@app.route("/sessoes")
@login_required
def sessoes():
    rows = query("""
        SELECT s.*, COUNT(i.id) AS inscritos,
        EXISTS(
            SELECT 1 FROM inscricoes x
            WHERE x.sessao_id=s.id
            AND x.utilizador_id=?
            AND x.estado='ativa'
        ) AS minha_inscricao
        FROM sessoes s
        LEFT JOIN inscricoes i ON i.sessao_id=s.id AND i.estado='ativa'
        WHERE s.estado='ativa'
        AND s.data_sessao >= date('now', 'localtime')
        GROUP BY s.id
        ORDER BY s.data_sessao, s.hora_inicio
    """, (session["uid"],))

    return render_template("sessoes.html", sessoes=rows)


# Inscrever o voluntário numa sessão
@app.post("/inscrever/<int:sessao_id>")
@login_required
def inscrever(sessao_id):
    if session["perfil"] == "admin":
        flash("Utilize uma conta de voluntário.", "error")
        return redirect(url_for("sessoes"))

    con = db()

    try:
        # Evitar inscrições acima do número de vagas
        con.execute("BEGIN IMMEDIATE")

        row = con.execute(
            "SELECT * FROM sessoes WHERE id=?",
            (sessao_id,)
        ).fetchone()

        s = dict(row) if row else None
        hoje = datetime.now().date().isoformat()

        if not s or s["estado"] != "ativa" or s["data_sessao"] < hoje:
            flash("Esta sessão não está disponível.", "error")

        else:
            total = con.execute(
                "SELECT COUNT(*) AS total FROM inscricoes WHERE sessao_id=? AND estado='ativa'",
                (sessao_id,)
            ).fetchone()["total"]

            row = con.execute(
                "SELECT id, estado FROM inscricoes WHERE sessao_id=? AND utilizador_id=?",
                (sessao_id, session["uid"])
            ).fetchone()

            existing = dict(row) if row else None

            if existing and existing["estado"] == "ativa":
                flash("Já está inscrito nesta sessão.", "error")

            elif total >= s["vagas"]:
                flash("Esta sessão já não tem vagas.", "error")

            elif existing:
                con.execute(
                    "UPDATE inscricoes SET estado='ativa' WHERE id=?",
                    (existing["id"],)
                )

                flash("Inscrição reativada.", "success")

            else:
                con.execute(
                    "INSERT INTO inscricoes (utilizador_id, sessao_id) VALUES (?, ?)",
                    (session["uid"], sessao_id)
                )

                flash("Inscrição realizada com sucesso!", "success")

        con.commit()

    except sqlite3.Error:
        con.rollback()
        flash("Não foi possível guardar a inscrição.", "error")

    finally:
        con.close()

    return redirect(url_for("sessoes"))


# Mostrar inscrições do voluntário
@app.route("/minhas-inscricoes")
@login_required
def minhas_inscricoes():
    rows = query("""
        SELECT i.id, i.estado, s.titulo, s.data_sessao, s.hora_inicio, s.hora_fim
        FROM inscricoes i
        JOIN sessoes s ON s.id=i.sessao_id
        WHERE i.utilizador_id=?
        ORDER BY s.data_sessao DESC
    """, (session["uid"],))

    return render_template(
        "minhas.html",
        inscricoes=rows,
        today=datetime.now().date().isoformat()
    )


# Cancelar uma inscrição
@app.post("/cancelar/<int:inscricao_id>")
@login_required
def cancelar(inscricao_id):
    row = query("""
        SELECT i.id FROM inscricoes i
        JOIN sessoes s ON s.id=i.sessao_id
        WHERE i.id=? AND i.utilizador_id=?
        AND i.estado='ativa'
        AND s.data_sessao >= date('now', 'localtime')
    """, (inscricao_id, session["uid"]), one=True)

    if not row:
        flash("Não é possível cancelar esta inscrição.", "error")

    else:
        execute(
            "UPDATE inscricoes SET estado='cancelada' WHERE id=?",
            (inscricao_id,)
        )

        flash("Inscrição cancelada.", "success")

    return redirect(url_for("minhas_inscricoes"))


# Área de gestão da associação
@app.route("/admin")
@admin_required
def admin():
    volunteers = query("""
        SELECT id, nome, email, telefone, ativo
        FROM utilizadores
        WHERE perfil='voluntario'
        ORDER BY id DESC
    """)

    sessions = query(
        "SELECT * FROM sessoes ORDER BY data_sessao DESC"
    )

    attendance = query("""
        SELECT i.id AS inscricao_id, u.nome, s.titulo, s.data_sessao, p.presente
        FROM inscricoes i
        JOIN utilizadores u ON u.id=i.utilizador_id
        JOIN sessoes s ON s.id=i.sessao_id
        LEFT JOIN presencas p ON p.inscricao_id=i.id
        WHERE i.estado='ativa'
        ORDER BY s.data_sessao DESC, u.nome
    """)

    return render_template(
        "admin.html",
        volunteers=volunteers,
        sessoes=sessions,
        attendance=attendance
    )


# Registar voluntário após verificação presencial
@app.post("/admin/voluntario")
@admin_required
def novo_voluntario():
    nome = request.form.get("nome", "").strip()
    email = request.form.get("email", "").strip().lower()
    telefone = request.form.get("telefone", "").strip()
    password = request.form.get("password", "")
    verified = request.form.get("verificado") == "sim"

    if not nome or "@" not in email or len(password) < 8 or not verified:
        flash("Preencha os dados e confirme a verificação presencial.", "error")

    else:
        try:
            execute("""
                INSERT INTO utilizadores (nome, email, telefone, password_hash)
                VALUES (?, ?, ?, ?)
            """, (nome, email, telefone, generate_password_hash(password)))

            flash("Voluntário registado com sucesso!", "success")

        except sqlite3.IntegrityError:
            flash("Este email já está registado.", "error")

    return redirect(url_for("admin"))


# Alterar a palavra-passe de um voluntário
@app.post("/admin/password/<int:voluntario_id>")
@admin_required
def alterar_password(voluntario_id):
    nova_password = request.form.get("nova_password", "")

    if len(nova_password) < 8:
        flash("A palavra-passe deve ter pelo menos 8 caracteres.", "error")
        return redirect(url_for("admin"))

    voluntario = query(
        "SELECT id FROM utilizadores WHERE id=? AND perfil='voluntario'",
        (voluntario_id,),
        one=True
    )

    if not voluntario:
        flash("Voluntário não encontrado.", "error")

    else:
        execute(
            "UPDATE utilizadores SET password_hash=? WHERE id=?",
            (generate_password_hash(nova_password), voluntario_id)
        )

        flash("Palavra-passe alterada com sucesso.", "success")

    return redirect(url_for("admin"))


# Criar uma sessão de voluntariado
@app.post("/admin/sessao")
@admin_required
def nova_sessao():
    titulo = request.form.get("titulo", "").strip()
    data = request.form.get("data", "")
    inicio = request.form.get("inicio", "")
    fim = request.form.get("fim", "")

    try:
        vagas = int(request.form.get("vagas", "0"))
        data_obj = datetime.strptime(data, "%Y-%m-%d").date()

        if not titulo or not inicio or not fim or inicio >= fim or vagas < 1:
            raise ValueError()

        if data_obj < datetime.now().date():
            raise ValueError()

        execute("""
            INSERT INTO sessoes (titulo, data_sessao, hora_inicio, hora_fim, vagas)
            VALUES (?, ?, ?, ?, ?)
        """, (titulo, data, inicio, fim, vagas))

        flash("Sessão criada com sucesso.", "success")

    except (ValueError, sqlite3.Error):
        flash("Dados da sessão inválidos.", "error")

    return redirect(url_for("admin"))




# Cancelar uma sessão
@app.post("/admin/sessao/<int:sessao_id>/cancelar")
@admin_required
def cancelar_sessao(sessao_id):
    execute(
        "UPDATE sessoes SET estado='cancelada' WHERE id=?",
        (sessao_id,)
    )

    flash("Sessão cancelada.", "success")
    return redirect(url_for("admin"))

# Registar presença ou falta
@app.post("/admin/presenca/<int:inscricao_id>")
@admin_required
def registar_presenca(inscricao_id):
    estado = request.form.get("presente")

    if estado not in ("0", "1"):
        flash("Escolha Presente ou Falta.", "error")
        return redirect(url_for("admin"))

    record = query(
        "SELECT id FROM inscricoes WHERE id=? AND estado='ativa'",
        (inscricao_id,),
        one=True
    )

    if not record:
        flash("Inscrição inválida.", "error")

    else:
        execute("""
            INSERT INTO presencas (inscricao_id, presente)
            VALUES (?, ?)
            ON CONFLICT(inscricao_id)
            DO UPDATE SET presente=excluded.presente
        """, (inscricao_id, int(estado)))

        flash("Presença registada.", "success")

    return redirect(url_for("admin"))





# Criar a conta da associação pelo terminal
@app.cli.command("criar-admin")
def criar_admin():
    email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    password = os.getenv("ADMIN_PASSWORD", "")

    if not email or len(password) < 8:
        print("Defina ADMIN_EMAIL e ADMIN_PASSWORD no ficheiro .env.")
        return

    try:
        execute("""
            INSERT INTO utilizadores (nome, email, password_hash, perfil)
            VALUES (?, ?, ?, 'admin')
        """, ("Administração", email, generate_password_hash(password)))

        print("Conta administrativa criada!")

    except sqlite3.IntegrityError:
        print("Já existe uma conta com este email.")


criar_base_dados()

if __name__ == "__main__":
    app.run(debug=True)
