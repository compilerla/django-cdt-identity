import logging
import os
import re

from django.core.validators import RegexValidator

logger = logging.getLogger(__name__)


class SecretNameValidator(RegexValidator):
    """RegexValidator that validates a secret name.

    Currently enforces the following rules:

    * The value must be between 1 and 127 characters long.
    * Secret names can only contain alphanumeric characters and dashes.

    Read more about Django validators:
    https://docs.djangoproject.com/en/5.0/ref/validators/#module-django.core.validators
    """

    def __init__(self, *args, **kwargs):
        kwargs["regex"] = re.compile(r"^[-a-zA-Z0-9]{1,127}$", re.ASCII)
        kwargs["message"] = (
            "Enter a valid secret name of between 1-127 alphanumeric ASCII characters and the hyphen character only."
        )
        super().__init__(*args, **kwargs)


NAME_VALIDATOR = SecretNameValidator()


def get_secret_by_name(secret_name):
    """
    Read a value from the secret store, or the environment by default.
    """
    NAME_VALIDATOR(secret_name)

    logger.debug("Reading secret values from the default store (env vars).")
    # environment variable names cannot contain the hyphen character
    # assume the variable name is the same but with underscores instead
    env_secret_name = secret_name.replace("-", "_")
    secret_value = os.environ.get(env_secret_name)
    # replace literal newlines with the actual newline character
    # to support local environment variable values that span multiple lines (e.g. PEM keys/certs)
    # because the VS Code Python extension doesn't support multiline environment variables
    # https://code.visualstudio.com/docs/python/environments#_environment-variables
    return secret_value.replace("\\n", "\n")
