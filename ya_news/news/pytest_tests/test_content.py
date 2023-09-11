import pytest

from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'paramentrized_client, have_form',
    (
        (pytest.lazy_fixture('admin_client'), True),
        (pytest.lazy_fixture('client'), False),
    ),
)
def test_have_form(paramentrized_client, have_form, news_id):
    """Авторизованный пользователь видит форму, анонимный - нет."""
    url = reverse('news:detail', args=news_id)
    response = paramentrized_client.get(url)
    assert ('form' in response.context) is have_form


@pytest.mark.django_db
@pytest.mark.usefixtures('all_comments')
def test_comments_order(client, news_id):
    """Проверяет порядок вывода комментариев."""
    url = reverse('news:detail', args=news_id)
    response = client.get(url)
    all_comments = response.context['news'].comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
@pytest.mark.usefixtures('all_news')
def test_news_count(client):
    """Проверяет колличество новостей на главной странице."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures('all_news')
def test_news_order(client):
    """Проверяет порядок вывода новостей на главной странице."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates
