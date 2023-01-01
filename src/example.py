import logging

from sanic import Sanic

from sanic_simple_restful import Api, ApiEndpoint

logger = logging.getLogger(__name__)

app = Sanic()


@app.middleware('response')
async def cors_headers(request, response):
    """
    Add CORS headers to all responses, including errors.
    """
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'POST, PUT, PATCH, DELETE, OPTIONS, GET'
    response.headers['Access-Control-Allow-Headers'] = "X-Requested-With,X-Prototype-Version," \
                                                       "Content-Type,Cache-Control,Pragma,Origin,Cookie"
    response.headers['Access-Control-Max-Age'] = '3600'


class TodoResource(ApiEndpoint):
    # method_decorators = [auth.auth_required]
    endpoint = 'todos/<todo_id>'

    async def get(self, request, todo_id):
        return {'id': todo_id}

    async def post(self, request, todo_id):
        return {'id': todo_id}, 201


api = Api(app, [TodoResource], '/v0.9/')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
