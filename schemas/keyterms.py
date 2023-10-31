from marshmallow import Schema, fields, validate


ALLOWED_PLATFORMS = ["twitter", "facebook", "instagram", 'tiktok', 'linkedin']


class KeytermGenSchema(Schema):
    id = fields.Int()
    text = fields.Str(required=True)
    terms = fields.List(cls_or_instance=fields.Str(), dump_only=True,)

class KeytermSelectSchema(Schema):
    terms = fields.List(cls_or_instance=fields.Str(), required=True)

class KeytermDataFromTable(Schema):
    terms = fields.List(cls_or_instance=fields.Str(), required=True)#, location="query")



class KeytermGetDataSchema(Schema):
    id = fields.Int()
    text = fields.Str(required=True)
    terms = fields.List(cls_or_instance=fields.Str(), required=True)
    platform = fields.Str(validate=validate.OneOf(ALLOWED_PLATFORMS), required=True)