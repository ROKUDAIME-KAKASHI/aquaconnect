from functools import wraps
from flask import render_template, redirect, url_for, request, flash
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.admin import admin_bp
from app.models import User, Farm, WaterQualityLog, ForumPost, ForumReply, Transaction
from app import db


def get_current_user():
    try:
        verify_jwt_in_request(locations=['cookies'])
        return User.query.get(int(get_jwt_identity()))
    except Exception:
        return None


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect(url_for('auth.login'))
        if user.role != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated


# ── Admin Dashboard ───────────────────────────────────────────────────────────

@admin_bp.route('/')
@admin_required
def index():
    user = get_current_user()
    stats = {
        'users':         User.query.count(),
        'farms':         Farm.query.count(),
        'water_logs':    WaterQualityLog.query.count(),
        'posts':         ForumPost.query.count(),
        'new_users_week': User.query.count(),  # simplified — use date filter in production
    }
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_posts_raw = ForumPost.query.order_by(ForumPost.created_at.desc()).limit(5).all()
    recent_posts = [p.to_dict() for p in recent_posts_raw]
    return render_template('admin/index.html', user=user, stats=stats,
                           recent_users=recent_users, recent_posts=recent_posts)


# ── User Management ───────────────────────────────────────────────────────────

@admin_bp.route('/users')
@admin_required
def users():
    user = get_current_user()
    query       = request.args.get('q', '').strip()
    role_filter = request.args.get('role', '').strip()

    q = User.query
    if query:
        q = q.filter(User.full_name.ilike(f'%{query}%') | User.email.ilike(f'%{query}%'))
    if role_filter:
        q = q.filter_by(role=role_filter)
    raw_users = q.order_by(User.created_at.desc()).all()

    users_data = []
    for u in raw_users:
        users_data.append({
            'id': u.id, 'full_name': u.full_name, 'email': u.email,
            'role': u.role, 'is_active': u.is_active,
            'created_at': u.created_at.isoformat(),
            'farm_count': Farm.query.filter_by(owner_id=u.id).count(),
        })
    return render_template('admin/users.html', user=user, users=users_data,
                           query=query, role_filter=role_filter)


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@admin_required
def toggle_user(user_id):
    current = get_current_user()
    target = User.query.get_or_404(user_id)
    if target.id == current.id:
        flash('You cannot ban yourself.', 'error')
    else:
        target.is_active = not target.is_active
        db.session.commit()
        flash(f'{"Banned" if not target.is_active else "Unbanned"}: {target.full_name}', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/role', methods=['POST'])
@admin_required
def change_role(user_id):
    target = User.query.get_or_404(user_id)
    new_role = request.form.get('role', 'farmer')
    if new_role in ('farmer', 'expert', 'admin'):
        target.role = new_role
        db.session.commit()
        flash(f'{target.full_name} role changed to {new_role}.', 'success')
    return redirect(url_for('admin.users'))


# ── Forum Moderation ──────────────────────────────────────────────────────────

CATEGORIES = ['General', 'Water Quality', 'Feeding & Nutrition',
              'Disease & Health', 'Financial', 'Technology', 'Market & Sales']


@admin_bp.route('/posts')
@admin_required
def posts():
    user = get_current_user()
    query           = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '').strip()

    q = ForumPost.query
    if query:
        q = q.filter(ForumPost.title.ilike(f'%{query}%') |
                     ForumPost.content.ilike(f'%{query}%'))
    if category_filter:
        q = q.filter_by(category=category_filter)
    raw_posts = q.order_by(ForumPost.created_at.desc()).all()
    post_data = [p.to_dict() for p in raw_posts]

    return render_template('admin/posts.html', user=user, posts=post_data,
                           query=query, category_filter=category_filter,
                           categories=CATEGORIES)


@admin_bp.route('/posts/<int:post_id>/delete', methods=['POST'])
@admin_required
def delete_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted by admin.', 'success')
    return redirect(url_for('admin.posts'))
