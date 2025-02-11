from django.contrib import admin

from .models import IdentityGatewayConfig


@admin.register(IdentityGatewayConfig)
class IdentityGatewayConfigAdmin(admin.ModelAdmin):
    list_display = ("client_name", "authority", "scheme")
