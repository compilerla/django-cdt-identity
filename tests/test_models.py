import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from cdt_identity.models import ClientConfig


@pytest.fixture
def config_data():
    return {
        "client_name": "test-client",
        "client_id_secret_name": "test-secret-name",
        "authority": "https://auth.example.com",
        "scheme": "bearer",
    }


@pytest.mark.django_db
def test_create_client_config(config_data):
    client = ClientConfig.objects.create(**config_data)

    assert client.client_name == config_data["client_name"]
    assert client.authority == config_data["authority"]
    assert client.scheme == config_data["scheme"]


@pytest.mark.django_db
def test_client_name_unique(config_data):
    ClientConfig.objects.create(**config_data)

    with pytest.raises(IntegrityError):
        ClientConfig.objects.create(**config_data)


@pytest.mark.django_db
def test_client_id_property(config_data, mocker):
    mock_get_secret = mocker.patch("cdt_identity.models.KeyVaultField")
    mock_get_secret.secret_value.return_value = "client-123"

    client = ClientConfig.objects.create(**config_data)
    assert client.client_id == "client-123"
    mock_get_secret.assert_called_once_with(config_data["client_id_secret_name"])


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
