from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
import os
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from functools import wraps

# Cargar variables de entorno desde archivo .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# def get_db_connection():
#     return psycopg2.connect(
#         dbname=os.getenv("POSTGRES_DB"),
#         user=os.getenv("POSTGRES_USER"),
#         password=os.getenv("POSTGRES_PASSWORD"),
#         host=os.getenv("PGHOST"),
#         port=os.getenv("PGPORT")
#     )

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

# ---------------- HOME / LOGIN -----------------

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id_user, password, user_mail FROM users WHERE user_name=%s",
            (username,)
        )

        user = cur.fetchone()

        cur.close()
        conn.close()

        if user and check_password_hash(user[1], password):

            session["user_id"] = user[0]
            session["user_name"] = username
            session["user_mail"] = user[2]

            return redirect(url_for("campus"))

        flash("❌ Usuario o contraseña incorrectos")

    return render_template("index.html")


# ---------------- REGISTER -----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        creado_en = "NOW()"
        actualizado_en = "NOW()"
        rol_defecto = "Alumno"



        conn = get_db_connection()
        cur = conn.cursor()

        try:

            cur.execute(
                "INSERT INTO users (user_name, password, user_mail, creado_en, actualizado_en, rol) VALUES (%s,%s,%s,%s,%s,%s)",
                (username, password, email, creado_en, actualizado_en, rol_defecto)
            )

            conn.commit()
            flash("✅ Registro correcto. Inicia sesión.")

            return redirect(url_for("index"))

        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash("⚠️ Usuario y correo ya existen.")

        finally:
            cur.close()
            conn.close()

    return render_template("register.html")


# ---------------- CAMPUS -----------------

@app.route("/campus")
def campus():

    if "user_id" not in session:
        return redirect(url_for("index"))

    return render_template("campus.html")


# ---------------- LOGOUT -----------------

@app.route("/logout")
def logout():

    session.clear()
    return redirect(url_for("index"))


@app.context_processor
def inject_api_key():
    return dict(api_key=os.getenv("OPENWEATHER_API_KEY"))

#Creamos la URL para el administrador
@app.route("/app-admin", methods=("GET", "POST"))
def perfil_admin():
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id_user, password, rol, user_mail FROM users WHERE user_name=%s",
            (username,)
        )

        user = cur.fetchone()

        cur.close()
        conn.close()

        if user and check_password_hash(user[1], password):
            role = user[2] or ""
            if role.lower() in ("admin", "administrador"):
                session["user_id"] = user[0]
                session["user_name"] = username
                session["user_mail"] = user[3]
                session["user_rol"] = role

                return render_template("base_admin.html")
            else:
                flash("⚠️ No tiene permisos de administrador.")
                return redirect(url_for("index"))

        flash("❌ Usuario o contraseña incorrectos.")
        return redirect(url_for("perfil_admin"))

    return render_template("admin.html")


if __name__ == "__main__":
    app.run(debug=True)



