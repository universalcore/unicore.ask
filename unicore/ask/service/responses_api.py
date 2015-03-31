from uuid import UUID
from cornice.resource import resource, view
from pyramid.exceptions import NotFound

from unicore.ask.service.models import (
    Question, QuestionResponse, QuestionOption)
from unicore.ask.service.schema import (
    QuestionResponseSchema, QuestionResponseGetSchema)
from unicore.ask.service.validators import response_get_uuid_validator


def get_response_object(request):
    uuid = request.matchdict['uuid']
    response = request.db.query(QuestionResponse).get(uuid)

    if response is None:
        raise NotFound

    return response


def get_responses(request):
    question_uuid = request.validated.get('question_uuid')
    option_uuid = request.validated.get('option_uuid')

    if question_uuid:
        question = request.db.query(Question).get(question_uuid)

        if not question:
            raise NotFound

        return question.responses

    if option_uuid:
        option = request.db.query(QuestionOption).get(option_uuid)

        if not option:
            raise NotFound

        return option.responses


def get_option_object(request):
    uuid = request.validated['option_uuid']
    option = request.db.query(QuestionOption).get(uuid)

    if option is None:
        raise NotFound

    return option


@resource(
    collection_path='/responses',
    path='/response/{uuid}')
class QuestionResponseResource(object):

    def __init__(self, request):
        self.request = request

    @view(renderer='json', schema=QuestionResponseSchema)
    def collection_post(self):
        def is_numeric_response(option, response):
            if (option.question.question_type == 'free_text' and
                    option.question.numeric):
                try:
                    int(response)
                except ValueError:
                    return False
            return True
        option = get_option_object(self.request)

        if not is_numeric_response(option, self.request.validated['text']):
            self.request.errors.add(
                'text', 'numeric', 'Numeric response is required.')
            self.request.status = 400
            return

        response = QuestionResponse()
        for attr, value in self.request.validated.iteritems():
            setattr(response, attr, value)
        response.question_id = option.question_id
        response.app_uuid = UUID(hex=self.request.validated['app_uuid'])
        response.user_uuid = UUID(hex=self.request.validated['user_uuid'])
        option.responses.append(response)
        option.responses_count = QuestionOption.responses_count + 1
        self.request.db.flush()
        return response.to_dict()

    @view(
        renderer='json',
        schema=QuestionResponseGetSchema,
        validators=response_get_uuid_validator)
    def collection_get(self):
        responses = get_responses(self.request)
        return [response.to_dict() for response in responses]

    @view(renderer='json')
    def get(self):
        response = get_response_object(self.request)
        return response.to_dict()
