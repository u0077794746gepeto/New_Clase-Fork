from flask import Flask
import os
from dotenv import load_dotenv

# cargar variables de entorno al iniciar la aplicación
load_dotenv()


<<<<<<< HEAD
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
            "SELECT id_user, password, user_email FROM users WHERE user_name=%s",
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
    # Si ya está autenticado como administrador, mostrar el panel
    if "user_id" in session and session.get("user_rol", "").lower() in ("admin", "administrador"):
        if request.method == "POST":
            # Si accede por POST, redirige a GET para mantener la sesión limpia
            return redirect(url_for("perfil_admin"))
        return render_template("perfil_admin.html")
    
    # Si no está autenticado o no es administrador, mostrar formulario de login
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

                return redirect(url_for("perfil_admin"))
            else:
                flash("⚠️ No tiene permisos de administrador.")
                return redirect(url_for("index"))

        flash("❌ Usuario o contraseña incorrectos.")
        return redirect(url_for("perfil_admin"))

    return render_template("admin.html")


# ============== MÓDULO DE GESTIÓN DE USUARIOS ==============

@app.route("/mod-usuarios")
def mod_usuarios():
    if "user_id" not in session or session.get("user_rol", "").lower() not in ("admin", "administrador"):
        return redirect(url_for("index"))
    return render_template("mod_usuarios.html")


@app.route("/buscar-usuarios", methods=["POST"])
def buscar_usuarios():
    if "user_id" not in session or session.get("user_rol", "").lower() not in ("admin", "administrador"):
        return {"success": False, "message": "No autorizado"}, 403

    search = request.get_json().get("search", "").strip()

    if not search:
        return {"usuarios": []}

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Buscar por nombre, email o fecha
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


@app.route("/crear-usuario", methods=["POST"])
def crear_usuario():
    if "user_id" not in session or session.get("user_rol", "").lower() not in ("admin", "administrador"):
        return {"success": False, "message": "No autorizado"}, 403

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
=======
def create_app():
    """Crea y configura la aplicación Flask, registrando los blueprints."""
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")

    # importar los módulos de rutas aquí para evitar dependencias circulares
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.profesor import profesor_bp
    from routes.alumno import alumno_bp
    from routes.oficina import oficina_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(profesor_bp)
    app.register_blueprint(alumno_bp)
    app.register_blueprint(oficina_bp)

    return app
>>>>>>> origin/main


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
