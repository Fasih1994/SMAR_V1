from marshmallow import Schema, fields


class GoooglePlaceDataSchema(Schema):
    text = fields.Str(required=True)
    includedType = fields.Str(required=False)

class GoooglePlaceIdSchema(Schema):
    id = fields.Str(required=True, location='query')
    includedType = fields.Str(required=False)

