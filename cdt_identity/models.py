from django.db import models


class ClientConfig(models.Model):
    """Identity Gateway Client configuration."""

    class Meta:
        verbose_name = "Identity Gateway Client"

    id = models.AutoField(primary_key=True)
    client_name = models.SlugField(
        help_text="The name of this Identity Gateway client",
        unique=True,
    )
    client_id = models.CharField(
        help_text="The client ID for this Identity Gateway client",
        max_length=100,
    )
    authority = models.CharField(
        help_text="The fully qualified HTTPS domain name for an Identity Gateway authority server",
        max_length=100,
    )
    scheme = models.CharField(
        help_text="The authentication scheme for the Identity Gateway authority server",
        max_length=100,
    )

    def __str__(self):
        return self.client_name
