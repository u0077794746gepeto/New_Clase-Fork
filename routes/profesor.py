from flask import Blueprint, render_template
from decorators import login_required, role_required

profesor_bp = Blueprint("profesor", __name__)


@profesor_bp.route("/")
@login_required
@role_required("Profesor")
def home():
    # aquí irían las vistas y la lógica específica de los profesores
    return "Página de profesor (pendiente de implementar)"
