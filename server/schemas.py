from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)

class ExpenseSchema(Schema):
    id = fields.Int(dump_only=True)
    category = fields.Str(required=True, validate=validate.OneOf(["Travel", "Lodging", "Food"]))
    description = fields.Str(allow_none=True)
    amount = fields.Decimal(as_string=True, required=True)
    date = fields.Date(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)