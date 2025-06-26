from datetime import datetime, timedelta
from app import db
from app.models import Asset, Notification, Violation
from sqlalchemy.exc import SQLAlchemyError

def run_checks():
    now = datetime.utcnow()
    upcoming = now + timedelta(minutes=15)
    notifications = []
    violations = []

    assets = Asset.query.all()

    for asset in assets:
        if asset.service_time:
            if now <= asset.service_time <= upcoming:
                add_notification(
                    asset,
                    'service',
                    asset.service_time,
                    f"Service due at {asset.service_time}",
                    notifications
                )
            
            if now > asset.service_time and (
                asset.last_serviced is None or 
                asset.last_serviced < asset.service_time
            ):
                add_violation(
                    asset,
                    'service',
                    f"Service overdue since {asset.service_time}",
                    violations
                )

        if asset.expiration_time:
            if now <= asset.expiration_time <= upcoming:
                add_notification(
                    asset,
                    'expiration',
                    asset.expiration_time,
                    f"Expires at {asset.expiration_time}",
                    notifications
                )
            
            if now > asset.expiration_time:
                add_violation(
                    asset,
                    'expiration',
                    f"Expired at {asset.expiration_time}",
                    violations
                )

    if notifications:
        db.session.add_all(notifications)
    if violations:
        db.session.add_all(violations)
    
    try:
        db.session.commit()
        return {
            "notifications": len(notifications),
            "violations": len(violations)
        }
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

def add_notification(asset, event_type, event_time, message, collection):
    if not Notification.query.filter_by(
        asset_id=asset.id,
        event_type=event_type,
        event_time=event_time
    ).first():
        notification = Notification(
            asset_id=asset.id,
            message=message,
            event_type=event_type,
            event_time=event_time
        )
        collection.append(notification)

def add_violation(asset, event_type, message, collection):
    if not Violation.query.filter_by(
        asset_id=asset.id,
        event_type=event_type
    ).first():
        violation = Violation(
            asset_id=asset.id,
            message=message,
            event_type=event_type
        )
        collection.append(violation)