from django.contrib import admin

from . import models


@admin.register(models.ClientConfig)
class ClientConfigAdmin(admin.ModelAdmin):
    list_display = ("client_name", "authority", "scheme")
