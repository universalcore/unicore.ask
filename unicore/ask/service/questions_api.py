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


def get_option_object(request, uuid):
    option = request.db.query(QuestionOption).get(uuid)

    if option is None:
        raise NotFound

    return option


@resource(
    collection_path='/questions',
    path='/questions/{uuid}',
    cors_origins=('*',))
class QuestionResource(object):

    def __init__(self, request):
        self.request = request

    @view(renderer='json')
    def collection_get(self):
        return [q.to_dict() for q in self.request.db.query(Question).all()]

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
        else:
            for option in self.request.validated['options']:
                # ignore uuid on post
                if 'uuid' in option:
                    option.pop('uuid')

                an_option = QuestionOption()
                for attr, value in option.iteritems():
                    setattr(an_option, attr, value)
                question.options.append(an_option)

        self.request.db.flush()

        new_data = question.to_dict()
        self.request.response.status_int = 201
        return new_data

    @view(renderer='json')
    def get(self):
        question = get_app_object(self.request)
        return question.to_dict()

    @view(renderer='json')
    def delete(self):
        question = get_app_object(self.request)
        self.request.db.delete(question)
        self.request.response.status_int = 204
        return {}

    @view(renderer='json', schema=QuestionSchema)
    def put(self):
        question = get_app_object(self.request)
        for attr, value in self.request.validated.iteritems():
            if value is not None and not attr == 'options':
                setattr(question, attr, value)

        validated_options = self.request.validated.get('new_options', [])

        # Delete existing options
        #existing_options = [
        #    o['title'] for o in validated_options]
        #for option in question.options:
        #    if option.title not in existing_options:
        #        self.request.db.delete(option)

        for option in validated_options:
            uuid = option.pop('uuid')

            if uuid is None:
                # adding a new option
                an_option = QuestionOption()
                for attr, value in option.iteritems():
                    setattr(an_option, attr, value)
                question.options.append(an_option)
            else:
                # Edit existing option
                an_option = get_option_object(self.request, uuid)
                for attr, value in option.iteritems():
                    setattr(an_option, attr, value)
        return question.to_dict()
