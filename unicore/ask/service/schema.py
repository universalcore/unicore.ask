import colander

from unicore.ask.service import validators


class QuestionSchema(colander.MappingSchema):
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
