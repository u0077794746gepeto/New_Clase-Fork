from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2
import os
from db import get_db_connection
from decorators import login_required, role_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/app-admin", methods=("GET", "POST"))
def perfil_admin():
    # si ya está autenticado como administrador, mostrar el panel
    if "user_id" in session and session.get("user_rol", "").lower() in ("admin", "administrador"):
        if request.method == "POST":
            return redirect(url_for("admin.perfil_admin"))
        return render_template("perfil_admin.html")

    # en caso contrario, procesar login
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

                return redirect(url_for("auth.campus"))
            else:
                flash("⚠️ No tiene permisos de administrador.")
                return redirect(url_for("auth.index"))

        flash("❌ Usuario o contraseña incorrectos.")
        return redirect(url_for("admin.perfil_admin"))

    return render_template("admin.html")


@admin_bp.route("/mod-usuarios")
@role_required("admin", "administrador")
def mod_usuarios():
    return render_template("mod_usuarios.html")


@admin_bp.route("/buscar-usuarios", methods=["POST"])
@role_required("admin", "administrador")
def buscar_usuarios():
    search = request.get_json().get("search", "").strip()

    if not search:
        return {"usuarios": []}

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT id_user, user_name, user_mail, rol, creado_en 
            FROM users 
            WHERE user_name ILIKE %s 
               OR user_mail ILIKE %s 
               OR DATE(creado_en)::text LIKE %s
            LIMIT 100
        """, (f"%{search}%", f"%{search}%", f"%{search}%"))

        usuarios = cur.fetchall()
        resultado = []

        for user in usuarios:
            resultado.append({
                "id_user": user[0],
                "user_name": user[1],
                "user_mail": user[2],
                "rol": user[3],
                "creado_en": str(user[4])
            })

        cur.close()
        conn.close()

        return {"usuarios": resultado}

    except Exception as e:
        print(f"Error en búsqueda: {e}")
        return {"success": False, "message": "Error en la búsqueda"}, 500


@admin_bp.route("/crear-usuario", methods=["POST"])
@role_required("admin", "administrador")
def crear_usuario():
    data = request.get_json()
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    rol = data.get("rol", "").strip()

    # Validaciones
    if not all([username, email, password, rol]):
        return {"success": False, "message": "Todos los campos son obligatorios"}

    if rol not in ["Profesor", "Alumno", "Oficina"]:
        return {"success": False, "message": "Rol inválido"}

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        hashed_password = generate_password_hash(password)

        cur.execute("""
            INSERT INTO users (user_name, password, user_mail, creado_en, actualizado_en, rol) 
            VALUES (%s, %s, %s, NOW(), NOW(), %s)
        """, (username, hashed_password, email, rol))

        conn.commit()
        cur.close()
        conn.close()

        return {"success": True, "message": "Usuario creado correctamente"}

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        cur.close()
        conn.close()
        return {"success": False, "message": "El usuario o email ya existe"}

    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        print(f"Error al crear usuario: {e}")
        return {"success": False, "message": "Error al crear el usuario"}


@admin_bp.app_context_processor
def inject_api_key():
    return dict(api_key=os.getenv("OPENWEATHER_API_KEY"))
