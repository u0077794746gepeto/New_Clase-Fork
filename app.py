from flask import Flask
import os
from dotenv import load_dotenv

# Cargar variables de entorno al iniciar la aplicación
load_dotenv()

def create_app():
    """Crea y configura la aplicación Flask, registrando los blueprints."""
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")

    # Importar los módulos de rutas
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.profesor import profesor_bp
    from routes.alumno import alumno_bp
    from routes.oficina import oficina_bp
    from routes.anuncios import anuncios_bp # IMPORTADO

    # Registrar los Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(profesor_bp)
    app.register_blueprint(alumno_bp)
    app.register_blueprint(oficina_bp)
    app.register_blueprint(anuncios_bp) # REGISTRADO

    @app.context_processor
    def inject_vars():
        return {'api_key': os.getenv("OPENWEATHER_API_KEY")}

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)