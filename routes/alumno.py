from flask import Blueprint
from decorators import login_required, role_required

alumno_bp = Blueprint("alumno", __name__)


@alumno_bp.route("/")
@login_required
@role_required("Alumno")
def home():
    # lógica de alumnos
    return "Página de alumno (pendiente de implementar)"
