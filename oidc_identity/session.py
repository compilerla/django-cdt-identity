from django.http import HttpRequest

from .models import ClientConfig


class Session:

    def __init__(
        self,
        request: HttpRequest,
        authorize_fail: str = None,
        authorize_sucess: str = None,
        scopes: str = None,
        scheme: str = None,
        reset: bool = False,
    ):
        """Initialize a new OIDC session wrapper for this request.

        Args:
            authorize_fail (str): A Django route string like `app:route` to redirect to upon authorization failure.

            authorize_success (str): A Django route string like `app:route` to redirect to upon authorization success.

            scopes (str): Additional scopes requested during login.

            scheme (str): Override the scheme this OIDC connection uses.

            reset (bool): True to reset this request's OIDC information.
        """

        self.request = request
        self.session = request.session

        if reset:
            self.oidc_eligibility_claims = ""
            self.oidc_expected_claims = ""
            self.oidc_scheme = ""
            self.oidc_scopes = ""
            self.clear_oidc_token()
        if authorize_fail:
            self.oidc_authorize_fail = authorize_fail
        if authorize_sucess:
            self.oidc_authorize_success = authorize_sucess
        if scheme:
            self.oidc_scheme = scheme
        if scopes:
            self.oidc_scopes = scopes

    @property
    def oidc_authorize_fail(self) -> str:
        return self.session.get("oidc_authorize_fail", "")

    @oidc_authorize_fail.setter
    def oidc_authorize_fail(self, value: str) -> None:
        self.session["oidc_authorize_fail"] = value

    @property
    def oidc_authorize_success(self) -> str:
        return self.session.get("oidc_authorize_success", "")

    @oidc_authorize_success.setter
    def oidc_authorize_success(self, value: str) -> None:
        self.session["oidc_authorize_success"] = value

    @property
    def oidc_eligibility_claims(self) -> str:
        return self.session.get("oidc_eligibility_claims", "")

    @oidc_eligibility_claims.setter
    def oidc_eligibility_claims(self, value: str) -> None:
        self.session["oidc_eligibility_claims"] = value

    @property
    def oidc_expected_claims(self) -> str:
        return self.session.get("oidc_expected_claims", "")

    @oidc_expected_claims.setter
    def oidc_expected_claims(self, value: str) -> None:
        self.session["oidc_expected_claims"] = value

    @property
    def oidc_verified_claims(self) -> dict:
        return self.session.get("oidc_verified_claims", {})

    @oidc_verified_claims.setter
    def oidc_verified_claims(self, value: dict) -> None:
        self.session["oidc_verified_claims"] = value

    @property
    def oidc_config(self) -> ClientConfig:
        val = self.session.get("oidc_config")
        return ClientConfig.objects.filter(id=val).first()

    @oidc_config.setter
    def oidc_config(self, value: ClientConfig) -> None:
        self.session["oidc_config"] = value.id

    @property
    def oidc_scheme(self) -> str:
        return self.session.get("oidc_scheme", "")

    @oidc_scheme.setter
    def oidc_scheme(self, value: str) -> None:
        self.session["oidc_scheme"] = value

    @property
    def oidc_scopes(self) -> str:
        return self.session.get("oidc_scopes", "")

    @oidc_scopes.setter
    def oidc_scopes(self, value: str) -> None:
        self.session["oidc_scopes"] = value

    @property
    def oidc_token(self) -> str:
        return self.session.get("oidc_token", "")

    @oidc_token.setter
    def oidc_token(self, value: str) -> None:
        self.session["oidc_token"] = value

    def clear_oidc_token(self):
        """Reset the session claims and token."""
        self.oidc_token = ""
        self.oidc_verified_claims = {}

    def has_oidc_token(self):
        """Return True if this session has an OIDC token. False otherwise."""
        return bool(self.oidc_token)

    def has_oidc_verified_claims(self):
        """Return True if this session has verified claims. False otherwise."""
        return bool(self.oidc_verified_claims)
