from marshmallow import Schema, fields


class ItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, dump_only=True)
    price = fields.Float(required=True)
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(lambda: StoreWitoutItemsSchema(), dump_only=True)

class ItemWithoutStoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, dump_only=True)
    price = fields.Float(required=True)


class ItemUpdateSchema(Schema):
    price = fields.Float(required=True)

class StoreSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    items = fields.List(fields.Nested(ItemWithoutStoreSchema()), dump_only=True)


class StoreWitoutItemsSchema(Schema):
    id = fields.Int()
    name = fields.Str()