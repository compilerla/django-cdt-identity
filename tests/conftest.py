from authlib.integrations.django_client import OAuth

import pytest
from pytest_socket import disable_socket


def pytest_runtest_setup():
    disable_socket()


@pytest.fixture
def mock_oauth_registry(mocker):
    return mocker.Mock(spec=OAuth)
