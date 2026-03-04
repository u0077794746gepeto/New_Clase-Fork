from flask import Blueprint, render_template
from decorators import login_required, role_required
from db import get_db_connection
from psycopg2.extras import RealDictCursor

alumno_bp = Blueprint("alumno", __name__)

@alumno_bp.route("/")
@login_required
@role_required("Alumno")
def home():
    # lógica de alumnos
    return "Página de alumno (pendiente de implementar)"

@alumno_bp.route('/campus')
@login_required
@role_required("Alumno")
def campus():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Traemos los anuncios para que el alumno los vea
    cur.execute('SELECT * FROM anuncios ORDER BY fecha_publicacion DESC LIMIT 5;')
    anuncios = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('campus.html', anuncios=anuncios)