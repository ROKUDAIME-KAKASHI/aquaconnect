from flask import Blueprint

financial_bp = Blueprint('financial', __name__)

from app.financial import routes  # noqa
