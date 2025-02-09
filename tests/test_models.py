import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from cdt_identity.models import ClientConfig


@pytest.fixture
def config_data():
    return {
        "client_name": "test-client",
        "client_id": "test-client-id",
        "authority": "https://auth.example.com",
        "scheme": "bearer",
    }


@pytest.mark.django_db
def test_create_client_config(config_data):
    client = ClientConfig.objects.create(**config_data)

    assert client.client_name == config_data["client_name"]
    assert client.client_id == config_data["client_id"]
    assert client.authority == config_data["authority"]
    assert client.scheme == config_data["scheme"]


@pytest.mark.django_db
def test_client_name_unique(config_data):
    ClientConfig.objects.create(**config_data)

    with pytest.raises(IntegrityError):
        ClientConfig.objects.create(**config_data)


@pytest.mark.django_db
def test_str_representation(config_data):
    client = ClientConfig.objects.create(**config_data)
    assert str(client) == config_data["client_name"]


@pytest.mark.django_db
def test_invalid_client_name(config_data):
    config_data["client_name"] = "invalid with spaces"
    with pytest.raises(ValidationError):
        client = ClientConfig(**config_data)
        client.full_clean()


@pytest.mark.django_db
def test_authority_max_length(config_data):
    config_data["authority"] = "a" * 101
    with pytest.raises(ValidationError):
        client = ClientConfig(**config_data)
        client.full_clean()


@pytest.mark.django_db
def test_scheme_max_length(config_data):
    config_data["scheme"] = "s" * 101
    with pytest.raises(ValidationError):
        client = ClientConfig(**config_data)
        client.full_clean()
