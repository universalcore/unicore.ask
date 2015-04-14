from uuid import UUID
from cornice.resource import resource, view
from pyramid.exceptions import NotFound

from unicore.ask.service.models import Question, QuestionOption
from unicore.ask.service.schema import QuestionSchema, QuestionsGetSchema


def get_question_object(request):
    uuid = request.matchdict['uuid']
    question = request.db.query(Question).get(uuid)

    if question is None:
        raise NotFound

    return question


def get_questions(request):
    query = {
        'app_uuid': request.validated['app_uuid'],
        'content_uuid': request.validated['content_uuid']
    }
    return request.db.query(Question).filter_by(**query)


def get_option_object(request, uuid):
    option = request.db.query(QuestionOption).get(uuid)

    if option is None:
        raise NotFound

    return option


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
        question.author_uuid = UUID(hex=self.request.validated['author_uuid'])
        question.app_uuid = UUID(hex=self.request.validated['app_uuid'])
        question.content_uuid = UUID(
            hex=self.request.validated['content_uuid'])
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
        question = get_question_object(self.request)
        return question.to_dict()

    @view(renderer='json', schema=QuestionsGetSchema)
    def collection_get(self):
        questions = get_questions(self.request)
        return [q.to_dict() for q in questions]

    @view(renderer='json', schema=QuestionSchema)
    def put(self):
        question = get_question_object(self.request)
        for attr, value in self.request.validated.iteritems():
            if value is not None and not attr == 'options':
                setattr(question, attr, value)
        question.author_uuid = UUID(hex=self.request.validated['author_uuid'])
        question.app_uuid = UUID(hex=self.request.validated['app_uuid'])
        question.content_uuid = UUID(
            hex=self.request.validated['content_uuid'])

        validated_options = self.request.validated.get('options', [])

        # Delete existing options
        existing_options = [
            o['uuid'] for o in validated_options if o['uuid']]
        for option in question.options:
            if option.uuid not in existing_options:
                self.request.db.delete(option)

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
