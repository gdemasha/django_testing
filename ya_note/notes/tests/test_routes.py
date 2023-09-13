from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestRoute(TestCase):
    """Тестирование маршрутов."""
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )
        cls.urls_for_notes = (
            ('notes:add', None),
            ('notes:edit', (cls.note.slug,)),
            ('notes:detail', (cls.note.slug,)),
            ('notes:delete', (cls.note.slug,)),
            ('notes:list', None),
            ('notes:success', None),
        )
        cls.visitor = User.objects.create(username='Визитер')
        cls.visitor_client = Client()
        cls.visitor_client.force_login(cls.visitor)

    def test_home_login_logout_signup_availability(self):
        """
        Доступность главной страницы, страниц входа, выхода и регистрации
        для анонимных пользователей.
        """
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_author(self):
        """
        Доступность списка записей, отдельной заметки,
        страниц добавления заметки, редактирования, удаления,
        успешного добавления для автора.
        """
        self.client.force_login(self.author)
        for name, args in self.urls_for_notes:
            with self.subTest(user=self.author, name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_no_availability_for_anon(self):
        """
        Недоступность списка записей, отдельной заметки,
        страниц добавления заметки, редактирования, удаления,
        успешного добавления для анонимного пользователя.
        """
        for name, args in self.urls_for_notes:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_not_found_for_visitor(self):
        """
        Ошибка доступа для не-автора на страницы
        отдельной заметки, редактирования и удаления.
        """
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.visitor_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_for_anon(self):
        """Переадресация для анонимного пользователя."""
        login_url = reverse('users:login')
        for name, args in self.urls_for_notes:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
