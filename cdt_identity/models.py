from django.db import models

from .secrets import NAME_VALIDATOR, get_secret_by_name


class SecretNameField(models.SlugField):
    """Field that stores the name of a secret held in a secret store.

    The secret value itself MUST NEVER be stored in this field.
    """

    description = """Field that stores the name of a secret held in a secret store.

    Secret names must be between 1-127 alphanumeric ASCII characters or hyphen characters.

    The secret value itself MUST NEVER be stored in this field.
    """

    def __init__(self, *args, **kwargs):
        kwargs["validators"] = [NAME_VALIDATOR]
        # although the validator also checks for a max length of 127
        # this setting enforces the length at the database column level as well
        kwargs["max_length"] = 127
        # the default is False, but this is more explicit
        kwargs["allow_unicode"] = False
        super().__init__(*args, **kwargs)

    def secret_value(self, instance):
        """Get the secret value from the secret store."""
        secret_name = getattr(instance, self.attname)
        return get_secret_by_name(secret_name)


class ClientConfig(models.Model):
    """OIDC Client configuration."""

    class Meta:
        verbose_name = "OIDC Client"

    id = models.AutoField(primary_key=True)
    client_name = models.SlugField(
        help_text="The name of this OIDC client",
        unique=True,
    )
    client_id_secret_name = SecretNameField(help_text="The name of the secret containing the client ID for this OIDC client")
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
