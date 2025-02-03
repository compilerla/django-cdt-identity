"""
Implements OpenID Connect (OIDC) for identity proofing and claims verification.

https://www.microsoft.com/en-us/security/business/security-101/what-is-openid-connect-oidc
"""

from django.apps import AppConfig


class OIDCAppConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "oidc_identity"
    verbose_name = "OpenID Connect Identity"
