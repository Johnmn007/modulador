from flask import Blueprint, render_template
from flask_login import login_required
# from . import estudiante_bp

estudiante_bp = Blueprint(
    'estudiante',  # ← este nombre define el prefijo del endpoint: estudiante.dashboard
    __name__,
    url_prefix='/estudiante',
    template_folder='templates'
)


@estudiante_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('estudiante/dashboard.html')



