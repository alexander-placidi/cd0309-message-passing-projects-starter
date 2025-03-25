from marshmallow import Schema, fields


class LocationSchema(Schema):
    id = fields.Integer(required=True)
    person_id = fields.Integer(required=True)
    longitude = fields.String(attribute="longitude", required=True)
    latitude = fields.String(attribute="latitude", required=True)
    creation_time = fields.DateTime(required=True)



class PersonSchema(Schema):
    id = fields.Integer(required=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    company_name = fields.String(required=True)



class ConnectionSchema(Schema):
    location = fields.Nested(LocationSchema, required=True)
    person = fields.Nested(PersonSchema, required=True)
