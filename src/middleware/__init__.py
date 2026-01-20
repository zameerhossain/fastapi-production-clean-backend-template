from .error_handler_middleware import error_handler_middleware
from .wrap_response_middleware import wrap_response_middleware


class Middleware:
    error_handler = staticmethod(error_handler_middleware)
    wrap_response = staticmethod(wrap_response_middleware)
