from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.api import api_bp
from app.models import User, Farm, WaterQualityLog, Transaction, ForumPost
from app.services import analyze_water_quality, calculate_financial_summary
from app import db, bcrypt
import json


@api_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'AquaConnect API'})


# ── Auth ─────────────────────────────────────────────────────────────────────

@api_bp.route('/auth/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(full_name=data['full_name'], email=data['email'],
                password_hash=hashed, role=data.get('role', 'farmer'))
    db.session.add(user)
    db.session.commit()
    token = create_access_token(identity=str(user.id))
    return jsonify({'user': user.to_dict(), 'access_token': token}), 201


@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    token = create_access_token(identity=str(user.id))
    return jsonify({'user': user.to_dict(), 'access_token': token})


# ── Farms ─────────────────────────────────────────────────────────────────────

@api_bp.route('/farms', methods=['GET'])
@jwt_required()
def api_get_farms():
    uid = int(get_jwt_identity())
    farms = Farm.query.filter_by(owner_id=uid).all()
    return jsonify([f.to_dict() for f in farms])


@api_bp.route('/farms', methods=['POST'])
@jwt_required()
def api_create_farm():
    uid = int(get_jwt_identity())
    data = request.get_json()
    farm = Farm(owner_id=uid, **{k: data.get(k) for k in
                ['name', 'location', 'area_hectares', 'fish_species', 'water_source']})
    db.session.add(farm)
    db.session.commit()
    return jsonify(farm.to_dict()), 201


# ── Water Quality ─────────────────────────────────────────────────────────────

@api_bp.route('/water-quality', methods=['POST'])
@jwt_required()
def api_analyze_water():
    data = request.get_json()
    result = analyze_water_quality(
        ph=data['ph'],
        temperature=data['temperature'],
        dissolved_oxygen=data['dissolved_oxygen'],
        ammonia=data.get('ammonia', 0.0),
        salinity=data.get('salinity', 0.0),
    )
    log = WaterQualityLog(
        farm_id=data['farm_id'],
        ph=data['ph'], temperature=data['temperature'],
        dissolved_oxygen=data['dissolved_oxygen'],
        ammonia=data.get('ammonia', 0.0),
        salinity=data.get('salinity', 0.0),
        health_status=result['health_status'],
        alerts=json.dumps(result['alerts']),
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({**log.to_dict(), **result})


@api_bp.route('/water-quality/<int:farm_id>', methods=['GET'])
@jwt_required()
def api_water_history(farm_id):
    logs = (WaterQualityLog.query
            .filter_by(farm_id=farm_id)
            .order_by(WaterQualityLog.recorded_at.desc())
            .limit(50).all())
    return jsonify([l.to_dict() for l in logs])


# ── Financial ─────────────────────────────────────────────────────────────────

@api_bp.route('/financial/summary/<int:farm_id>', methods=['GET'])
@jwt_required()
def api_financial_summary(farm_id):
    txs = Transaction.query.filter_by(farm_id=farm_id).all()
    return jsonify(calculate_financial_summary([t.to_dict() for t in txs]))


# ── Forum ─────────────────────────────────────────────────────────────────────

@api_bp.route('/forum/posts', methods=['GET'])
@jwt_required()
def api_forum_posts():
    posts = ForumPost.query.order_by(ForumPost.created_at.desc()).limit(50).all()
    return jsonify([p.to_dict() for p in posts])
