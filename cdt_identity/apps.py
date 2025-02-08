"""
Identity proofing and claims verification from the California Department of Techonology Identity Gateway.
"""

from django.apps import AppConfig


class CDTIdentityAppConfig(AppConfig):
    name = "cdt_identity"
    verbose_name = "CDT Identity Gateway"
