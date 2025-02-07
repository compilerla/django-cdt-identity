from django.db import models

from keyvault_field.fields import KeyVaultField


class ClientConfig(models.Model):
    """OIDC Client configuration."""

    class Meta:
        verbose_name = "OIDC Client"

    id = models.AutoField(primary_key=True)
    client_name = models.SlugField(
        help_text="The name of this OIDC client",
        unique=True,
    )
    client_id_secret_name = KeyVaultField(help_text="The name of the secret containing the client ID for this OIDC client")
    authority = models.CharField(
        help_text="The fully qualified HTTPS domain name for an OIDC authority server",
        max_length=100,
    )
    scheme = models.CharField(
        help_text="The authentication scheme for the authority server",
        max_length=100,
    )

    @property
    def client_id(self):
        secret_name_field = self._meta.get_field("client_id_secret_name")
        return secret_name_field.secret_value(self)

    def __str__(self):
        return self.client_name
