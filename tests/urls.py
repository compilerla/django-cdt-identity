from django.urls import include, path

urlpatterns = [path("", include("cdt_identity.urls"))]
