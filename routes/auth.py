import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor
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
            # inserta el usuario y recupera su id para crear el evento de bienvenida
            cur.execute(
                "INSERT INTO users (user_name, password, user_mail, creado_en, actualizado_en, rol) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id_user",
                (username, password, email, creado_en, actualizado_en, rol_defecto)
            )
            new_id = cur.fetchone()[0]

            # evento de bienvenida personal (no es 'external')
            cur.execute(
                "INSERT INTO events (user_id, title, description, start_date, end_date, external) "
                "VALUES (%s,%s,%s,NOW(),NOW(),FALSE)",
                (new_id, "Bienvenido al campus", "¡Gracias por registrarte! Esperamos que disfrutes de tu agenda personal.")
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


@auth_bp.route("/campus", methods=["GET", "POST"])
def campus():
    # cualquier usuario debe estar autenticado para llegar aquí
    if "user_id" not in session:
        return redirect(url_for("auth.index"))

    # redirige a admin al panel de administración
    role = session.get("user_rol", "").lower()
    if role in ("admin", "administrador"):
        return redirect(url_for("admin.perfil_admin"))

    # si es POST, actualizamos los datos del usuario
    if request.method == "POST":
        new_name = request.form.get("username")
        new_mail = request.form.get("email")
        new_password = request.form.get("password", "").strip()
        
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # si la contraseña fue proporcionada, la encriptamos y actualizamos
            if new_password:
                hashed_password = generate_password_hash(new_password)
                cur.execute(
                    "UPDATE users SET user_name=%s, user_mail=%s, password=%s, actualizado_en=NOW() WHERE id_user=%s",
                    (new_name, new_mail, hashed_password, session["user_id"])
                )
            else:
                # si no hay contraseña, solo actualizamos nombre y email
                cur.execute(
                    "UPDATE users SET user_name=%s, user_mail=%s, actualizado_en=NOW() WHERE id_user=%s",
                    (new_name, new_mail, session["user_id"])
                )
            conn.commit()
            # actualizar sesión para reflejar cambios
            session["user_name"] = new_name
            session["user_mail"] = new_mail
            flash("✅ Perfil actualizado.")
        except Exception:
            conn.rollback()
            flash("⚠️ No se pudo actualizar el perfil.")
        finally:
            cur.close()
            conn.close()

    # --- LÓGICA PARA CARGAR ANUNCIOS EN LA FICHA ---
    anuncios_lista = []
    conn_anuncios = get_db_connection()
    cur_anuncios = conn_anuncios.cursor(cursor_factory=RealDictCursor)
    try:
        cur_anuncios.execute(
            "SELECT titulo, mensaje, prioridad, fecha_publicacion FROM anuncios ORDER BY fecha_publicacion DESC LIMIT 5"
        )
        anuncios_lista = cur_anuncios.fetchall()
    except Exception as e:
        print(f"Error al cargar anuncios: {e}")
    finally:
        cur_anuncios.close()
        conn_anuncios.close()
    # -----------------------------------------------

    # para otros roles, muestra la página de bienvenida / ficha con calendario y anuncios
    return render_template("campus.html", anuncios=anuncios_lista)


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.index"))


# --------------------- API de eventos -----------------------------
@auth_bp.route("/campus/events", methods=["GET", "POST"])
def user_events():
    """Devuelve o crea eventos del usuario autenticado."""
    if "user_id" not in session:
        return jsonify({"error": "no autorizado"}), 401
    user_id = session["user_id"]

    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == "GET":
        cur.execute(
            "SELECT id_event, title, description, start_date, end_date, external, source "
            "FROM events WHERE user_id=%s",
            (user_id,)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        events = []
        for r in rows:
            events.append({
                "id": r[0],
                "title": r[1],
                "description": r[2],
                "start": r[3].isoformat(),
                "end": r[4].isoformat(),
                "external": r[5],
                "source": r[6]
            })
        return jsonify(events)
    else:
        data = request.get_json()
        title = data.get("title")
        desc = data.get("description", "")
        start = data.get("start")
        end = data.get("end", start)
        cur.execute(
            "INSERT INTO events (user_id, title, description, start_date, end_date, external) "
            "VALUES (%s,%s,%s,%s,%s,FALSE) RETURNING id_event",
            (user_id, title, desc, start, end)
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"id": new_id}), 201


@auth_bp.route("/campus/events/<int:event_id>", methods=["PUT", "DELETE"])
def modify_event(event_id):
    if "user_id" not in session:
        return jsonify({"error": "no autorizado"}), 401
    user_id = session["user_id"]
    conn = get_db_connection()
    cur = conn.cursor()

    # verificar que el evento pertenece al usuario
    cur.execute("SELECT user_id FROM events WHERE id_event=%s", (event_id,))
    row = cur.fetchone()
    if not row or row[0] != user_id:
        cur.close()
        conn.close()
        return jsonify({"error": "evento no encontrado"}), 404

    if request.method == "PUT":
        data = request.get_json()
        title = data.get("title")
        desc = data.get("description", "")
        start = data.get("start")
        end = data.get("end", start)
        cur.execute(
            "UPDATE events SET title=%s, description=%s, start_date=%s, end_date=%s, actualizado_en=NOW() "
            "WHERE id_event=%s",
            (title, desc, start, end, event_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "ok"})
    else:  # DELETE
        cur.execute("DELETE FROM events WHERE id_event=%s", (event_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "ok"})


@auth_bp.app_context_processor
def inject_api_key():
    return dict(api_key=os.getenv("OPENWEATHER_API_KEY"))