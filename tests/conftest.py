from authlib.integrations.django_client import OAuth, DjangoOAuth2App

from django.contrib.sessions.middleware import SessionMiddleware

import pytest
from pytest_socket import disable_socket


def pytest_runtest_setup():
    disable_socket()


@pytest.fixture
def mock_oauth_registry(mocker):
    return mocker.Mock(spec=OAuth)


@pytest.fixture
def mock_oauth_client(mocker):
    return mocker.Mock(spec=DjangoOAuth2App)


@pytest.fixture
def mock_request(rf):
    """
    Fixture creates and initializes a new Django request object similar to a real application request.
    """
    # create a request for a path
    request = rf.get("/some/arbitrary/path")

    # https://stackoverflow.com/a/55530933/358804
    middleware = [SessionMiddleware(lambda x: x)]
    for m in middleware:
        m.process_request(request)

    request.session.save()
    return request
