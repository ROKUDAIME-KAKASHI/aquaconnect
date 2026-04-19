import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)
from flask_babel import Babel
babel = Babel()


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # ── Config ──────────────────────────────────────────────────────────────
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///aquaconnect.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config['JWT_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config['JWT_COOKIE_SAMESITE'] = 'Lax'

    # ── Extensions ───────────────────────────────────────────────────────────
    from whitenoise import WhiteNoise
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = WhiteNoise(app.wsgi_app, root='app/static/', prefix='static/')
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # ── Security & Extensions ──────────────────────────────────────────────
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    
    # Restrict CORS for Production & Capacitor
    CORS(app, resources={r"/api/*": {
        "origins": [
            "https://aquaconnect-self.vercel.app", 
            "capacitor://localhost", 
            "http://localhost"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }})

    # Apply Rate Limiting to the API Blueprint
    from app.api.routes import api_bp
    limiter.limit("100 per hour")(api_bp)
    limiter.limit("10 per minute", methods=["POST"])(api_bp) # Stricter for mutations

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: blob:;"
        return response

    from flask import request, session

    def get_locale():
        # if a user is logged in, use the locale from the user settings
        lang = session.get('language')
        if lang:
            return lang
        try:
            from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
            from app.models import User
            verify_jwt_in_request(locations=['cookies'], optional=True)
            uid = get_jwt_identity()
            if uid:
                user = User.query.get(int(uid))
                if user and user.language:
                    return user.language
        except Exception:
            pass
        return request.accept_languages.best_match(['en', 'hi', 'bn', 'ta', 'te', 'ml', 'kn']) or 'en'
    
    babel.init_app(app, locale_selector=get_locale)

    # ── Register Blueprints ──────────────────────────────────────────────────
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.dashboard.routes import dashboard_bp
    from app.water_quality.routes import water_bp
    from app.financial.routes import financial_bp
    from app.forum.routes import forum_bp
    from app.api.routes import api_bp
    from app.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(water_bp, url_prefix='/water-quality')
    app.register_blueprint(financial_bp, url_prefix='/financial')
    app.register_blueprint(forum_bp, url_prefix='/forum')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # ── Error Handlers ───────────────────────────────────────────────────────
    from flask import render_template as rt
    @app.errorhandler(404)
    def page_not_found(e):
        return rt('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return rt('errors/500.html'), 500

    # ── Context Processor (injects current_user into all templates) ──────────
    @app.context_processor
    def inject_user():
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        from app.models import User
        try:
            verify_jwt_in_request(locations=['cookies'])
            uid = get_jwt_identity()
            user = User.query.get(int(uid))
            return {'current_user': user}
        except Exception:
            return {'current_user': None}

    @app.before_request
    def update_last_active():
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        from app.models import User
        from datetime import datetime, timezone
        from app import db
        try:
            verify_jwt_in_request(locations=['cookies'], optional=True)
            uid = get_jwt_identity()
            if uid:
                user = User.query.get(int(uid))
                if user:
                    user.last_active = datetime.now(timezone.utc)
                    db.session.commit()
        except Exception:
            pass

    # ── Create tables ────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    return app
