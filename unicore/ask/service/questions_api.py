from pyramid.exceptions import NotFound

from cornice.resource import resource, view

from unicore.hub.service.models import Question


def get_question_object(request):
    uuid = request.matchdict['uuid']
    question = request.db.query(Question).get(uuid)

    if question is None:
        raise NotFound

    return question


@resource(collection_path='/questions', path='/questions/{uuid}')
class QuestionResource(object):

    def __init__(self, request):
        self.request = request

    @view(renderer='json')
    def collection_post(self):
        return {}

    @view(renderer='json')
    def get(self):
        question = get_question_object(self.request)
        return question.to_dict()

    @view(renderer='json')
    def put(self):
        return {}
