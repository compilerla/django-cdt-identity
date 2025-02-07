"""
OpenID Connect (OIDC) client for identity proofing and claims verification from
the California Department of Techonology Identity Gateway.

https://www.microsoft.com/en-us/security/business/security-101/what-is-openid-connect-oidc
"""

from django.apps import AppConfig


class OIDCAppConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "cdt_identity"
    verbose_name = "CDT Identity"
