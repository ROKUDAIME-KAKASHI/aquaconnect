import json, csv, io
from flask import render_template, redirect, url_for, request, flash, make_response
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.water_quality import water_bp
from app.models import User, Farm, WaterQualityLog
from app.services import analyze_water_quality
from app import db


def get_current_user():
    try:
        verify_jwt_in_request(locations=['cookies'])
        uid = get_jwt_identity()
        return User.query.get(int(uid))
    except Exception:
        return None


@water_bp.route('/')
def index():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    farms = Farm.query.filter_by(owner_id=user.id).all()
    farm_id = request.args.get('farm_id', type=int)
    selected_farm = None
    logs = []
    if farms:
        selected_farm = Farm.query.get(farm_id) if farm_id else farms[0]
        if selected_farm and selected_farm.owner_id == user.id:
            logs = (WaterQualityLog.query
                    .filter_by(farm_id=selected_farm.id)
                    .order_by(WaterQualityLog.recorded_at.desc())
                    .limit(20).all())
    return render_template('water_quality/index.html',
                           user=user, farms=farms, selected_farm=selected_farm,
                           logs=[l.to_dict() for l in logs])


@water_bp.route('/analyze', methods=['POST'])
def analyze():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    farm_id = request.form.get('farm_id', type=int)
    farm = Farm.query.get(farm_id)
    if not farm or farm.owner_id != user.id:
        flash('Farm not found.', 'error')
        return redirect(url_for('water_quality.index'))

    ph = float(request.form.get('ph', 7.0))
    temperature = float(request.form.get('temperature', 25.0))
    dissolved_oxygen = float(request.form.get('dissolved_oxygen', 6.0))
    ammonia = float(request.form.get('ammonia', 0.0))
    salinity = float(request.form.get('salinity', 0.0))

    result = analyze_water_quality(ph, temperature, dissolved_oxygen, ammonia, salinity)

    log = WaterQualityLog(
        farm_id=farm_id,
        ph=ph, temperature=temperature,
        dissolved_oxygen=dissolved_oxygen,
        ammonia=ammonia, salinity=salinity,
        health_status=result['health_status'],
        alerts=json.dumps(result['alerts']),
    )
    db.session.add(log)
    db.session.commit()

    farms = Farm.query.filter_by(owner_id=user.id).all()
    logs = (WaterQualityLog.query
            .filter_by(farm_id=farm.id)
            .order_by(WaterQualityLog.recorded_at.desc())
            .limit(20).all())
    return render_template('water_quality/index.html',
                           user=user, farms=farms, selected_farm=farm,
                           logs=[l.to_dict() for l in logs],
                           analysis_result=result)


# ── History (paginated) ───────────────────────────────────────────────────────

@water_bp.route('/history')
def history():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    farms = Farm.query.filter_by(owner_id=user.id).all()
    farm_id = request.args.get('farm_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 25
    selected_farm = None
    logs = []
    total_pages = 1

    if farms:
        selected_farm = Farm.query.get(farm_id) if farm_id else farms[0]
        if selected_farm and selected_farm.owner_id == user.id:
            q = WaterQualityLog.query.filter_by(farm_id=selected_farm.id)\
                .order_by(WaterQualityLog.recorded_at.desc())
            total = q.count()
            total_pages = max(1, (total + per_page - 1) // per_page)
            page = max(1, min(page, total_pages))
            logs = [l.to_dict() for l in q.offset((page - 1) * per_page).limit(per_page).all()]

    return render_template('water_quality/history.html',
                           user=user, farms=farms, selected_farm=selected_farm,
                           logs=logs, page=page, total_pages=total_pages)


# ── Alerts ────────────────────────────────────────────────────────────────────

@water_bp.route('/alerts')
def alerts():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    farms = Farm.query.filter_by(owner_id=user.id).all()
    farm_ids = [f.id for f in farms]
    status_filter = request.args.get('status', '')

    base_q = WaterQualityLog.query.filter(WaterQualityLog.farm_id.in_(farm_ids))
    critical_count = base_q.filter_by(health_status='critical').count()
    warning_count  = base_q.filter_by(health_status='warning').count()
    good_count     = base_q.filter_by(health_status='good').count()

    if status_filter in ('critical', 'warning'):
        alert_q = base_q.filter_by(health_status=status_filter)
    else:
        alert_q = base_q.filter(WaterQualityLog.health_status.in_(['critical', 'warning']))

    raw_logs = alert_q.order_by(WaterQualityLog.recorded_at.desc()).limit(100).all()

    farm_map = {f.id: f.name for f in farms}
    alert_logs = []
    for l in raw_logs:
        d = l.to_dict()
        d['farm_name'] = farm_map.get(l.farm_id, 'Unknown')
        alert_logs.append(d)

    return render_template('water_quality/alerts.html',
                           user=user, alert_logs=alert_logs,
                           critical_count=critical_count,
                           warning_count=warning_count,
                           good_count=good_count,
                           status_filter=status_filter)


# ── Export CSV ────────────────────────────────────────────────────────────────

@water_bp.route('/export')
def export_csv():
    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    farm_id = request.args.get('farm_id', type=int)
    farms = Farm.query.filter_by(owner_id=user.id).all()
    farm_ids = [f.id for f in farms]

    q = WaterQualityLog.query.filter(WaterQualityLog.farm_id.in_(farm_ids))
    if farm_id and farm_id in farm_ids:
        q = q.filter_by(farm_id=farm_id)
    logs = q.order_by(WaterQualityLog.recorded_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Farm ID', 'pH', 'Temperature', 'Dissolved Oxygen', 'Ammonia', 'Salinity', 'Status', 'Alerts'])
    for l in logs:
        writer.writerow([l.recorded_at, l.farm_id, l.ph, l.temperature,
                         l.dissolved_oxygen, l.ammonia, l.salinity,
                         l.health_status, l.alerts or ''])
    output.seek(0)
    resp = make_response(output.getvalue())
    resp.headers['Content-Disposition'] = 'attachment; filename=water_quality_export.csv'
    resp.headers['Content-Type'] = 'text/csv'
    return resp

