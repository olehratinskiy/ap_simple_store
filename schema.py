from marshmallow import Schema,fields, validate, post_load
from  models import User,Item,Orders


class UserSchema(Schema):
    user_id = fields.Int()
    username = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Email(validate=validate.Email)
    password = fields.Str()

    @post_load()
    def create_user(self,data, **kwargs):
        return User(**data)


class ImgSchema(Schema):
    id = fields.Int()
    img = fields.Str()
    name = fields.Str()
    mimetype = fields.Str()


class ItemSchema(Schema):
    item_id = fields.Int()
    name = fields.Str()
    storage_quantity = fields.Int()
    price = fields.Int()
    status = fields.Str(validate= validate.OneOf(["sold out", "available"]))
    img_id = fields.Int()

    @post_load()
    def create_item(self, data, **kwargs):
        return Item(**data)


class OrdersSchema(Schema):
    order_id = fields.Int()
    user_id = fields.Int()
    item_id = fields.Int()
    item_quantity = fields.Int()
    price = fields.Int()

    @post_load()
    def create_orders(self,data ,**kwargs):
        return Orders(**data)







