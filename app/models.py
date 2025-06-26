# app/models.py
from datetime import datetime
from app import db

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    service_time = db.Column(db.DateTime, nullable=True)
    expiration_time = db.Column(db.DateTime, nullable=True)
    last_serviced = db.Column(db.DateTime, nullable=True)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    event_type = db.Column(db.String(20), nullable=False)
    event_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Violation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    event_type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)