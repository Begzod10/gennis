from flask_apispec import use_kwargs, marshal_with
from marshmallow import Schema

from webargs import fields


class PetSchema(Schema):
    class Meta:
        fields = ('name', 'desc', 'price')
