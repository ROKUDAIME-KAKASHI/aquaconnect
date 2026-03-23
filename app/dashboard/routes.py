from flask import render_template, redirect, url_for, request, flash
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.dashboard import dashboard_bp
from app.models import User, Farm, WaterQualityLog
from app import db


def get_current_user():
    try:
        verify_jwt_in_request(locations=['cookies'])
        uid = get_jwt_identity()
        return User.query.get(int(uid))
    except Exception:
        return None


@dashboard_bp.route('/')
def index():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    farms = Farm.query.filter_by(owner_id=user.id).all()
    farm = farms[0] if farms else None

    latest_log = None
    if farm:
        latest_log = (WaterQualityLog.query
                      .filter_by(farm_id=farm.id)
                      .order_by(WaterQualityLog.recorded_at.desc())
                      .first())

    return render_template('dashboard/index.html',
                           user=user,
                           farm=farm,
                           farms=farms,
                           latest_log=latest_log)


@dashboard_bp.route('/farm/create', methods=['GET', 'POST'])
def create_farm():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        farm = Farm(
            owner_id=user.id,
            name=request.form.get('name', '').strip(),
            location=request.form.get('location', '').strip(),
            area_hectares=float(request.form.get('area_hectares') or 0),
            fish_species=request.form.get('fish_species', '').strip(),
            water_source=request.form.get('water_source', '').strip(),
        )
        db.session.add(farm)
        db.session.commit()
        flash('Farm created successfully!', 'success')
        return redirect(url_for('dashboard.index'))
    return render_template('dashboard/create_farm.html', user=user)


@dashboard_bp.route('/farm/<int:farm_id>')
def farm_detail(farm_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    farm = Farm.query.get_or_404(farm_id)
    if farm.owner_id != user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard.index'))
    logs_count = WaterQualityLog.query.filter_by(farm_id=farm.id).count()
    logs = [l.to_dict() for l in
            WaterQualityLog.query.filter_by(farm_id=farm.id)
            .order_by(WaterQualityLog.recorded_at.desc()).limit(8).all()]
    from app.models import Transaction
    tx_count = Transaction.query.filter_by(farm_id=farm.id).count()
    recent_txs = Transaction.query.filter_by(farm_id=farm.id)\
        .order_by(Transaction.date.desc()).limit(8).all()
    latest_log = logs[0] if logs else None
    
    from app.services import get_weather_alert
    weather_forecast = get_weather_alert(farm.location)

    return render_template('dashboard/farm_detail.html',
                           user=user, farm=farm, logs=logs, logs_count=logs_count,
                           latest_log=latest_log, tx_count=tx_count,
                           transactions=[t.to_dict() for t in recent_txs],
                           weather_forecast=weather_forecast)


@dashboard_bp.route('/farm/<int:farm_id>/edit', methods=['GET', 'POST'])
def edit_farm(farm_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    farm = Farm.query.get_or_404(farm_id)
    if farm.owner_id != user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        farm.name = request.form.get('name', '').strip() or farm.name
        farm.location = request.form.get('location', '').strip()
        farm.area_hectares = float(request.form.get('area_hectares') or 0)
        farm.fish_species = request.form.get('fish_species', '').strip()
        farm.water_source = request.form.get('water_source', '').strip()
        db.session.commit()
        flash('Farm updated successfully.', 'success')
        return redirect(url_for('dashboard.farm_detail', farm_id=farm.id))
    return render_template('dashboard/edit_farm.html', user=user, farm=farm)


@dashboard_bp.route('/farm/<int:farm_id>/delete', methods=['POST'])
def delete_farm(farm_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    farm = Farm.query.get_or_404(farm_id)
    if farm.owner_id != user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard.index'))
    db.session.delete(farm)
    db.session.commit()
    flash(f'Farm "{farm.name}" has been deleted.', 'success')
    return redirect(url_for('dashboard.index'))
