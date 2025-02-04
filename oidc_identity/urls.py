from django.urls import path
from django.views.generic import TemplateView

from . import views
from .routes import Routes


app_name = "oidc"

endpoints_template = [
    Routes.cancel,
    Routes.post_logout,
    Routes.success,
]
endpoints_view = [
    Routes.authorize,
    Routes.login,
    Routes.logout,
]

urlpatterns = []

for endpoint in endpoints_template:
    # simple template-only view
    urlpatterns.append(path(endpoint, TemplateView.as_view(template_name=f"oidc_identity/{endpoint}.html"), name=endpoint))
for endpoint in endpoints_view:
    # view functions
    urlpatterns.append(path(endpoint, getattr(views, endpoint), name=endpoint))
