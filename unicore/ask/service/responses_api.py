from cornice.resource import resource, view
from pyramid.exceptions import NotFound

from unicore.ask.service.models import (
    QuestionResponse, QuestionOption)
from unicore.ask.service.schema import QuestionResponseSchema


def get_response_object(request):
    uuid = request.matchdict['uuid']
    response = request.db.query(QuestionResponse).get(uuid)

    if response is None:
        raise NotFound

    return response


def get_responses(request):
    uuid = request.matchdict['option_uuid']

    option = request.db.query(QuestionOption).get(uuid)

    if option is None:
        raise NotFound

    return option.responses


def get_option_object(request):
    uuid = request.matchdict['option_uuid']
    option = request.db.query(QuestionOption).get(uuid)

    if option is None:
        raise NotFound

    return option


@resource(
    collection_path='/responses/{option_uuid}',
    path='/response/{uuid}')
class QuestionResponseResource(object):

    def __init__(self, request):
        self.request = request

    @view(renderer='json', schema=QuestionResponseSchema)
    def collection_post(self):
        option = get_option_object(self.request)

        response = QuestionResponse()
        for attr, value in self.request.validated.iteritems():
            setattr(response, attr, value)
        response.question_id = option.question_id
        option.responses.append(response)
        self.request.db.flush()
        return response.to_dict()

    @view(renderer='json')
    def collection_get(self):
        # TODO: find a way to return question responses
        # and not just option responses
        responses = get_responses(self.request)
        return [response.to_dict() for response in responses]

    @view(renderer='json')
    def get(self):
        response = get_response_object(self.request)
        return response.to_dict()
