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

uuid_validator = colander.All(
    colander.Length(max=32, min=32))


@colander.deferred
def options_validator(node, kw):
    request = kw.get('request')

    def validator(node, value):
        question_type = request.json_body.get('question_type')
        if question_type != 'free_text' and len(value) < 2:
            raise colander.Invalid(node, 'Atleast 2 options are required')
    return validator


def response_get_uuid_validator(request):
    question_uuid = request.params.get('question_uuid')
    option_uuid = request.params.get('option_uuid')

    if not (question_uuid or option_uuid):
        request.errors.add(
            'uuid', 'required', 'question_uuid or option_uuid required')

    if question_uuid and option_uuid:
        request.errors.add(
            'uuid', 'required', 'Only 1 uuid is required.')
