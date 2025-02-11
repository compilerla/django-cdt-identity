class Routes:
    def route(route_fragment: str):
        return f"cdt:{route_fragment}"

    authorize = "authorize"
    cancel = "cancel"
    login = "login"
    logout = "logout"
    post_logout = "post_logout"
    verify_fail = "verify_fail"
    verify_success = "verify_success"

    route_authorize = route(authorize)
    route_cancel = route(cancel)
    route_login = route(login)
    route_logout = route(logout)
    route_post_logout = route(post_logout)
    route_verify_fail = route(verify_fail)
    route_verify_success = route(verify_success)
