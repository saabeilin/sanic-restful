from http import HTTPMethod

from sanic_simple_restful import ApiEndpoint


def test_routes_1():
    api = ApiEndpoint()
    assert api._get_routes() == {"": [HTTPMethod.OPTIONS]}
