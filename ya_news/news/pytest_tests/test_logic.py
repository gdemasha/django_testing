from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news_id):
    """Анонимный пользователь не может создать комментарий."""
    url = reverse('news:detail', args=news_id)
    client.post(url, form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(admin_client, form_data, news_id):
    """Авторизованный пользователь может создать комментарий."""
    url = reverse('news:detail', args=news_id)

    response = admin_client.post(url, form_data)

    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']


def test_user_cant_use_bad_words(admin_client, news_id):
    """Пользователь не может использовать запрещенные слова."""
    url = reverse('news:detail', args=news_id)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS}, еще текст'}

    response = admin_client.post(url, data=bad_words_data)

    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(
        author_client, comment_id, url_to_comments
):
    """Пользователь может удалить свои комментарии."""
    delete_url = reverse('news:delete', args=comment_id)

    response = author_client.post(delete_url)

    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(admin_client, comment_id):
    """Другой пользователь не может удалять чужие комментарии."""
    delete_url = reverse('news:delete', args=comment_id)

    response = admin_client.post(delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
        author_client, form_data, comment_id, url_to_comments, comment
):
    """Пользователь может редактировать свои комментарии."""
    edit_url = reverse('news:edit', args=comment_id)

    response = author_client.post(edit_url, form_data)

    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        admin_client, comment_id, form_data, comment
):
    """Другой пользователь не может редактировать чужие комментарии."""
    edit_url = reverse('news:edit', args=comment_id)

    response = admin_client.post(edit_url, form_data)

    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
