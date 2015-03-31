import colander

from unicore.ask.service import validators


class QuestionOptionSchema(colander.MappingSchema):
    uuid = colander.SchemaNode(
        colander.String(),
        validator=validators.uuid_validator, missing=None)
    title = colander.SchemaNode(
        colander.String(),
        validator=validators.option_title_validator)
    short_name = colander.SchemaNode(
        colander.String(),
        validator=validators.option_short_name_validator,
        missing=None)


class Options(colander.SequenceSchema):
    option = QuestionOptionSchema()


class QuestionSchema(colander.MappingSchema):
    app_uuid = colander.SchemaNode(
        colander.String(),
        validator=validators.uuid_validator)
    author_uuid = colander.SchemaNode(
        colander.String(),
        validator=validators.uuid_validator)
    content_uuid = colander.SchemaNode(
        colander.String(),
        validator=validators.uuid_validator)
    title = colander.SchemaNode(
        colander.String(),
        validator=validators.question_title_validator)
    short_name = colander.SchemaNode(
        colander.String(),
        validator=validators.question_short_name_validator,
        missing=None)
    question_type = colander.SchemaNode(
        colander.String(),
        validator=validators.question_type_validator)
    multiple = colander.SchemaNode(colander.Boolean(), default=False)
    options = Options(validator=validators.options_validator, default=[])


class QuestionResponseSchema(colander.MappingSchema):
    option_uuid = colander.SchemaNode(
        colander.String(),
        validator=validators.uuid_validator)
    app_uuid = colander.SchemaNode(
        colander.String(),
        validator=validators.uuid_validator)
    user_uuid = colander.SchemaNode(
        colander.String(),
        validator=validators.uuid_validator)
    text = colander.SchemaNode(
        colander.String())


class QuestionResponseGetSchema(colander.MappingSchema):
    question_uuid = colander.SchemaNode(
        colander.String(),
        location="querystring",
        validator=validators.uuid_validator,
        missing=None)
    option_uuid = colander.SchemaNode(
        colander.String(),
        location="querystring",
        validator=validators.uuid_validator,
        missing=None)
