import colander

from unicore.ask.service.models import Question

question_title_validator = colander.All(
    colander.Length(max=Question.title_length))
question_short_name_validator = colander.All(
    colander.Length(max=Question.short_name_length))
question_type_validator = colander.OneOf(Question.question_types)
