from flask import render_template, redirect, url_for
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.main import main_bp


@main_bp.route('/')
def index():
    try:
        verify_jwt_in_request(locations=['cookies'])
        return redirect(url_for('dashboard.index'))
    except Exception:
        return render_template('landing.html')

