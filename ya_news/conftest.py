from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Новость',
    )
    return news


@pytest.fixture
def all_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    return all_news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        text='Комментарий',
        author=author,
        news=news,
    )
    return comment


@pytest.fixture
def all_comments(author, news, freezer):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return all_comments


@pytest.fixture
def news_id(news):
    return news.id,


@pytest.fixture
def comment_id(comment):
    return comment.id,


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор комментария')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def form_data():
    return {'text': 'Текст комментария'}


@pytest.fixture
def url_to_comments(news_id):
    news_url = reverse('news:detail', args=news_id)
    url_to_comments = f'{news_url}#comments'
    return url_to_comments
