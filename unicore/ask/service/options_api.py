from cornice.resource import resource, view
from pyramid.exceptions import NotFound

from unicore.ask.service.models import QuestionOption
from unicore.ask.service.schema import QuestionOptionSchema


def get_app_object(request):
    uuid = request.matchdict['uuid']
    option = request.db.query(QuestionOption).get(uuid)

    if option is None:
        raise NotFound

    return option


def get_option_object(request, uuid):
    option = request.db.query(QuestionOption).get(uuid)

    if option is None:
        raise NotFound

    return option


@resource(
    collection_path='/options',
    path='/options/{uuid}',
    cors_origins=('*',))
class OptionResource(object):

    def __init__(self, request):
        self.request = request

    @view(renderer='json')
    def collection_get(self):
        qs = self.request.db.query(QuestionOption)
        if 'question_uuid' in self.request.GET:
            qs = qs.filter_by(question_id=self.request.GET['question_uuid'])
        else:
            qs = qs.all()
        return [
            q.to_dict() for q in qs]

    @view(renderer='json', schema=QuestionOptionSchema)
    def collection_post(self):
        option = QuestionOption()
        self.request.db.add(option)

        print self.request

        for attr, value in self.request.validated.iteritems():
            if attr != 'uuid':
                setattr(option, attr, value)
        self.request.db.flush()

        new_data = option.to_dict()
        self.request.response.status_int = 201
        return new_data

    @view(renderer='json')
    def get(self):
        option = get_app_object(self.request)
        return option.to_dict()

    @view(renderer='json')
    def delete(self):
        option = get_app_object(self.request)
        self.request.db.delete(option)
        self.request.response.status_int = 204
        return {}

    @view(renderer='json', schema=QuestionOptionSchema)
    def put(self):
        option = get_app_object(self.request)
        for attr, value in self.request.validated.iteritems():
            if value is not None and not attr == 'options':
                setattr(option, attr, value)
        return option.to_dict()
