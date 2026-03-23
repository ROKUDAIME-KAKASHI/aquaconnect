import secrets
import os
import smtplib
from email.message import EmailMessage
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from datetime import datetime, timezone, timedelta
from flask import render_template, redirect, url_for, request, flash, make_response, current_app
from flask_jwt_extended import (
    create_access_token, set_access_cookies, unset_jwt_cookies,
    verify_jwt_in_request, get_jwt_identity
)
from app.auth import auth_bp
from app.models import User, Farm, WaterQualityLog, ForumPost, ForumReply
from app import db, bcrypt


def get_current_user():
    try:
        verify_jwt_in_request(locations=['cookies'])
        return User.query.get(int(get_jwt_identity()))
    except Exception:
        return None


@auth_bp.route('/landing')
def landing():
    """Public landing / marketing page."""
    try:
        verify_jwt_in_request(locations=['cookies'])
        return redirect(url_for('dashboard.index'))  # already logged in
    except Exception:
        return render_template('landing.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            token = create_access_token(identity=str(user.id))
            resp = make_response(redirect(url_for('dashboard.index')))
            set_access_cookies(resp, token)
            return resp
        flash('Invalid email or password.', 'error')
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'farmer')

        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'error')
            return render_template('auth/register.html')

        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(full_name=full_name, email=email, password_hash=hashed, role=role)
        db.session.add(user)
        db.session.commit()

        token = create_access_token(identity=str(user.id))
        resp = make_response(redirect(url_for('dashboard.index')))
        set_access_cookies(resp, token)
        return resp
    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    resp = make_response(redirect(url_for('auth.login')))
    unset_jwt_cookies(resp)
    return resp


# ── Forgot / Reset Password ──────────────────────────────────────────────────

def send_reset_email(to_email, reset_link):
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_user = os.environ.get('SMTP_USERNAME')
    smtp_pass = os.environ.get('SMTP_PASSWORD')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    
    if not (smtp_server and smtp_user and smtp_pass):
        # Fallback for local development
        print("\n" + "="*50)
        print("📨 MOCK EMAIL: Password Reset Link")
        print(f"To: {to_email}")
        print(f"Link: {reset_link}")
        print("="*50 + "\n")
        return

    msg = EmailMessage()
    msg['Subject'] = 'Reset your AquaConnect Password'
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg.set_content(f"Hello,\n\nClick the link below to reset your password:\n\n{reset_link}\n\nIf you did not request a password reset, please ignore this email.\n\nThanks,\nAquaConnect Team")
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    sent = False
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = s.dumps(user.email, salt='password-reset-salt')
            reset_link = url_for('auth.reset_password', token=token, _external=True)
            send_reset_email(user.email, reset_link)
        sent = True  # always show success to prevent email enumeration
    return render_template('auth/forgot_password.html', sent=sent)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    invalid = False
    email = None
    
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600) # 1 hour
    except (SignatureExpired, BadSignature):
        invalid = True

    if request.method == 'POST' and not invalid:
        new_pwd = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if len(new_pwd) < 8:
            flash('Password must be at least 8 characters.', 'error')
        elif new_pwd != confirm:
            flash('Passwords do not match.', 'error')
        else:
            user = User.query.filter_by(email=email).first()
            if user:
                user.password_hash = bcrypt.generate_password_hash(new_pwd).decode('utf-8')
                db.session.commit()
            flash('Password reset successfully! Please sign in.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token, invalid=invalid)


# ── Profile ──────────────────────────────────────────────────────────────────

@auth_bp.route('/profile')
def profile():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    farm_count = Farm.query.filter_by(owner_id=user.id).count()
    log_count  = WaterQualityLog.query.join(Farm).filter(Farm.owner_id == user.id).count()
    post_count = ForumPost.query.filter_by(author_id=user.id).count()
    reply_count = ForumReply.query.filter_by(author_id=user.id).count()
    return render_template('auth/profile.html', user=user,
                           farm_count=farm_count, log_count=log_count,
                           post_count=post_count, reply_count=reply_count)


@auth_bp.route('/profile/update', methods=['POST'])
def update_profile():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    new_name  = request.form.get('full_name', '').strip()
    new_email = request.form.get('email', '').strip().lower()
    if not new_name or not new_email:
        flash('Name and email are required.', 'error')
        return redirect(url_for('auth.profile'))
    if new_email != user.email and User.query.filter_by(email=new_email).first():
        flash('That email is already in use.', 'error')
        return redirect(url_for('auth.profile'))
    user.full_name = new_name
    user.email = new_email
    db.session.commit()
    flash('Profile updated successfully.', 'success')
    return redirect(url_for('auth.profile'))


# ── Settings ─────────────────────────────────────────────────────────────────

@auth_bp.route('/settings')
def settings():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    return render_template('auth/settings.html', user=user)


@auth_bp.route('/settings/change-password', methods=['POST'])
def change_password():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    current = request.form.get('current_password', '')
    new_pwd  = request.form.get('new_password', '')
    confirm  = request.form.get('confirm_password', '')
    if not bcrypt.check_password_hash(user.password_hash, current):
        flash('Current password is incorrect.', 'error')
    elif len(new_pwd) < 8:
        flash('New password must be at least 8 characters.', 'error')
    elif new_pwd != confirm:
        flash('New passwords do not match.', 'error')
    else:
        user.password_hash = bcrypt.generate_password_hash(new_pwd).decode('utf-8')
        db.session.commit()
        flash('Password changed successfully.', 'success')
    return redirect(url_for('auth.settings'))


@auth_bp.route('/settings/delete-account', methods=['POST'])
def delete_account():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    resp = make_response(redirect(url_for('auth.login')))
    unset_jwt_cookies(resp)
    db.session.delete(user)
    db.session.commit()
    flash('Your account has been permanently deleted.', 'info')
    return resp
