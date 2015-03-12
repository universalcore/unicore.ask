import uuid

from unicore.ask.service.tests import BaseTestCase


class QuestionApiTestCase(BaseTestCase):

    def setUp(self):
        super(QuestionApiTestCase, self).setUp()
        self.question_1_option = self.create_free_text_option(self.db)
        self.question_1 = self.create_free_text_question(
            self.db, title='What is your name', short_name='name',
            options=[])
        self.question_2 = self.create_multiple_choice_question(
            self.db, title='What is your age', short_name='age',
            options=[
                self.create_multiple_choice_option(self.db, title='<18'),
                self.create_multiple_choice_option(self.db, title='18-29'),
                self.create_multiple_choice_option(self.db, title='30-49'),
                self.create_multiple_choice_option(self.db, title='50+'),
            ])
        self.question_3 = self.create_multiple_choice_question(
            self.db, title='Which sports do you watch', short_name='sports',
            multiple=True,
            options=[
                self.create_multiple_choice_option(self.db, title='cricket'),
                self.create_multiple_choice_option(self.db, title='rugby'),
                self.create_multiple_choice_option(self.db, title='soccer'),
                self.create_multiple_choice_option(self.db, title='tennis'),
                self.create_multiple_choice_option(self.db, title='other'),
            ])

        self.db.commit()

    def test_view(self):
        resp = self.app.get(
            '/questions/%s' % self.question_1.uuid)
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.json_body, {
            'uuid': self.question_1.uuid,
            'title': 'What is your name',
            'short_name': 'name',
            'type': 'free_text',
            'options': [{
                'uuid': self.question_1_option.uuid,
                'responses': [],
                'responses_count': 0,
            }]
            })

    def test_edit(self):
        # change non-privileged fields
        resp = self.app.put_json(
            '/questions/%s' % uuid.uuid4().hex,
            params={'title': 'foo2'})
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.json_body, {})

    def test_create(self):
        data = {'title': 'foobar'}
        resp = self.app.post_json(
            '/questions', params=data)
        self.assertEqual(resp.json_body, {})
