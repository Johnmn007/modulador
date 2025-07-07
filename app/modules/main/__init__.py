from flask import Blueprint

main_bp = Blueprint(
    'main',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/main/static'
)

from . import routes  # Importa rutas para que queden registradas
