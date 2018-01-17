import inspect
import logging
import typing
from functools import wraps

import sanic
from sanic import response
from sanic.constants import HTTP_METHODS
from sanic.views import HTTPMethodView

logger = logging.getLogger(__file__)


class ApiEndpoint(HTTPMethodView):
    endpoint: str
    endpoints: typing.List[str] = []

    async def options(self, request, *args, **kwargs):
        """
        Returns a default empty response for OPTIONS method,
        needed for CORS pre-flight.
        Do not forget to add CORS headers globally!
        """
        return response.raw(b'')

    #
    # def dispatch_request(self, request, *args, **kwargs):
    #     return response.json(super(ApiResource).dispatch_request(request, *args, **kwargs))


def unpack(value):
    """Return a three tuple of data, code, and headers"""
    if not isinstance(value, tuple):
        return value, 200, {}

    try:
        data, code, headers = value
        return data, code, headers
    except ValueError:
        pass

    try:
        data, code = value
        return data, code, {}
    except ValueError:
        pass

    return value, 200, {}


class Api(object):
    def __init__(self,
                 app: sanic.Sanic,
                 endpoints: typing.List[ApiEndpoint],
                 prefix='', decorators=None):
        self.urls = {}
        self.prefix = prefix
        self.decorators = decorators or []
        self.endpoints = set(endpoints)
        self.resources = []
        self.app = app

        # TODO: late initialization?
        for endpoints in self.endpoints:
            self.add_endpoints(endpoints)

    def add_endpoints(self, api_endpoint: ApiEndpoint):
        view_instance = self.output(api_endpoint.as_view())
        if api_endpoint.endpoints:
            for endpoint in api_endpoint.endpoints:
                self.app.add_route(view_instance, self.prefix + endpoint)
        else:
            self.app.add_route(view_instance, self.prefix + api_endpoint.endpoint)

    def add_endpoints_(self, api_endpoint: ApiEndpoint):
        for method in HTTP_METHODS:

            method_handler = getattr(api_endpoint, method.lower(), None)
            if not method_handler:
                continue

            method_signature = inspect.signature(method_handler)
            method_urls = []
            url = ''
            for p in method_signature.parameters.values():
                if p.name in ('self', 'request'):
                    continue
                if p.kind != inspect._ParameterKind.POSITIONAL_OR_KEYWORD:
                    break
                if p.default != inspect._empty:
                    method_urls.append(url)
                var = f'/<{p.name}:{p.annotation.__name__}>' if p.annotation != inspect._empty else f'/<{p.name}>'
                url += var
            method_urls.append(url)

            logger.warning(method_urls)

            view_instance = self.output(api_endpoint.as_view())
            # for endpoint in resource.endpoints:
            #     self.app.add_route(view_instance, self.prefix + endpoint)
            for endpoint in method_urls:
                logger.warning(self.prefix + api_endpoint.endpoint + endpoint)
                self.app.route(
                    self.prefix + api_endpoint.endpoint + endpoint,
                    methods=frozenset({method}))(view_instance)
                # TODO - register same for OPTIONS?

    def output(self, resource):
        """
        Wraps a resource for cases where the resource does not directly return a response object
        :param resource: The resource as a Sanic view function
        """

        @wraps(resource)
        async def wrapper(*args, **kwargs):
            resp = await resource(*args, **kwargs)
            if isinstance(resp, response.HTTPResponse):
                return resp
            data, code, headers = unpack(resp)
            return response.json(data, code, headers=headers)

        if hasattr(resource, 'view_class'):
            wrapper.view_class = resource.view_class

        return wrapper
