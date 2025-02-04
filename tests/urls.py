from django.urls import include, path


urlpatterns = [path("", include("oidc_identity.urls"))]
