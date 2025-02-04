class Routes:
    def route(route_fragment: str):
        return f"oidc:{route_fragment}"

    cancel = "cancel"
    post_logout = "post_logout"
    success = "success"

    route_cancel = route(cancel)
    route_post_logout = route(post_logout)
    route_success = route(success)
