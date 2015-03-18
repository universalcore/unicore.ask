import colander

from unicore.ask.service.models import Question, QuestionOption

question_title_validator = colander.All(
    colander.Length(max=Question.title_length))
question_short_name_validator = colander.All(
    colander.Length(max=Question.short_name_length))
question_type_validator = colander.OneOf(Question.question_types)

option_title_validator = colander.All(
    colander.Length(max=QuestionOption.title_length))
option_short_name_validator = colander.All(
    colander.Length(max=QuestionOption.short_name_length))
option_uuid_validator = colander.All(
    colander.Length(max=32, min=32))


@colander.deferred
def options_validator(node, kw):
    request = kw.get('request')

    def validator(node, value):
        question_type = request.json_body.get('question_type')
        if question_type != 'free_text' and len(value) < 2:
            raise colander.Invalid(node, 'Atleast 2 options are required')
    return validator
