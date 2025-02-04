from oidc_identity import urls, views


def test_endpoints_view():
    for endpoint in urls.endpoints_view:
        assert hasattr(views, endpoint)
