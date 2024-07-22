from unittest import TestCase
from random import randint
from unittest.mock import Mock
from django.test import RequestFactory
from authentication.models import User
from suggest.views import SuggestBookView


class TestSuggestBookView(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        username = f'testuser{randint(1, 10000)}'
        self.user = User.objects.create(username=username, password='123451')

    def test_empty_genre_ratings(self):
        request = self.factory.get('/suggest/')
        request.user = self.user
        view = SuggestBookView()
        response = view.get(request)
        self.assertEqual(response.status_code, 404)

    def test_empty_preferred_genres(self):
        request = self.factory.get('/suggest/')
        request.user = self.user
        view = SuggestBookView()
        view.cursor = Mock()
        view.cursor.fetchall.return_value = [
            ('Horror', 4.5), ('Romance', 4.5)]
        response = view.get(request)
        self.assertEqual(response.status_code, 404)

    def test_empty_books(self):
        request = self.factory.get('/suggest/')
        request.user = self.user
        view = SuggestBookView()
        view.cursor = Mock()
        view.cursor.fetchall.side_effect = [
            [('Horror', 4.5), ('Romance', 4.5)], []]
        response = view.get(request)
        self.assertEqual(response.status_code, 404)

    
