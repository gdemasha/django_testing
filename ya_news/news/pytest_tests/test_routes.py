import pytest

from pytest_django.asserts import assertRedirects

from http import HTTPStatus

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
def test_pages_availability(client, name, args):
    """Доступность страниц для анонимных пользователей."""
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id')),
        ('news:delete', pytest.lazy_fixture('comment_id')),
    ),
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client, expected_status, args, name
):
    """
    Авторизованный пользователь не может перейти на
    страницы редактирования и удаления
    чужого комментария.
    """
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id')),
        ('news:delete', pytest.lazy_fixture('comment_id')),
    ),
)
def test_redirect_for_anonymous_client(client, name, args):
    """Проверяет редирект для неавторизованного пользователя."""
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
