from flask import Blueprint

water_bp = Blueprint('water_quality', __name__)

from app.water_quality import routes  # noqa
