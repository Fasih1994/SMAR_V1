from marshmallow import Schema, fields, validate, ValidationError, validates_schema


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
    from_date = fields.Date(format='%Y-%m-%d', error_messages={'invalid': 'Invalid date format. Use yyyy-mm-dd'})
    to_date = fields.Date(format='%Y-%m-%d', error_messages={'invalid': 'Invalid date format. Use yyyy-mm-dd'})

    @validates_schema
    def validate_dates(self, data, **kwargs):
        # Check that either both from_date and to_date are present or both are absent
        if ('from_date' in data and 'to_date' not in data) or ('to_date' in data and 'from_date' not in data):
            raise ValidationError("Both 'from_date' and 'to_date' must be provided together.")
