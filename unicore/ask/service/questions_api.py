from cornice.resource import resource, view


@resource(collection_path='/questions', path='/questions/{uuid}')
class QuestionResource(object):

    def __init__(self, request):
        self.request = request

    @view(renderer='json')
    def collection_post(self):
        return {}

    @view(renderer='json')
    def get(self):
        return {}

    @view(renderer='json')
    def put(self):
        return {}
