from django.urls import path
from django.views.generic import TemplateView

from .routes import Routes


app_name = "oidc"

endpoints_template = [
    Routes.cancel,
    Routes.post_logout,
    Routes.success,
]

urlpatterns = []

for endpoint in endpoints_template:
    # simple template-only view
    urlpatterns.append(path(endpoint, TemplateView.as_view(template_name=f"oidc_identity/{endpoint}.html"), name=endpoint))
