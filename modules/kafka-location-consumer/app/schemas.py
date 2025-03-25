from marshmallow import Schema, fields

class LocationSchema(Schema):
    id = fields.Integer(required=True)
    person_id = fields.Integer(required=True)
    longitude = fields.String(attribute="longitude", required=True)
    latitude = fields.String(attribute="latitude", required=True)
    creation_time = fields.DateTime(required=True)