from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify

User = get_user_model()


class NoteCreation(TestCase):
    """Тестирование создания записей."""
    MAX_LENGTH = 100

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Автор')
        cls.url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'zagolovok',
        }

    def test_anon_cant_create_note(self):
        """Анонимный пользователь не может создать запись."""
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать запись."""
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.user)
        self.assertEqual(note.slug, self.form_data['slug'])

    def test_not_unique_slug(self):
        """Если слаг не уникален, запись не будет создана."""
        note = Note.objects.create(
            title='Опа',
            text='Тут',
            slug='slug',
            author=self.user,
        )
        self.form_data['slug'] = note.slug
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=f'{note.slug}{WARNING}',
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_no_slug(self):
        """Если слага нет, то используется слагифицированный заголовок."""
        response = self.auth_client.post(self.url, data=self.form_data)
        new_slug = slugify(self.form_data['title'])[:self.MAX_LENGTH]
        self.assertRedirects(response, self.success_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.slug, new_slug)


class NoteEditDelete(TestCase):
    """Тестирование редактирования и удаления записей."""
    NOTE_TEXT = 'Запись'
    NEW_NOTE = 'Обновлённая запись'
    TITLE = 'Заголовок'
    NEW_TITLE = 'Кто я?'
    SLUG = 'slug'
    NEW_SLUG = 'Kto'

    @classmethod
    def setUpTestData(cls):
        cls.success_url = reverse('notes:success')
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.visitor = User.objects.create(username='Визитер')
        cls.visitor_client = Client()
        cls.visitor_client.force_login(cls.visitor)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug=cls.SLUG,
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'text': cls.NEW_NOTE,
            'title': cls.NEW_TITLE,
            'slug': cls.NEW_SLUG,
        }

    def test_author_deletes_note(self):
        """Проверяет, что автор может удалить свою запись."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_visitor_cant_delete_notes(self):
        """
        Проверяет, что сторонний пользователь
        не может удалить чужую запись.
        """
        response = self.visitor_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_edits_note(self):
        """Проверяет, что автор может редактировать свою запись."""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE)
        self.assertEqual(self.note.title, self.NEW_TITLE)
        self.assertEqual(self.note.slug, self.NEW_SLUG)

    def test_visitor_cant_edit_note(self):
        """
        Проверяет, что сторонний пользователь
        не может редактировать чужую запись.
        """
        response = self.visitor_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
