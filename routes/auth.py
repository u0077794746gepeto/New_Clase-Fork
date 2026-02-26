import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from db import get_db_connection

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id_user, password, user_mail, rol FROM users WHERE user_name=%s",
            (username,)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            session["user_name"] = username
            session["user_mail"] = user[2]
            session["user_rol"] = user[3]

            # después de autenticarse, llevar al campus general
            return redirect(url_for("auth.campus"))

        flash("❌ Usuario o contraseña incorrectos")

    return render_template("index.html")


@auth_bp.route("/register", methods=["GET", "POST"])
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
            return redirect(url_for("auth.index"))
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash("⚠️ Usuario y correo ya existen.")
        finally:
            cur.close()
            conn.close()

    return render_template("register.html")


@auth_bp.route("/campus")
def campus():
    # cualquier usuario debe estar autenticado para llegar aquí
    if "user_id" not in session:
        return redirect(url_for("auth.index"))

    # redirige a admin al panel de administración
    role = session.get("user_rol", "").lower()
    if role in ("admin", "administrador"):
        return redirect(url_for("admin.perfil_admin"))

    # para otros roles, muestra la página de bienvenida
    return render_template("campus.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.index"))


@auth_bp.app_context_processor

def inject_api_key():
    return dict(api_key=os.getenv("OPENWEATHER_API_KEY"))
