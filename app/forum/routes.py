from flask import render_template, redirect, url_for, request, flash
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.forum import forum_bp
from app.models import User, ForumPost, ForumReply
from app import db


def get_current_user():
    try:
        verify_jwt_in_request(locations=['cookies'])
        return User.query.get(int(get_jwt_identity()))
    except Exception:
        return None


CATEGORIES = ['General', 'Water Quality', 'Feeding & Nutrition',
              'Disease & Health', 'Financial', 'Technology', 'Market & Sales']


@forum_bp.route('/')
def index():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    category = request.args.get('category', '')
    q = ForumPost.query
    if category:
        q = q.filter_by(category=category)
    posts = q.order_by(ForumPost.created_at.desc()).all()
    return render_template('forum/index.html',
                           user=user, posts=posts,
                           categories=CATEGORIES, active_category=category)


@forum_bp.route('/post/new', methods=['GET', 'POST'])
def new_post():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
        category = request.form.get('category', 'General')
        post = ForumPost(
            author_id=user.id,
            title=request.form.get('title', '').strip(),
            content=request.form.get('content', '').strip(),
            category=category,
        )
        db.session.add(post)
        db.session.commit()
        
        # --- AI Expert Auto-Reply ---
        if category in ['Disease & Health', 'Water Quality']:
            from app.services import generate_ai_expert_reply
            from app.models import User, ForumReply
            
            # Find or insert the AI user identity
            ai_user = User.query.filter_by(email='ai_expert@aquaconnect.com').first()
            if not ai_user:
                ai_user = User(
                    full_name='AquaConnect AI',
                    email='ai_expert@aquaconnect.com',
                    password_hash='ai_generated_placeholder',
                    role='expert'
                )
                db.session.add(ai_user)
                db.session.commit()
                
            ai_content = generate_ai_expert_reply(post.title, post.content)
            
            ai_reply = ForumReply(
                post_id=post.id,
                author_id=ai_user.id,
                content=ai_content,
                is_expert_answer=True
            )
            db.session.add(ai_reply)
            db.session.commit()

        return redirect(url_for('forum.post_detail', post_id=post.id))
    return render_template('forum/new_post.html', user=user, categories=CATEGORIES)


@forum_bp.route('/post/<int:post_id>')
def post_detail(post_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    post = ForumPost.query.get_or_404(post_id)
    post.views += 1
    db.session.commit()
    replies = ForumReply.query.filter_by(post_id=post_id).order_by(ForumReply.created_at).all()
    return render_template('forum/post_detail.html',
                           user=user, post=post, replies=replies)


@forum_bp.route('/post/<int:post_id>/reply', methods=['POST'])
def add_reply(post_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    content = request.form.get('content', '').strip()
    if content:
        reply = ForumReply(
            post_id=post_id,
            author_id=user.id,
            content=content,
            is_expert_answer=(user.role == 'expert'),
        )
        db.session.add(reply)
        db.session.commit()
    return redirect(url_for('forum.post_detail', post_id=post_id))


# ── Edit Post ─────────────────────────────────────────────────────────────────

@forum_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    post = ForumPost.query.get_or_404(post_id)
    if post.author_id != user.id and user.role != 'admin':
        flash('You can only edit your own posts.', 'error')
        return redirect(url_for('forum.post_detail', post_id=post_id))
    if request.method == 'POST':
        post.title    = request.form.get('title', '').strip() or post.title
        post.content  = request.form.get('content', '').strip() or post.content
        post.category = request.form.get('category', post.category)
        db.session.commit()
        flash('Post updated.', 'success')
        return redirect(url_for('forum.post_detail', post_id=post.id))
    return render_template('forum/edit_post.html', user=user, post=post, categories=CATEGORIES)


# ── Delete Post ───────────────────────────────────────────────────────────────

@forum_bp.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    post = ForumPost.query.get_or_404(post_id)
    if post.author_id != user.id and user.role != 'admin':
        flash('You can only delete your own posts.', 'error')
        return redirect(url_for('forum.post_detail', post_id=post_id))
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect(url_for('forum.index'))


# ── Delete Reply ──────────────────────────────────────────────────────────────

@forum_bp.route('/reply/<int:reply_id>/delete', methods=['POST'])
def delete_reply(reply_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    reply = ForumReply.query.get_or_404(reply_id)
    if reply.author_id != user.id and user.role != 'admin':
        flash('You can only delete your own replies.', 'error')
        return redirect(url_for('forum.post_detail', post_id=reply.post_id))
    post_id = reply.post_id
    db.session.delete(reply)
    db.session.commit()
    flash('Reply deleted.', 'success')
    return redirect(url_for('forum.post_detail', post_id=post_id))


# ── Search ────────────────────────────────────────────────────────────────────

@forum_bp.route('/search')
def search():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    query    = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()

    q = ForumPost.query
    if query:
        q = q.filter(
            ForumPost.title.ilike(f'%{query}%') |
            ForumPost.content.ilike(f'%{query}%')
        )
    if category:
        q = q.filter_by(category=category)
    raw_posts = q.order_by(ForumPost.created_at.desc()).limit(50).all()

    results = []
    for p in raw_posts:
        d = p.to_dict()
        d['has_expert_answer'] = any(r.is_expert_answer for r in p.replies)
        results.append(d)

    return render_template('forum/search.html', user=user,
                           results=results, query=query,
                           category=category, categories=CATEGORIES)


# ── Experts Directory ─────────────────────────────────────────────────────────

@forum_bp.route('/experts')
def experts():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    expert_users = User.query.filter_by(role='expert', is_active=True).all()
    experts_data = []
    for e in expert_users:
        experts_data.append({
            'id': e.id,
            'full_name': e.full_name,
            'post_count':     ForumPost.query.filter_by(author_id=e.id).count(),
            'reply_count':    ForumReply.query.filter_by(author_id=e.id).count(),
            'expert_answers': ForumReply.query.filter_by(author_id=e.id, is_expert_answer=True).count(),
        })
    return render_template('forum/experts.html', user=user, experts=experts_data)

