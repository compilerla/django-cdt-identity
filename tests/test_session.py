import pytest
from django.http import HttpRequest

from cdt_identity.models import ClientConfig
from cdt_identity.session import Session


@pytest.fixture
def mock_request(mocker):
    request = mocker.MagicMock(spec=HttpRequest)
    request.session = {"session_id": 123}
    return request


@pytest.fixture
def mock_config(mocker):
    return mocker.MagicMock(spec=ClientConfig)


@pytest.mark.django_db
def test_session_init(mock_request):
    session = Session(mock_request, "auth:fail", "auth:success", "scopes", "scheme")
    assert session.request == mock_request
    assert session.session == mock_request.session
    assert session.oidc_authorize_fail == "auth:fail"
    assert session.oidc_authorize_success == "auth:success"
    assert session.oidc_scheme == "scheme"
    assert session.oidc_scopes == "scopes"


def test_session_init_with_reset(mock_request):
    s1 = Session(mock_request, "auth:fail", "auth:success", "scopes", "scheme")
    s1.oidc_expected_claims = "claim1"
    s1.oidc_eligibility_claims = "claim2"
    s1.oidc_verified_claims = {"claim2": True}
    s1.oidc_token = "test_token"

    s2 = Session(mock_request, reset=True)

    assert s1.oidc_scheme == s2.oidc_scheme == ""
    assert s1.oidc_scopes == s2.oidc_scopes == ""
    assert s1.oidc_expected_claims == s2.oidc_expected_claims == ""
    assert s1.oidc_eligibility_claims == s2.oidc_eligibility_claims == ""
    assert s1.has_oidc_token() is s2.has_oidc_token() is False
    assert s1.has_oidc_verified_claims() is s2.has_oidc_verified_claims() is False


def test_session_property_string(mock_request):
    session = Session(mock_request)
    session.oidc_token = "test_token"

    assert session.oidc_token == "test_token"
    assert mock_request.session["oidc_token"] == "test_token"


def test_session_config(mocker, mock_config, mock_request):
    mock_config.id = "123"

    session = Session(mock_request)
    session.oidc_config = mock_config
    assert mock_request.session["oidc_config"] == "123"

    mock_filter = mocker.patch.object(ClientConfig.objects, "filter")
    mock_filter.return_value.first.return_value = mock_config

    assert session.oidc_config == mock_config
    mock_filter.assert_called_once_with(id="123")


def test_clear_oidc_token(mock_request):
    session = Session(mock_request)
    session.oidc_token = "test_token"
    session.oidc_verified_claims = {"claim": "verified"}

    session.clear_oidc_token()

    assert session.oidc_token == ""
    assert not session.has_oidc_token()

    assert session.oidc_verified_claims == {}
    assert not session.has_oidc_verified_claims()


def test_has_oidc_token(mock_request):
    session = Session(mock_request)
    assert not session.has_oidc_token()

    session.oidc_token = "test_token"
    assert session.has_oidc_token()
