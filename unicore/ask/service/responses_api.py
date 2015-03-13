from cornice.resource import resource, view
from pyramid.exceptions import NotFound

from unicore.ask.service.models import QuestionResponse


def get_response_object(request):
    uuid = request.matchdict['uuid']
    response = request.db.query(QuestionResponse).get(uuid)

    if response is None:
        raise NotFound

    return response


def get_responses(request):
    question_option_uuid = request.matchdict['question_option_uuid']
    return request.db.query(QuestionResponse).filter_by(
        question_option_id=question_option_uuid)


@resource(
    collection_path='/responses/{question_option_uuid}',
    path='/response/{uuid}')
class QuestionResponseResource(object):

    def __init__(self, request):
        self.request = request

    @view(renderer='json')
    def collection_post(self):
        return {}

    @view(renderer='json')
    def collection_get(self):
        responses = get_responses(self.request)
        return [response.to_dict() for response in responses]

    @view(renderer='json')
    def get(self):
        response = get_response_object(self.request)
        return response.to_dict()

    @view(renderer='json')
    def put(self):
        return {}
