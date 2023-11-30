from marshmallow import Schema, fields


class ReviewSchema(Schema):
    class Meta:
        fields = ('id', 'author_name', 'rating', 'text', 'time', 'translated',
                  'profile_photo_url', 'relative_time_description', 'author_url',
                  'language', 'original_language')


class PlaceSchema(Schema):
    reviews = fields.Nested(ReviewSchema, many=True)

    class Meta:
        fields = ('id', 'formatted_phone_number',
                  'name', 'rating', 'lat', 'lng',
                  'reviews', 'city', 'category')

class ApiResponseSchema(Schema):
    result = fields.Nested(PlaceSchema)
    status = fields.String()

    class Meta:
        fields = ('result', 'status')