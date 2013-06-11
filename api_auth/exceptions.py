class AccessDenied(Exception):
    """
    Used to have the API views return a 403
    """
    pass


class ServiceUnavailable(Exception):
    """
    Used to have the API views return a 503 when key components are missing
    """
    pass


class PageNotFound(Exception):
    """
    Avoid Django's default Http404 (which attempts to use a template)
    """
    pass