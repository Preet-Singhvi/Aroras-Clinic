from flask import Blueprint, request
from flask_restful import Api, Resource
from app import db
from app.models import Asset, Notification, Violation
from app.schemas import asset_schema, assets_schema, notification_schema, notifications_schema, violation_schema, violations_schema
from app.utils import run_checks
from app.response_model import success_response, error_response
from flasgger import swag_from
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

class AssetResource(Resource):
    @swag_from({
        'responses': {
            200: {
                'description': 'List of all assets',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string'},
                        'code': {'type': 'integer'},
                        'message': {'type': 'string'},
                        'data': {
                            'type': 'array',
                            'items': {'$ref': '#/definitions/Asset'}
                        }
                    }
                }
            }
        }
    })
    def get(self):
        """List all assets"""
        try:
            assets = Asset.query.all()
            data = assets_schema.dump(assets)
            return success_response(data)
        except SQLAlchemyError as e:
            return error_response("Database error", 500, {"details": str(e)})

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
            201: {
                'description': 'Asset created successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string'},
                        'code': {'type': 'integer'},
                        'message': {'type': 'string'},
                        'data': {'$ref': '#/definitions/Asset'}
                    }
                }
            },
            400: {
                'description': 'Validation error',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string'},
                        'code': {'type': 'integer'},
                        'message': {'type': 'string'},
                        'errors': {'type': 'object'}
                    }
                }
            }
        }
    })
    def post(self):
        """Create a new asset"""
        data = request.get_json()
        
        # Validate input
        errors = asset_schema.validate(data)
        if errors:
            return error_response("Validation failed", 400, errors)
        
        # Check for duplicate name
        if Asset.query.filter_by(name=data['name']).first():
            return error_response("Asset name already exists", 409)
        
        try:
            # Create asset
            asset = Asset(
                name=data['name'],
                service_time=datetime.fromisoformat(data['service_time']) if 'service_time' in data else None,
                expiration_time=datetime.fromisoformat(data['expiration_time']) if 'expiration_time' in data else None,
                last_serviced=datetime.fromisoformat(data['last_serviced']) if 'last_serviced' in data else None
            )
            
            db.session.add(asset)
            db.session.commit()
            return success_response(asset_schema.dump(asset), "Asset created", 201)
        
        except (TypeError, ValueError) as e:
            return error_response("Invalid date format", 400, {"details": str(e)})
        except SQLAlchemyError as e:
            db.session.rollback()
            return error_response("Database error", 500, {"details": str(e)})

class AssetDetailResource(Resource):
    @swag_from({
        'parameters': [{
            'name': 'asset_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the asset'
        }],
        'responses': {
            200: {
                'description': 'Asset details',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string'},
                        'code': {'type': 'integer'},
                        'message': {'type': 'string'},
                        'data': {'$ref': '#/definitions/Asset'}
                    }
                }
            },
            404: {
                'description': 'Asset not found',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string'},
                        'code': {'type': 'integer'},
                        'message': {'type': 'string'}
                    }
                }
            }
        }
    })
    def get(self, asset_id):
        """Get asset details"""
        try:
            asset = Asset.query.get(asset_id)
            if not asset:
                return error_response("Asset not found", 404)
            return success_response(asset_schema.dump(asset))
        except SQLAlchemyError as e:
            return error_response("Database error", 500, {"details": str(e)})

    @swag_from({
        'parameters': [
            {
                'name': 'asset_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the asset'
            },
            {
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
            }
        ],
        'responses': {
            200: {
                'description': 'Asset updated',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string'},
                        'code': {'type': 'integer'},
                        'message': {'type': 'string'},
                        'data': {'$ref': '#/definitions/Asset'}
                    }
                }
            },
            400: {
                'description': 'Validation error',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string'},
                        'code': {'type': 'integer'},
                        'message': {'type': 'string'},
                        'errors': {'type': 'object'}
                    }
                }
            },
            404: {
                'description': 'Asset not found',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string'},
                        'code': {'type': 'integer'},
                        'message': {'type': 'string'}
                    }
                }
            }
        }
    })
    def put(self, asset_id):
        """Update an asset"""
        try:
            asset = Asset.query.get(asset_id)
            if not asset:
                return error_response("Asset not found", 404)
                
            data = request.get_json()
            
            # Validate input
            errors = asset_schema.validate(data, partial=True)
            if errors:
                return error_response("Validation failed", 400, errors)
                
            # Update fields
            if 'name' in data:
                # Check for duplicate name
                if data['name'] != asset.name and Asset.query.filter_by(name=data['name']).first():
                    return error_response("Asset name already exists", 409)
                asset.name = data['name']
                
            if 'service_time' in data:
                asset.service_time = datetime.fromisoformat(data['service_time'])
            if 'expiration_time' in data:
                asset.expiration_time = datetime.fromisoformat(data['expiration_time'])
            if 'last_serviced' in data:
                asset.last_serviced = datetime.fromisoformat(data['last_serviced'])
                
            db.session.commit()
            return success_response(asset_schema.dump(asset), "Asset updated")
            
        except (TypeError, ValueError) as e:
            return error_response("Invalid date format", 400, {"details": str(e)})
        except SQLAlchemyError as e:
            db.session.rollback()
            return error_response("Database error", 500, {"details": str(e)})

    @swag_from({
        'parameters': [{
            'name': 'asset_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the asset'
        }],
        'responses': {
            204: {
                'description': 'Asset deleted',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string'},
                        'code': {'type': 'integer'},
                        'message': {'type': 'string'}
                    }
                }
            },
            404: {
                'description': 'Asset not found',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string'},
                        'code': {'type': 'integer'},
                        'message': {'type': 'string'}
                    }
                }
            }
        }
    })
    def delete(self, asset_id):
        """Delete an asset"""
        try:
            asset = Asset.query.get(asset_id)
            if not asset:
                return error_response("Asset not found", 404)
                
            db.session.delete(asset)
            db.session.commit()
            return success_response(None, "Asset deleted", 204)
        except SQLAlchemyError as e:
            db.session.rollback()
            return error_response("Database error", 500, {"details": str(e)})

class RunChecks(Resource):
    @swag_from({
        'responses': {
            200: {
                'description': 'Checks executed successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string'},
                        'code': {'type': 'integer'},
                        'message': {'type': 'string'},
                        'data': {
                            'type': 'object',
                            'properties': {
                                'notifications_created': {'type': 'integer'},
                                'violations_created': {'type': 'integer'}
                            }
                        }
                    }
                }
            }
        }
    })
    def post(self):
        """Run periodic checks"""
        try:
            result = run_checks()
            return success_response({
                "notifications_created": result.get("notifications", 0),
                "violations_created": result.get("violations", 0)
            }, "Checks completed")
        except Exception as e:
            return error_response("Error running checks", 500, {"details": str(e)})

class NotificationList(Resource):
    @swag_from({
        'responses': {
            200: {
                'description': 'List of all notifications',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string'},
                        'code': {'type': 'integer'},
                        'message': {'type': 'string'},
                        'data': {
                            'type': 'array',
                            'items': {'$ref': '#/definitions/Notification'}
                        }
                    }
                }
            }
        }
    })
    def get(self):
        """List all notifications"""
        try:
            notifications = Notification.query.all()
            data = notifications_schema.dump(notifications)
            return success_response(data)
        except SQLAlchemyError as e:
            return error_response("Database error", 500, {"details": str(e)})

class ViolationList(Resource):
    @swag_from({
        'responses': {
            200: {
                'description': 'List of all violations',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string'},
                        'code': {'type': 'integer'},
                        'message': {'type': 'string'},
                        'data': {
                            'type': 'array',
                            'items': {'$ref': '#/definitions/Violation'}
                        }
                    }
                }
            }
        }
    })
    def get(self):
        """List all violations"""
        try:
            violations = Violation.query.all()
            data = violations_schema.dump(violations)
            return success_response(data)
        except SQLAlchemyError as e:
            return error_response("Database error", 500, {"details": str(e)})

api.add_resource(AssetResource, '/assets')
api.add_resource(AssetDetailResource, '/assets/<int:asset_id>')
api.add_resource(RunChecks, '/run-checks')
api.add_resource(NotificationList, '/notifications')
api.add_resource(ViolationList, '/violations')