import uuid

from unicore.ask.service.tests import DBTestCase
from unicore.ask.service.models import (
    QuestionOption, Question, QuestionResponse)


class ResponsesApiTestCase(DBTestCase):
    def create_question_option(self, session=None, **attrs):
        return self.create_model_object(QuestionOption, session, **attrs)

    def create_question(self, session=None, **attrs):
        return self.create_model_object(Question, session, **attrs)

    def create_question_response(self, session=None, **attrs):
        return self.create_model_object(QuestionResponse, session, **attrs)

    def setUp(self):
        super(ResponsesApiTestCase, self).setUp()

        # Create Free Text Question
        self.question_1 = self.create_question(
            self.db, title='What is your name', short_name='name',
            question_type='free_text',
            options=[])
        self.db.flush()
        self.question_1_option = self.create_question_option(
            self.db, question_id=self.question_1.uuid)
        self.db.flush()
        self.question_1_response = self.create_question_response(
            self.db,
            question_id=self.question_1.uuid,
            question_option_id=self.question_1_option.uuid,
            text='joe soap')
        self.db.flush()

        # Create Multiple Choice Question (radio)
        self.question_2 = self.create_question(
            self.db, title='What is your age', short_name='age',
            question_type='multiple_choice',
            options=[])
        self.db.flush()

        self.age_option_1 = self.create_question_option(
            self.db, title='<18', question_id=self.question_2.uuid)
        self.age_option_2 = self.create_question_option(
            self.db, title='18-29', question_id=self.question_2.uuid)
        self.age_option_3 = self.create_question_option(
            self.db, title='30-49', question_id=self.question_2.uuid)
        self.age_option_4 = self.create_question_option(
            self.db, title='50+', question_id=self.question_2.uuid)
        self.db.flush()
        self.question_2_response = self.create_question_response(
            self.db,
            question_id=self.question_2.uuid,
            question_option_id=self.age_option_3.uuid,
            text='30-49')
        self.db.flush()

        # Create Multiple Choice Question (multiple select)
        self.question_3 = self.create_question(
            self.db, title='Which sports do you watch', short_name='sports',
            multiple=True, question_type='multiple_choice',
            options=[])
        self.db.flush()

        self.sport_option_1 = self.create_question_option(
            self.db, title='cricket', question_id=self.question_3.uuid)
        self.sport_option_2 = self.create_question_option(
            self.db, title='rugby', question_id=self.question_3.uuid)
        self.sport_option_3 = self.create_question_option(
            self.db, title='soccer', question_id=self.question_3.uuid)
        self.sport_option_4 = self.create_question_option(
            self.db, title='tennis', question_id=self.question_3.uuid)
        self.sport_option_5 = self.create_question_option(
            self.db, title='other', question_id=self.question_3.uuid)
        self.db.flush()
        self.question_3_response_1 = self.create_question_response(
            self.db,
            question_id=self.question_3.uuid,
            question_option_id=self.sport_option_1.uuid,
            text='cricket')
        self.question_3_response_2 = self.create_question_response(
            self.db,
            question_id=self.question_3.uuid,
            question_option_id=self.sport_option_4.uuid,
            text='tennis')
        self.db.flush()

        self.db.commit()

    def test_response_not_found(self):
        self.app.get('/response/%s' % uuid.uuid4(), status=404)

    def test_free_text_question_response(self):
        resp = self.app.get(
            '/response/%s' % self.question_1_response.uuid)
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.json_body, self.question_1_response.to_dict())

        resp = self.app.get(
            '/responses?option_uuid=%s' % self.question_1_option.uuid)
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.json_body, [self.question_1_response.to_dict()])

    def test_multiple_choice_question(self):
        resp = self.app.get(
            '/response/%s' % self.question_2_response.uuid)
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.json_body, self.question_2_response.to_dict())

        resp = self.app.get(
            '/responses?option_uuid=%s' % self.age_option_3.uuid)
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.json_body, [self.question_2_response.to_dict()])

    def test_multiple_choice_question_with_multiple_responses(self):
        resp = self.app.get(
            '/response/%s' % self.question_3_response_1.uuid)
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.json_body, self.question_3_response_1.to_dict())
        resp = self.app.get(
            '/response/%s' % self.question_3_response_2.uuid)
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.json_body, self.question_3_response_2.to_dict())

        resp = self.app.get(
            '/responses?option_uuid=%s' % self.sport_option_1.uuid)
        self.assertEqual(
            resp.json_body, [self.question_3_response_1.to_dict()])

        resp = self.app.get(
            '/responses?option_uuid=%s' % self.sport_option_4.uuid)
        self.assertEqual(
            resp.json_body, [self.question_3_response_2.to_dict()])

    def test_invalid_get_responses(self):
        resp = self.app.get('/responses', status=400)
        self.assertEqual(
            resp.json_body['errors'][0]['description'],
            'question_uuid or option_uuid required')

        data = {
            'option_uuid': uuid.uuid4().hex,
            'question_uuid': uuid.uuid4().hex}
        resp = self.app.get('/responses', params=data, status=400)
        self.assertEqual(
            resp.json_body['errors'][0]['description'],
            'Only 1 uuid is required.')

    def test_create(self):
        data = {'text': 'foobar', 'option_uuid': self.question_1_option.uuid}
        resp = self.app.post_json(
            '/responses', params=data)
        self.assertEqual(resp.json_body['text'], data['text'])

        resp = self.app.get(
            '/questions/%s' % self.question_1.uuid)
        self.assertEqual(resp.json_body['options'][0]['responses_count'], 1)
