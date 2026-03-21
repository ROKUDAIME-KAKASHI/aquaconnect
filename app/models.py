from datetime import datetime, timezone
from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='farmer')  # farmer | expert | admin
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)

    farms = db.relationship('Farm', backref='owner', lazy=True)
    posts = db.relationship('ForumPost', backref='author', lazy=True)
    replies = db.relationship('ForumReply', backref='author', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
        }


class Farm(db.Model):
    __tablename__ = 'farms'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(200))
    area_hectares = db.Column(db.Float)
    fish_species = db.Column(db.String(200))
    water_source = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    water_logs = db.relationship('WaterQualityLog', backref='farm', lazy=True)
    transactions = db.relationship('Transaction', backref='farm', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'name': self.name,
            'location': self.location,
            'area_hectares': self.area_hectares,
            'fish_species': self.fish_species,
            'water_source': self.water_source,
        }


class WaterQualityLog(db.Model):
    __tablename__ = 'water_quality_logs'

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    ph = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    dissolved_oxygen = db.Column(db.Float, nullable=False)
    ammonia = db.Column(db.Float, default=0.0)
    salinity = db.Column(db.Float, default=0.0)
    health_status = db.Column(db.String(20))   # good | warning | critical
    alerts = db.Column(db.Text)                # JSON string list
    recorded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'ph': self.ph,
            'temperature': self.temperature,
            'dissolved_oxygen': self.dissolved_oxygen,
            'ammonia': self.ammonia,
            'salinity': self.salinity,
            'health_status': self.health_status,
            'alerts': json.loads(self.alerts) if self.alerts else [],
            'recorded_at': self.recorded_at.isoformat(),
        }


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # income | expense
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(80))
    description = db.Column(db.String(200))
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'type': self.type,
            'amount': self.amount,
            'category': self.category,
            'description': self.description,
            'date': self.date.isoformat(),
        }


class ForumPost(db.Model):
    __tablename__ = 'forum_posts'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(60), default='General')
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    replies = db.relationship('ForumReply', backref='post', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'author_id': self.author_id,
            'author_name': self.author.full_name if self.author else 'Unknown',
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'views': self.views,
            'reply_count': len(self.replies),
            'created_at': self.created_at.isoformat(),
        }


class ForumReply(db.Model):
    __tablename__ = 'forum_replies'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_expert_answer = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'author_id': self.author_id,
            'author_name': self.author.full_name if self.author else 'Unknown',
            'author_role': self.author.role if self.author else '',
            'content': self.content,
            'is_expert_answer': self.is_expert_answer,
            'created_at': self.created_at.isoformat(),
        }
