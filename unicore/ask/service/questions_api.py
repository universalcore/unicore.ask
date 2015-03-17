from cornice.resource import resource, view
from pyramid.exceptions import NotFound

from unicore.ask.service.models import Question, QuestionOption
from unicore.ask.service.schema import QuestionSchema


def get_app_object(request):
    uuid = request.matchdict['uuid']
    question = request.db.query(Question).get(uuid)

    if question is None:
        raise NotFound

    return question


@resource(collection_path='/questions', path='/questions/{uuid}')
class QuestionResource(object):

    def __init__(self, request):
        self.request = request

    @view(renderer='json', schema=QuestionSchema)
    def collection_post(self):
        question = Question()
        self.request.db.add(question)

        for attr, value in self.request.validated.iteritems():
            if not attr == 'options':
                setattr(question, attr, value)
        self.request.db.flush()

        # Automatically create an option for Free Text question
        if question.question_type == 'free_text':
            option = QuestionOption(
                question_id=question.uuid,
                title=question.title,
                short_name=question.short_name)
            self.request.db.add(option)
            self.request.db.flush()
        else:
            for option in self.request.validated['options']:
                an_option = QuestionOption()
                for attr, value in option.iteritems():
                    setattr(an_option, attr, value)
                question.options.append(an_option)

        new_data = question.to_dict()
        self.request.response.status_int = 201
        return new_data

    @view(renderer='json')
    def get(self):
        question = get_app_object(self.request)
        return question.to_dict()

    @view(renderer='json')
    def put(self):
        return {}
