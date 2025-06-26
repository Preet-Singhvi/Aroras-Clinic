from marshmallow import Schema, fields, validate

class AssetSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    service_time = fields.DateTime(allow_none=True)
    expiration_time = fields.DateTime(allow_none=True)
    last_serviced = fields.DateTime(allow_none=True)

class NotificationSchema(Schema):
    id = fields.Int(dump_only=True)
    asset_id = fields.Int(required=True)
    message = fields.Str(required=True)
    event_type = fields.Str(required=True, validate=validate.OneOf(['service', 'expiration']))
    event_time = fields.DateTime(required=True)
    created_at = fields.DateTime(dump_only=True)

class ViolationSchema(Schema):
    id = fields.Int(dump_only=True)
    asset_id = fields.Int(required=True)
    message = fields.Str(required=True)
    event_type = fields.Str(required=True, validate=validate.OneOf(['service', 'expiration']))
    created_at = fields.DateTime(dump_only=True)

asset_schema = AssetSchema()
assets_schema = AssetSchema(many=True)
notification_schema = NotificationSchema()
notifications_schema = NotificationSchema(many=True)
violation_schema = ViolationSchema()
violations_schema = ViolationSchema(many=True)