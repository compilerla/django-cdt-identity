import re

import pytest
from django.http import HttpResponse

from cdt_identity.routes import Routes
from cdt_identity.session import Session
from cdt_identity.views import _client_or_error_redirect, authorize, login, logout


@pytest.fixture
def mock_session(mocker):
    session = mocker.Mock(spec=Session)
    mocker.patch("cdt_identity.views.Session", return_value=session)
    return session


@pytest.fixture
def mock_oauth_create_client(mocker, mock_oauth_client):
    return mocker.patch("cdt_identity.views.create_client", return_value=mock_oauth_client)


@pytest.fixture
def mock_client_or_error_redirect(mocker, mock_oauth_client):
    return mocker.patch("cdt_identity.views._client_or_error_redirect", return_value=mock_oauth_client)


@pytest.mark.django_db
def test_client_or_error_redirect_no_config(mock_request, mock_oauth_create_client):
    with pytest.raises(Exception, match="No oauth_config in session"):
        _client_or_error_redirect(mock_request)

    mock_oauth_create_client.assert_not_called()


@pytest.mark.django_db
def test_client_or_error_redirect_no_client(mocker, mock_oauth_create_client, mock_request, mock_session):
    mock_session.oidc_config = mocker.Mock(client_name="name")
    mock_session.oidc_scheme = "scheme"
    mock_session.oidc_scopes = "scopes"
    mock_oauth_create_client.return_value = None

    with pytest.raises(Exception, match="oauth_client not registered: name"):
        _client_or_error_redirect(mock_request)


@pytest.mark.django_db
@pytest.mark.usefixtures("mock_oauth_create_client")
def test_client_or_error_redirect_client(mocker, mock_request, mock_session):
    mock_session.oidc_config = mocker.Mock(client_name="name")
    mock_session.oidc_scheme = "scheme"
    mock_session.oidc_scopes = "scopes"

    result = _client_or_error_redirect(mock_request)

    assert hasattr(result, "authorize_redirect")


@pytest.mark.django_db
@pytest.mark.usefixtures("mock_client_or_error_redirect")
def test_authorize_success(mocker, mock_oauth_client, mock_request, mock_session):
    mock_oauth_client.authorize_access_token.return_value = {
        "id_token": "test_token",
        "userinfo": {"claim1": "1", "claim2": "value", "claim3": "value"},
    }
    mock_session.oidc_expected_claims = "claim1 claim2"
    mock_session.oidc_eligibility_claims = "claim1"
    mock_session.oidc_claims_authorize_success = "/success"
    mock_redirect = mocker.patch("cdt_identity.views.redirect")

    authorize(mock_request)

    mock_redirect.assert_called_once_with("/success")
    assert mock_session.oidc_verified_claims == {"claim1": True, "claim2": "value"}


@pytest.mark.django_db
def test_authorize_no_client(mocker, mock_client_or_error_redirect, mock_request):
    error_redirect = mocker.Mock(spec=[])
    mock_client_or_error_redirect.return_value = error_redirect

    response = authorize(mock_request)

    assert response == error_redirect


@pytest.mark.django_db
@pytest.mark.usefixtures("mock_client_or_error_redirect")
def test_authorize_no_token(mock_oauth_client, mock_request):
    mock_oauth_client.authorize_access_token.return_value = None

    with pytest.raises(Exception, match="authorize_access_token returned None"):
        authorize(mock_request)


@pytest.mark.django_db
@pytest.mark.usefixtures("mock_client_or_error_redirect")
def test_authorize_token_exception(mock_oauth_client, mock_request):
    mock_oauth_client.authorize_access_token.side_effect = Exception("authorize token failed")

    with pytest.raises(Exception, match="authorize token failed"):
        authorize(mock_request)


@pytest.mark.django_db
@pytest.mark.usefixtures("mock_client_or_error_redirect")
def test_authorize_no_expected_claims(mocker, mock_oauth_client, mock_request, mock_session):
    mock_oauth_client.authorize_access_token.return_value = {
        "id_token": "test_token",
        "userinfo": {"claim1": "1", "claim2": "value", "claim3": "value"},
    }
    mock_session.oidc_expected_claims = ""
    mock_session.oidc_eligibility_claims = "claim1"
    mock_session.oidc_claims_authorize_fail = "/fail"
    mock_redirect = mocker.patch("cdt_identity.views.redirect")

    authorize(mock_request)

    mock_redirect.assert_called_once_with("/fail")


@pytest.mark.django_db
@pytest.mark.usefixtures("mock_client_or_error_redirect")
def test_authorize_no_token_claims(mocker, mock_oauth_client, mock_request, mock_session):
    mock_oauth_client.authorize_access_token.return_value = {
        "id_token": "test_token",
        "userinfo": {},
    }
    mock_session.oidc_expected_claims = "claim1 claim2"
    mock_session.oidc_eligibility_claims = "claim1"
    mock_session.oidc_claims_authorize_fail = "/fail"
    mock_redirect = mocker.patch("cdt_identity.views.redirect")

    authorize(mock_request)

    mock_redirect.assert_called_once_with("/fail")


@pytest.mark.django_db
@pytest.mark.usefixtures("mock_client_or_error_redirect")
def test_authorize_token_error_claims(mocker, mock_oauth_client, mock_request, mock_session):
    mock_oauth_client.authorize_access_token.return_value = {
        "id_token": "test_token",
        "userinfo": {"claim1": 5, "claim2": 10, "claim3": 100},
    }
    mock_session.oidc_expected_claims = "claim1 claim2"
    mock_session.oidc_eligibility_claims = "claim1"
    mock_session.oidc_claims_authorize_fail = "/fail"
    mock_redirect = mocker.patch("cdt_identity.views.redirect")

    authorize(mock_request)

    mock_redirect.assert_called_once_with("/fail")


@pytest.mark.django_db
@pytest.mark.usefixtures("mock_client_or_error_redirect")
def test_login_success(mocker, mock_oauth_client, mock_request):
    mock_oauth_client.authorize_redirect.return_value = HttpResponse(status=200)
    mock_reverse = mocker.patch("cdt_identity.views.reverse", return_value="authorize")

    response = login(mock_request)

    assert response.status_code == 200
    mock_reverse.assert_called_once_with(Routes.route_authorize)


@pytest.mark.django_db
@pytest.mark.usefixtures("mock_client_or_error_redirect")
def test_login_failure(mock_oauth_client, mock_request):
    mock_oauth_client.authorize_redirect.return_value = None

    with pytest.raises(Exception):
        login(mock_request)


@pytest.mark.django_db
def test_login_no_client(mocker, mock_client_or_error_redirect, mock_request):
    error_redirect = mocker.Mock(spec=[])
    mock_client_or_error_redirect.return_value = error_redirect

    response = login(mock_request)

    assert response == error_redirect


@pytest.mark.django_db
@pytest.mark.usefixtures("mock_client_or_error_redirect")
def test_login_authorize_redirect_exception(mock_oauth_client, mock_request):
    mock_oauth_client.authorize_redirect.side_effect = Exception("authorize_redirect")

    with pytest.raises(Exception, match="authorize_redirect"):
        login(mock_request)


@pytest.mark.django_db
@pytest.mark.usefixtures("mock_client_or_error_redirect")
@pytest.mark.parametrize(
    "status_code, content",
    [
        (400, "bad request"),
        (404, "not found"),
        (500, "server error"),
    ],
)
def test_login_authorize_redirect_error_response(mock_oauth_client, mock_request, status_code, content):
    mock_oauth_client.authorize_redirect.return_value = HttpResponse(content=content, status=status_code)

    with pytest.raises(Exception, match=re.escape(f"authorize_redirect error response [{status_code}]: {content}")):
        login(mock_request)


@pytest.mark.django_db
@pytest.mark.usefixtures("mock_client_or_error_redirect")
def test_logout(mocker, mock_request, mock_session):
    mock_redirects = mocker.patch("cdt_identity.views.redirects")
    mock_redirects.deauthorize_redirect.return_value = HttpResponse(status=200)
    mock_reverse = mocker.patch("cdt_identity.views.reverse", return_value="deauthorize")

    response = logout(mock_request)

    assert response.status_code == 200
    mock_redirects.deauthorize_redirect.assert_called_once()
    mock_reverse.assert_called_once_with(Routes.route_post_logout)
    mock_session.clear_oidc_token.assert_called_once()


@pytest.mark.django_db
@pytest.mark.usefixtures("mock_client_or_error_redirect")
def test_logout_no_client(mocker, mock_client_or_error_redirect, mock_request):
    error_redirect = mocker.Mock(spec=[])
    mock_client_or_error_redirect.return_value = error_redirect

    response = logout(mock_request)

    assert response == error_redirect
    assert response == error_redirect
