import logging

from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse

from . import redirects
from .claims import ClaimsParser
from .client import create_client
from .client import oauth as registry
from .routes import Routes
from .session import Session

logger = logging.getLogger(__name__)


def _client_or_error_redirect(request: HttpRequest):
    """Calls `cdt_identity.client.create_client()`.

    If a client is created successfully, return it; otherwise, raise an appropriate Exception.
    """
    client = None
    session = Session(request)

    config = session.oidc_config
    if not config:
        raise Exception("No oauth_config in session")

    scheme = session.oidc_scheme
    scopes = session.oidc_scopes
    client = create_client(registry, config, scopes, scheme)
    if not client:
        raise Exception(f"oauth_client not registered: {config.client_name}")

    return client


def authorize(request: HttpRequest):
    """View implementing OIDC token authorization."""
    logger.debug(Routes.route_authorize)

    session = Session(request)
    client_result = _client_or_error_redirect(request)

    if hasattr(client_result, "authorize_access_token"):
        # this looks like an oauth_client since it has the method we need
        oauth_client = client_result
    else:
        # this does not look like an oauth_client, it's an error redirect
        return client_result

    logger.debug("Attempting to authorize OIDC access token")
    token = None
    exception = None

    try:
        token = oauth_client.authorize_access_token(request)
    except Exception as ex:
        exception = ex

    if token is None and not exception:
        logger.warning("Could not authorize OIDC access token")
        exception = Exception("authorize_access_token returned None")

    if exception:
        raise exception

    logger.debug("OIDC access token authorized")

    # Store the id_token in the user's session. This is the minimal amount of information needed later to log the user out.
    session.oidc_token = token["id_token"]

    # Process the returned claims
    processed_claims = []
    expected_claims = [claim for claim in session.oidc_expected_claims.split(" ") if claim]
    if expected_claims:
        userinfo = token.get("userinfo", {})
        processed_claims = ClaimsParser.parse(userinfo, expected_claims)
    # if we found the eligibility claim
    eligibility_claim = session.oidc_eligibility_claims
    if eligibility_claim and eligibility_claim in processed_claims:
        # store and redirect to success
        session.oidc_verified_claims = processed_claims.claims
        return redirect(session.oidc_claims_authorize_success)
    # else redirect to failure
    if processed_claims and processed_claims.errors:
        logger.error(processed_claims.errors)
    return redirect(session.oidc_claims_authorize_fail)


def login(request: HttpRequest):
    """View implementing OIDC authorize_redirect."""
    logger.debug(Routes.route_login)

    oauth_client_result = _client_or_error_redirect(request)

    if hasattr(oauth_client_result, "authorize_redirect"):
        # this looks like an oauth_client since it has the method we need
        oauth_client = oauth_client_result
    else:
        # this does not look like an oauth_client, it's an error redirect
        return oauth_client_result

    route = reverse(Routes.route_authorize)
    redirect_uri = redirects.generate_redirect_uri(request, route)

    logger.debug(f"OAuth authorize_redirect with redirect_uri: {redirect_uri}")

    exception = None
    result = None

    try:
        result = oauth_client.authorize_redirect(request, redirect_uri)
    except Exception as ex:
        exception = ex

    if result and result.status_code >= 400:
        exception = Exception(f"authorize_redirect error response [{result.status_code}]: {result.content.decode()}")
    elif result is None and exception is None:
        exception = Exception("authorize_redirect returned None")

    if exception:
        raise exception

    return result


def logout(request: HttpRequest):
    """View handler for OIDC sign out."""
    logger.debug(Routes.route_logout)

    session = Session(request)
    oauth_client_result = _client_or_error_redirect(request)

    if hasattr(oauth_client_result, "load_server_metadata"):
        # this looks like an oauth_client since it has the method we need
        # (called in redirects.deauthorize_redirect)
        oauth_client = oauth_client_result
    else:
        # this does not look like an oauth_client, it's an error redirect
        return oauth_client_result

    # overwrite the session token, the user is signed out of the app
    token = session.oidc_token
    session.clear_oidc_token()

    route = reverse(Routes.route_post_logout)
    redirect_uri = redirects.generate_redirect_uri(request, route)

    logger.debug(f"OAuth end_session_endpoint with redirect_uri: {redirect_uri}")

    # send the user through the end_session_endpoint, redirecting back to
    # the post_logout route
    return redirects.deauthorize_redirect(request, oauth_client, token, redirect_uri)
    return redirects.deauthorize_redirect(request, oauth_client, token, redirect_uri)
