from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("django-oidc-identity")
except PackageNotFoundError:
    # package is not installed
    pass


VERSION = __version__
