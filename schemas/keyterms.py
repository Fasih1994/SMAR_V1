from marshmallow import Schema, fields, validate


ALLOWED_PLATFORMS = ["all", "twitter", "facebook", "instagram", 'tiktok', 'linkedin']


class KeytermGenSchema(Schema):
    id = fields.Int()
    text = fields.Str(required=True)
    terms = fields.List(cls_or_instance=fields.Str(), dump_only=True,)


class KeytermGetDataSchema(Schema):
    id = fields.Int()
    text = fields.Str(required=True)
    terms = fields.List(cls_or_instance=fields.Str(), required=True)
    platforms = fields.Str(validate=validate.OneOf(ALLOWED_PLATFORMS), required=True)