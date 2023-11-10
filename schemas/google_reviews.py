from marshmallow import Schema, fields


class GoooglePlaceDataSchema(Schema):
    text = fields.Str(required=True)

class GoooglePlaceIdSchema(Schema):
    id = fields.Str(required=True, location='query')
