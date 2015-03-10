import uuid

from unicore.ask.service.tests import BaseTestCase


class QuestionApiTestCase(BaseTestCase):

    def test_view(self):
        resp = self.app.get(
            '/questions/%s' % uuid.uuid4().hex)
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.json_body, {})

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
