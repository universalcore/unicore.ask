from cornice.resource import resource, view
from pyramid.exceptions import NotFound

from unicore.ask.service.models import QuestionResponse, Question


def get_response_object(request):
    uuid = request.matchdict['uuid']
    response = request.db.query(QuestionResponse).get(uuid)

    if response is None:
        raise NotFound

    return response


def get_responses(request):
    question_uuid = request.matchdict['question_uuid']

    question = request.db.query(Question).get(question_uuid)

    if question is None:
        raise NotFound

    return question.responses.order_by('question_id')


@resource(
    collection_path='/responses/{question_uuid}',
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
