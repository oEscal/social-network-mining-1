import pytest
from random import choice
from api.views import policies
from mixer.backend.django import mixer
from api.tests.utils import *
from api.models import Policy
from django.test import RequestFactory
from django.urls import reverse
from api.serializers import Policy as Policy_serializer
from api.enums import Policy as Enum_policy


@pytest.fixture(scope='module')
def factory():
    return RequestFactory()


@pytest.fixture
def policy(db):
    return mixer.blend(Policy, tags=["PSD", "PS"], bots=[1, 2], id=1,
                       API_type=choice([x[0] for x in Enum_policy.api_types()]),
                       filter=choice([x[0] for x in Enum_policy.api_filter()]))


@pytest.fixture
def policy_twitter(db):
    return mixer.blend(Policy, tags=["PSD", "PS"], bots=[1, 2], id=1,
                       API_type="TWITTER", filter=choice([x[0] for x in Enum_policy.api_filter()]))


@pytest.fixture
def policy_instagram(db):
    return mixer.blend(Policy, tags=["PSD", "PS"], bots=[1, 2], id=1,
                       API_type="INSTAGRAM", filter=choice([x[0] for x in Enum_policy.api_filter()]))


def test_successful_policies_request(factory, policy):
    path = reverse('policies')
    request = factory.get(path)
    response = policies.policies(request)
    assert is_response_successful(response)


def test_unsuccessfully_policies_request(factory, db):
    path = reverse('policies')
    request = factory.get(path)
    response = policies.policies(request)
    assert is_response_empty(response)


def test_successful_policy_request(factory, policy):
    path = reverse('policy', kwargs={'id': 1})
    request = factory.get(path)
    response = policies.policy(request, id=1)
    assert is_response_successful(response)


def test_unsuccessfully_policy_request(factory, db):
    path = reverse('policy', kwargs={'id': 1})
    request = factory.get(path)
    response = policies.policy(request, id=1)
    assert is_response_unsuccessful(response)


def test_successful_bot_policies_request(factory, policy):
    path = reverse('bot_policies', kwargs={'id': 1})
    request = factory.get(path)
    response = policies.bot_policies(request, id=1)
    assert is_response_successful(response)


def test_unsuccessfully_bot_policies_request(factory, db):
    path = reverse('bot_policies', kwargs={'id': 1})
    request = factory.get(path)
    response = policies.bot_policies(request, id=1)
    assert is_response_empty(response)


def test_successful_add_policy_request(factory, policy):
    path = reverse('add_policy')
    data = Policy_serializer(policy).data
    data.pop('id', None)
    request = factory.post(path, data, content_type='application/json')
    response = policies.add_policy(request)
    assert is_response_successful(response)


def test_unsuccessfully_add_policy_request(factory, db):
    path = reverse('add_policy')
    request = factory.post(path, content_type='application/json')
    response = policies.add_policy(request)
    assert is_response_unsuccessful(response)


def test_successful_remove_policy_request(factory, policy):
    path = reverse('remove_policy', kwargs={'id': 1})
    request = factory.delete(path)
    response = policies.remove_policy(request, id=1)
    assert is_response_successful(response)


def test_unsuccessfully_remove_policy_request(factory, db):
    path = reverse('remove_policy', kwargs={'id': 1})
    request = factory.delete(path)
    response = policies.remove_policy(request, id=1)
    assert is_response_unsuccessful(response)


def test_successful_update_policy_request(factory, policy):
    path = reverse('update_policy', kwargs={'id': 1})
    request = factory.put(path, {'name': 'bot_1'}, content_type='application/json')
    response = policies.update_policy(request, id=1)
    assert is_response_successful(response)


def test_unsuccessfully_update_policy_request(factory, db):
    path = reverse('update_policy', kwargs={'id': 1})
    request = factory.put(path)
    response = policies.update_policy(request, id=1)
    assert is_response_unsuccessful(response)


def test_successful_instagram__policies_request(factory, policy_instagram):
    path = reverse('instagram_policies')
    request = factory.get(path)
    response = policies.instagram_policies(request)
    assert is_response_successful(response)


def test_successful_twitter__policies_request(factory, policy_twitter):
    path = reverse('twitter_policies')
    request = factory.get(path)
    response = policies.twitter_policies(request)
    assert is_response_successful(response)


def test_unsuccessfully_instagram__policies_request(factory, db):
    path = reverse('instagram_policies')
    request = factory.get(path)
    response = policies.instagram_policies(request)
    assert is_response_empty(response)


def test_unsuccessfully_twitter__policies_request(factory, db):
    path = reverse('twitter_policies')
    request = factory.get(path)
    response = policies.twitter_policies(request)
    assert is_response_empty(response)