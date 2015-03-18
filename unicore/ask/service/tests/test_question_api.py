import uuid

from unicore.ask.service.tests import DBTestCase
from unicore.ask.service.models import QuestionOption, Question


class QuestionApiTestCase(DBTestCase):
    def create_question_option(self, session=None, **attrs):
        return self.create_model_object(QuestionOption, session, **attrs)

    def create_question(self, session=None, **attrs):
        return self.create_model_object(Question, session, **attrs)

    def setUp(self):
        super(QuestionApiTestCase, self).setUp()
        self.question_1 = self.create_question(
            self.db, title='What is your name', short_name='name',
            question_type='free_text',
            options=[])
        self.db.flush()
        self.question_1_option = self.create_question_option(
            self.db, question_id=self.question_1.uuid)

        self.question_2 = self.create_question(
            self.db, title='What is your age', short_name='age',
            question_type='multiple_choice',
            options=[])
        self.db.flush()

        self.create_question_option(
            self.db, title='<18', question_id=self.question_2.uuid)
        self.create_question_option(
            self.db, title='18-29', question_id=self.question_2.uuid)
        self.create_question_option(
            self.db, title='30-49', question_id=self.question_2.uuid)
        self.create_question_option(
            self.db, title='50+', question_id=self.question_2.uuid)

        self.question_3 = self.create_question(
            self.db, title='Which sports do you watch', short_name='sports',
            multiple=True, question_type='multiple_choice',
            options=[])
        self.db.flush()

        self.create_question_option(
            self.db, title='cricket', question_id=self.question_3.uuid)
        self.create_question_option(
            self.db, title='rugby', question_id=self.question_3.uuid)
        self.create_question_option(
            self.db, title='soccer', question_id=self.question_3.uuid)
        self.create_question_option(
            self.db, title='tennis', question_id=self.question_3.uuid)
        self.create_question_option(
            self.db, title='other', question_id=self.question_3.uuid)

        self.db.commit()

    def test_uuid(self):
        the_uuid = self.question_1._uuid
        self.assertEqual(the_uuid, uuid.UUID(self.question_1.uuid))
        self.question_1.uuid = self.question_1.uuid
        self.assertEqual(the_uuid, self.question_1._uuid)
        self.question_1.uuid = uuid.UUID(self.question_1.uuid)
        self.assertEqual(the_uuid, self.question_1._uuid)

    def test_question_not_found(self):
        self.app.get('/questions/%s' % uuid.uuid4(), status=404)

    def test_free_text_question(self):
        resp = self.app.get(
            '/questions/%s' % self.question_1.uuid)
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.json_body, self.question_1.to_dict())

    def test_multiple_choice_question(self):
        resp = self.app.get(
            '/questions/%s' % self.question_2.uuid)
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.json_body, self.question_2.to_dict())

    def test_multiple_choice_question_with_multiple_response(self):
        resp = self.app.get(
            '/questions/%s' % self.question_3.uuid)
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.json_body, self.question_3.to_dict())

    def test_edit(self):
        resp = self.app.put_json(
            '/questions/%s' % self.question_1.uuid,
            params={'title': 'What is your name?'})
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.json_body['title'], 'What is your name?')

        # test get also returns same data
        resp = self.app.get('/questions/%s' % self.question_1.uuid)
        self.assertEqual(resp.json_body['title'], 'What is your name?')

    def test_create(self):
        data = {
            'title': 'What is your name',
            'short_name': 'name',
            'question_type': 'free_text'}
        resp = self.app.post_json(
            '/questions', params=data)
        self.assertEqual(resp.status_int, 201)
        self.assertEqual(resp.json_body['title'], data['title'])
        self.assertEqual(resp.json_body['short_name'], data['short_name'])
        self.assertEqual(
            resp.json_body['question_type'], data['question_type'])
        self.assertEqual(resp.json_body['options'][0]['responses_count'], 0)
        self.assertEqual(resp.json_body['options'][0]['title'], data['title'])
        self.assertEqual(
            resp.json_body['options'][0]['short_name'], data['short_name'])

        # test get also returns same data
        resp = self.app.get(
            '/questions/%s' % resp.json_body['uuid'])
        self.assertEqual(resp.json_body['title'], data['title'])
        self.assertEqual(resp.json_body['short_name'], data['short_name'])
        self.assertEqual(
            resp.json_body['question_type'], data['question_type'])
        self.assertEqual(resp.json_body['multiple'], False)
        self.assertEqual(resp.json_body['options'][0]['responses_count'], 0)
        self.assertEqual(resp.json_body['options'][0]['title'], data['title'])
        self.assertEqual(
            resp.json_body['options'][0]['short_name'], data['short_name'])

    def test_create_missing_fields(self):
        resp = self.app.post_json(
            '/questions', params={}, status=400)
        self.assertEqual(
            resp.json_body['errors'][0]['description'], 'title is missing')
        self.assertEqual(
            resp.json_body['errors'][1]['description'],
            'question_type is missing')

    def test_create_invalid_question_type(self):
        data = {
            'title': 'What is your name',
            'short_name': 'name',
            'question_type': 'unknown'}
        resp = self.app.post_json(
            '/questions', params=data, status=400)
        self.assertEqual(
            resp.json_body['errors'][0]['description'],
            '"unknown" is not one of free_text, multiple_choice')

    def test_create_multiple_choice_invalid(self):
        # No options specified
        data = {
            'title': 'What is your name',
            'short_name': 'name',
            'question_type': 'multiple_choice'}
        resp = self.app.post_json(
            '/questions', params=data, status=400)
        self.assertEqual(
            resp.json_body['errors'][0]['description'],
            'Atleast 2 options are required')

        # Less than 2 options specified
        data = {
            'title': 'What is your age',
            'short_name': 'age',
            'question_type': 'multiple_choice',
            'options': [{'title': 'very old'}]
            }
        resp = self.app.post_json(
            '/questions', params=data, status=400)
        self.assertEqual(
            resp.json_body['errors'][0]['description'],
            'Atleast 2 options are required')

    def test_create_multiple_choice(self):
        data = {
            'title': 'What is your age',
            'short_name': 'age',
            'question_type': 'multiple_choice',
            'multiple': True,
            'options': [
                {'title': '<16', 'short_name': 'yonger_than_16'},
                {'title': '16-29', 'short_name': '17_to_29'},
                {'title': '30-50', 'short_name': '30_to_50'},
                {'title': '>50', 'short_name': 'older_than_50'},
            ]}
        resp = self.app.post_json('/questions', params=data, status=201)
        self.assertEqual(resp.json_body['title'], data['title'])
        self.assertEqual(resp.json_body['short_name'], data['short_name'])
        self.assertEqual(
            resp.json_body['question_type'], data['question_type'])
        self.assertEqual(resp.json_body['multiple'], True)
        self.assertEqual(resp.json_body['options'][0]['responses_count'], 0)
        self.assertEqual(resp.json_body['options'][0]['title'], '<16')
        self.assertEqual(
            resp.json_body['options'][0]['short_name'], 'yonger_than_16')
        self.assertEqual(len(resp.json_body['options']), 4)

        # test get also returns same data
        resp = self.app.get(
            '/questions/%s' % resp.json_body['uuid'])
        self.assertEqual(resp.json_body['title'], data['title'])
        self.assertEqual(resp.json_body['short_name'], data['short_name'])
        self.assertEqual(
            resp.json_body['question_type'], data['question_type'])
        self.assertEqual(resp.json_body['multiple'], True)
        self.assertEqual(resp.json_body['options'][0]['responses_count'], 0)
        self.assertEqual(resp.json_body['options'][0]['title'], '<16')
        self.assertEqual(
            resp.json_body['options'][0]['short_name'], 'yonger_than_16')
        self.assertEqual(len(resp.json_body['options']), 4)
