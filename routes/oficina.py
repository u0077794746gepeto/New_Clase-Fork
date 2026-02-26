from flask import Blueprint
from decorators import login_required, role_required

oficina_bp = Blueprint("oficina", __name__)


@oficina_bp.route("/")
@login_required
@role_required("Oficina")
def home():
    # lógica de personal de administración distinta del administrador
    return "Página de oficina (pendiente de implementar)"
