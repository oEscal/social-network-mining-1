import pytest
from django.test import RequestFactory
from django.urls import reverse
from api.models import User, Tweet
from api.views import users
from mixer.backend.django import mixer
from api.tests.utils import *
from api import neo4j


@pytest.fixture(scope='module')
def factory():
	return RequestFactory()


@pytest.fixture
def users_list(db):
	return mixer.cycle(5).blend(User)


@pytest.fixture
def user(db):
	return mixer.blend(User, id=1, user_id=1)


@pytest.fixture
def tweet(db):
	return mixer.blend(Tweet, user=1)


@catch_exception
def test_successful_twitter_users_request(error_catcher, factory, users_list):
	path = reverse('twitter_users')
	request = factory.get(path)
	response = users.twitter_users(request)
	assert is_response_successful(response)


@catch_exception
def test_unsuccessfully_twitter_users_request(error_catcher, factory, db):
	path = reverse('twitter_users')
	request = factory.get(path)
	response = users.twitter_users(request)
	assert is_response_unsuccessful(response)


@catch_exception
def test_successful_twitter_user_request(error_catcher, factory, user):
	path = reverse('twitter_user', kwargs={'id': 1})
	request = factory.get(path)
	response = users.twitter_user(request, id=1)
	assert is_response_successful(response)


@catch_exception
def test_unsuccessfully_twitter_user_request(error_catcher, factory, db):
	path = reverse('twitter_user', kwargs={'id': 1})
	request = factory.get(path)
	response = users.twitter_user(request, id=1)
	assert is_response_unsuccessful(response)


@catch_exception
def test_successful_twitter_user_tweets_request(error_catcher, factory, tweet):
	path = reverse('twitter_user_tweets', kwargs={'id': 1})
	request = factory.get(path)
	response = users.twitter_user_tweets(request, id=1)
	assert is_response_successful(response)


@catch_exception
def test_unsuccessfully_twitter_user_tweets_request(error_catcher, factory, db):
	path = reverse('twitter_user_tweets', kwargs={'id': 1})
	request = factory.get(path)
	response = users.twitter_user_tweets(request, id=1)
	assert is_response_unsuccessful(response)
