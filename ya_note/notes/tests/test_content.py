from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    """Тестирование контента."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )
        cls.form_urls = (
            ('notes:add', None),
            ('notes:edit', (cls.note.slug,)),
        )
        cls.other = User.objects.create(username='Другой пользователь')
        cls.other_client = Client()
        cls.other_client.force_login(cls.other)
        cls.others_note = Note.objects.create(
            title='Другой заголовок',
            text='Другой текст',
            author=cls.other,
        )

    def test_form(self):
        """
        Залогиненный пользователь видит форму
        на страницах создания и редактирования заметки,
        а анонимный - нет.
        """
        for name, args in self.form_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response_author = self.author_client.get(url)
                response = self.client.get(url)
                self.assertIn('form', response_author.context)
                self.assertEqual(response.context, None)

    def test_notes_list_for_diff_users(self):
        """
        Отдельная заметка передается на страницу со списком заметок
        в списке object_list, в словаре context.
        В списке заметок одного пользователя нет заметок
        другого пользователя.
        """
        url = reverse('notes:list')
        response = self.author_client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        self.assertNotIn(self.others_note, object_list)
