from flask import Flask
import os
from dotenv import load_dotenv

# cargar variables de entorno al iniciar la aplicación
load_dotenv()


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


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
