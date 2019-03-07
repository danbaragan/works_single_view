from marshmallow import fields, ValidationError
from flask_marshmallow import Marshmallow


ma = Marshmallow()


class WorkSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    iswc = fields.Str(dump_only=True)
    created = fields.DateTime(dump_only=True)
    modified = fields.DateTime(dump_only=True)
    title = fields.Str(dump_only=True)
    providers = fields.Nested(
        'ProviderSchema',
        dump_only=True,
        many=True,
    )
    contributors = fields.Nested(
        'ContributorSchema',
        dump_only=True,
        many=True,
    )


class ProviderSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    provider_work_id = fields.Int(attribute='workprovider.provider_work_id', dump_only=True)


class ContributorSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)


works_schema = WorkSchema(many=True)
