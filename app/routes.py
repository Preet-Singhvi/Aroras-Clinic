# app/routes.py (updated)
from flask import Blueprint, request, abort
from flask_restful import Api, Resource
from app import db
from app.models import Asset, Notification, Violation
from app.schemas import asset_schema, assets_schema, notification_schema, notifications_schema, violation_schema, violations_schema
from app.utils import run_checks
from flasgger import swag_from
from datetime import datetime

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

class AssetResource(Resource):
    @swag_from({'responses': {200: {'description': 'List of all assets'}}})
    def get(self):
        """List all assets"""
        assets = Asset.query.all()
        return assets_schema.dump(assets), 200

    @swag_from({
        'parameters': [{
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'service_time': {'type': 'string', 'format': 'date-time'},
                    'expiration_time': {'type': 'string', 'format': 'date-time'},
                    'last_serviced': {'type': 'string', 'format': 'date-time'}
                },
                'required': ['name']
            }
        }],
        'responses': {
            201: {'description': 'Asset created successfully'},
            400: {'description': 'Validation error'}
        }
    })
    def post(self):
        """Create a new asset"""
        data = request.get_json()
        print("data : ",data)
        errors = asset_schema.validate(data)
        if errors:
            return {'message': 'Validation error', 'errors': errors}, 400
        
        if Asset.query.filter_by(name=data['name']).first():
            return {'message': 'Asset with this name already exists'}, 400
            
        asset = Asset(
            name=data['name'],
            service_time=datetime.fromisoformat(data['service_time']) if 'service_time' in data else None,
            expiration_time=datetime.fromisoformat(data['expiration_time']) if 'expiration_time' in data else None,
            last_serviced=datetime.fromisoformat(data['last_serviced']) if 'last_serviced' in data else None
        )
        print("Asset ",asset)
        db.session.add(asset)
        db.session.commit()
        return asset_schema.dump(asset), 201

class AssetDetailResource(Resource):
    @swag_from({'responses': {200: {'description': 'Asset details'}}})
    def get(self, asset_id):
        """Get asset details"""
        asset = Asset.query.get_or_404(asset_id)
        return asset_schema.dump(asset), 200

    @swag_from({
        'parameters': [{
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'service_time': {'type': 'string', 'format': 'date-time'},
                    'expiration_time': {'type': 'string', 'format': 'date-time'},
                    'last_serviced': {'type': 'string', 'format': 'date-time'}
                }
            }
        }],
        'responses': {
            200: {'description': 'Asset updated'},
            400: {'description': 'Validation error'}
        }
    })
    def put(self, asset_id):
        """Update an asset"""
        asset = Asset.query.get_or_404(asset_id)
        data = request.get_json()
        
        # Validate input
        errors = asset_schema.validate(data, partial=True)
        if errors:
            return {'message': 'Validation error', 'errors': errors}, 400
            
        # Update fields
        if 'name' in data:
            # Check for duplicate name
            if data['name'] != asset.name and Asset.query.filter_by(name=data['name']).first():
                return {'message': 'Asset with this name already exists'}, 400
            asset.name = data['name']
            
        if 'service_time' in data:
            asset.service_time = datetime.fromisoformat(data['service_time'])
        if 'expiration_time' in data:
            asset.expiration_time = datetime.fromisoformat(data['expiration_time'])
        if 'last_serviced' in data:
            asset.last_serviced = datetime.fromisoformat(data['last_serviced'])
            
        db.session.commit()
        return asset_schema.dump(asset), 200

    @swag_from({'responses': {204: {'description': 'Asset deleted'}}})
    def delete(self, asset_id):
        """Delete an asset"""
        asset = Asset.query.get_or_404(asset_id)
        db.session.delete(asset)
        db.session.commit()
        return '', 204

class RunChecks(Resource):
    @swag_from({'responses': {200: {'description': 'Checks executed successfully'}}})
    def post(self):
        """Run periodic checks"""
        run_checks()
        return {"message": "Checks executed"}, 200

class NotificationList(Resource):
    @swag_from({'responses': {200: {'description': 'List of all notifications'}}})
    def get(self):
        """List all notifications"""
        notifications = Notification.query.all()
        return notifications_schema.dump(notifications), 200

class ViolationList(Resource):
    @swag_from({'responses': {200: {'description': 'List of all violations'}}})
    def get(self):
        """List all violations"""
        violations = Violation.query.all()
        return violations_schema.dump(violations), 200

api.add_resource(AssetResource, '/assets')
api.add_resource(AssetDetailResource, '/assets/<int:asset_id>')
api.add_resource(RunChecks, '/run-checks')
api.add_resource(NotificationList, '/notifications')
api.add_resource(ViolationList, '/violations')