from marshmallow import Schema, fields

class PersonSchema(Schema):
    person_id = fields.Integer()
    first_name = fields.String()
    last_name = fields.String()
    company_name = fields.String()

