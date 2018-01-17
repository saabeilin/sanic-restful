Gotta simplify your REST APIs creation!
=======================================

Sanic's built-in `HTTPMethodView` is a useful thing, but sometimes one wants more sugar.

Whay not? 

## Usage example


```python
import logging

from sanic import Sanic

from sanic_restful import Api, ApiEndpoint

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
```

And let's try it:

```bash
$ http POST http://localhost:8000/v0.9/todos/1
HTTP/1.1 201 Created
Access-Control-Allow-Credentials: true
Access-Control-Allow-Headers: X-Requested-With,X-Prototype-Version,Content-Type,Cache-Control,Pragma,Origin,Cookie
Access-Control-Allow-Methods: POST, PUT, PATCH, DELETE, OPTIONS, GET
Access-Control-Allow-Origin: *
Access-Control-Max-Age: 3600
Connection: keep-alive
Content-Length: 10
Content-Type: application/json
Keep-Alive: 5

{
    "id": "1"
}
```


-----
