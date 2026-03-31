from flask import render_template, redirect, url_for, request, session
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.main import main_bp
from app import db
from app.models import User

@main_bp.route('/')
def index():
    try:
        verify_jwt_in_request(locations=['cookies'])
        return redirect(url_for('dashboard.index'))
    except Exception:
        return render_template('landing.html')

@main_bp.route('/set_language/<lang>')
def set_language(lang):
    if lang not in ['en', 'hi', 'bn', 'ta', 'te', 'ml', 'kn']:
        lang = 'en'
    
    session['language'] = lang

    try:
        verify_jwt_in_request(locations=['cookies'], optional=True)
        uid = get_jwt_identity()
        if uid:
            user = User.query.get(int(uid))
            if user:
                user.language = lang
                db.session.commit()
    except Exception:
        pass
        
    resp = redirect(request.referrer or url_for('main.index'))
    if lang == 'en':
        resp.delete_cookie('googtrans', path='/')
    else:
        resp.set_cookie('googtrans', f'/en/{lang}', path='/')
        
    return resp
