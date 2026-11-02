# Week 4: Advanced Web Application Development Technologies

> 🇬🇷 [Ελληνική έκδοση](README.md)

So far we have been writing **HTTP clients** (with `requests`). In this lab we move to the other side: we write **HTTP servers** and test them with the clients we already know how to build.

## Preparation

```bash
python3 -m venv flask_lab
source flask_lab/bin/activate        # macOS/Linux
# flask_lab\Scripts\activate.bat     # Windows (cmd)
# flask_lab\Scripts\Activate.ps1     # Windows (PowerShell)
pip install flask requests waitress
```

+ You will need **two terminals**: the server runs in the first one (and “occupies” it until `Ctrl+C`), the checks (curl / Python) run in the second. Activate the venv in both.
+ ⚠️ **macOS**: port 5000 is used by the _AirPlay Receiver_ (error `403` or "Address already in use"). Run Flask on another port, e.g. `flask --app app run --debug --port 5001`, and change the URLs in the checks accordingly.
+ In the Python checks, `BASE` is the address of your server:
  ```python
  BASE = 'http://127.0.0.1:5000'
  ```

---

## Exercise 0: A server without Flask (WSGI)

**Goal:** Run the WSGI application from the slides using only Python's standard library, and see what Flask does for us.

**Requirements:**
1. Save the code as `wsgi_app.py` and run it: `python wsgi_app.py`
2. Open http://127.0.0.1:8000/ in your browser, then http://127.0.0.1:8000/hello?name=Maria. What is printed in the server's terminal?
3. Find the keys `REQUEST_METHOD`, `PATH_INFO`, `QUERY_STRING` and `HTTP_USER_AGENT` in `environ`. What do they correspond to in the HTTP request?
4. Modify `application` so that:
    - `/` → `Hello World!` (text/plain)
    - `/status` → JSON `{"status": "ok"}` with `Content-Type: application/json` (use `json.dumps(...).encode()`)
    - anything else → `404 Not Found`
5. Test with a client: which User-Agent does the server see when the request comes from a browser, from curl and from `requests`?

**Comprehension Questions**
+ Why does `application` return a list of `bytes` and not `str`?
+ What happens if you forget to call `start_response`?
+ Which of the above (routing, JSON, headers, status codes) would Flask do for you?

**Code skeleton:**
<details>
<summary><b>Code</b></summary>

```python
# wsgi_app.py
from wsgiref.simple_server import make_server

def application(environ, start_response):
    # Print the most interesting keys of the request
    for key in ['REQUEST_METHOD', 'PATH_INFO', 'QUERY_STRING', 'HTTP_USER_AGENT']:
        print(f"{key}: {environ.get(key)}")
    print('-' * 40)

    # TODO: return a different response depending on environ['PATH_INFO']
    status = '200 OK'
    headers = [('Content-Type', 'text/plain; charset=utf-8')]
    start_response(status, headers)
    return [b'Hello World!']

if __name__ == '__main__':
    with make_server('127.0.0.1', 8000, application) as server:
        print('Serving on http://127.0.0.1:8000 (Ctrl+C to stop)')
        server.serve_forever()
```

</details>

**Check:**
```bash
curl -i http://127.0.0.1:8000/
curl -i http://127.0.0.1:8000/status
curl -i http://127.0.0.1:8000/missing
```
```python
import requests

for path in ['/', '/status', '/missing']:
    r = requests.get(f'http://127.0.0.1:8000{path}', timeout=5)
    print(path, r.status_code, r.headers['Content-Type'], r.text)
```

---

## Exercise 1: Basic Flask Application Setup

**Goal:** Create a basic Flask application as a single file.

**Requirements:**
1. Create an `app.py` with a Flask instance
2. Implement 3 routes:
   - `/` - Returns "Welcome to Flask Lab"
   - `/about` - Returns JSON with information about the app: name, version, description, environment
   - `/status` - Returns JSON with `{"status": "ok"}`
3. Run the app in debug mode, in one of two ways:
   - `python app.py` (uses `app.run(debug=True)`)
   - `flask --app app run --debug`
4. With the server running, change the message of `/` and save. What do you notice in the server's terminal?
5. Deliberately add an error (e.g. `1/0`) to a route and open it in the browser. What do you see? Why must a public server never run like this?

> 💡 If a view function returns a `dict`, Flask automatically converts it to JSON (just like `jsonify()`).

**Code skeleton:**
<details>
<summary><b>Code</b></summary>

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    # TODO: Implement
    pass

# TODO: /about and /status

if __name__ == '__main__':
    app.run(debug=True)
```

</details>

**Check:**
```bash
curl http://127.0.0.1:5000/
curl http://127.0.0.1:5000/about
curl -i http://127.0.0.1:5000/status
```
```python
import requests

BASE = 'http://127.0.0.1:5000'

r = requests.get(f'{BASE}/', timeout=5)
print(r.status_code, r.headers['Content-Type'], r.text)

for path in ['/about', '/status']:
    r = requests.get(f'{BASE}{path}', timeout=5)
    print(path, r.status_code, r.headers['Content-Type'], r.json())
```

---

## Exercise 2: Configuration Management

**Goal:** Create a configuration system with different environments.

**Requirements:**
1. Create `config.py` with a base class `Config` and three subclasses:
   - `DevelopmentConfig` (DEBUG=True, DATABASE_URI=sqlite)
   - `ProductionConfig` (DEBUG=False, DATABASE_URI from the environment variable `DATABASE_URL`)
   - `TestingConfig` (TESTING=True)
2. Each config should have:
   - `SECRET_KEY`
   - `DATABASE_URI` (create a fake one like `sqlite:///dev.db` — we are not using a database yet)
   - `DEBUG` (True/False)
3. Modify `app.py` to load the config named by the environment variable `APP_CONFIG` (default: `development`).
4. What happens if you write `Debug = True` instead of `DEBUG = True`?

**Code skeleton:**
<details>
<summary><b>Code</b></summary>

```python
# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'base-secret-key'
    # TODO: Add more base config

class DevelopmentConfig(Config):
    # TODO: Implement
    pass

class ProductionConfig(Config):
    # TODO: Implement
    pass

class TestingConfig(Config):
    # TODO: Implement
    pass

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

```python
# app.py (additions)
import os
from config import config

app = Flask(__name__)
config_name = os.environ.get('APP_CONFIG', 'default')
app.config.from_object(config[config_name])
```

</details>

**Check:**
```bash
export APP_CONFIG=production          # Windows (cmd): set APP_CONFIG=production
                                      # PowerShell:    $env:APP_CONFIG="production"
python
```
```python
# In the Python shell
from app import app
print(app.config['DEBUG'])
print(app.config['DATABASE_URI'])
```

---

## Exercise 3: Application Factory Pattern

**Goal:** Convert the single-file app into an application factory.

**Requirements:**
1. Create the file structure:
   ```
   myapp/
   ├── app/
   │   └── __init__.py
   ├── config.py
   └── run.py
   ```
2. In `app/__init__.py` implement a `create_app(config_name)` function
3. `create_app` should:
   - Create a Flask instance
   - Load the configuration
   - Define (temporarily, inside the function) the routes from Exercise 1
   - Return the app
4. `run.py` should call `create_app()` and run the app
5. Try creating two apps with different configs in the same Python shell. Why is this useful for testing?

> ℹ️ Older tutorials use `FLASK_ENV`. It was removed in Flask 2.3 and no longer has any effect, which is why we use our own variable (`APP_CONFIG`).

**Code skeleton:**
<details>
<summary><b>Code</b></summary>

```python
# app/__init__.py
from flask import Flask
from config import config

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    @app.route('/')
    def index():
        return 'Welcome to Flask Lab'

    # TODO: /about and /status from Exercise 1

    return app
```

```python
# run.py
import os
from app import create_app

config_name = os.environ.get('APP_CONFIG', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    app.run()   # DEBUG comes from the config
```

</details>

**Check:**
```bash
cd myapp
export APP_CONFIG=development         # Windows: set APP_CONFIG=development
python run.py
# or, without run.py:
flask --app "app:create_app('development')" run --debug
```
```python
from app import create_app

dev = create_app('development')
test = create_app('testing')
print(dev.config['DEBUG'], test.config['TESTING'])
```

---

## Exercise 4: First Blueprint - Main Module

**Goal:** Create a first blueprint for the main routes.

**Requirements:**
1. Create the blueprint structure:
   ```
   app/
   ├── __init__.py
   └── main/
       ├── __init__.py
       └── routes.py
   ```
2. In `main/__init__.py` create a blueprint named 'main'
3. **Move** the routes of Exercise 3 from `create_app()` to `main/routes.py` and add:
   - `/health` - Health check endpoint (JSON with `status` and `timestamp`)
4. Register the blueprint in `create_app()`
5. Why is `from app.main import routes` at the **end** of `main/__init__.py`?

**Code skeleton:**
<details>
<summary><b>Code</b></summary>

```python
# app/main/__init__.py
from flask import Blueprint

bp = Blueprint('main', __name__)

# At the end: routes.py imports bp, otherwise we get a circular import
from app.main import routes
```

```python
# app/main/routes.py
from datetime import datetime, timezone
from flask import jsonify
from app.main import bp

@bp.route('/')
def index():
    # TODO: Implement
    pass

@bp.route('/health')
def health():
    # TODO: Return JSON with status, timestamp
    # Hint: datetime.now(timezone.utc).isoformat()
    pass
```

```python
# app/__init__.py
from flask import Flask
from config import config

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app
```

</details>

**Check:**
```bash
curl http://127.0.0.1:5000/health
```
```python
import requests

BASE = 'http://127.0.0.1:5000'
r = requests.get(f'{BASE}/health', timeout=5)
print(r.status_code, r.json())
```

---

## Exercise 5: API Blueprint with URL Prefix

**Goal:** Create an API blueprint with versioned endpoints.

**Requirements:**
1. Create the `app/api/` blueprint (same structure as `main`)
2. Register it with the URL prefix `/api/v1`
3. Implement the endpoints:
   - `GET /api/v1/info` - API information
   - `GET /api/v1/echo?message=hello` - Echo service
4. All responses must be in JSON format
5. If `message` is missing, `/echo` must return `400 Bad Request` with JSON `{"error": "..."}`
6. Why is it good practice for an API URL to include a version (`v1`)?

**Code skeleton:**
<details>
<summary><b>Code</b></summary>

```python
# app/api/__init__.py
from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import routes
```

```python
# app/api/routes.py
from flask import jsonify, request
from app.api import bp

@bp.route('/info')
def api_info():
    return jsonify({
        'version': '1.0',
        'endpoints': ['/api/v1/info', '/api/v1/echo']
    })

@bp.route('/echo')
def echo():
    # TODO: Get 'message' from query params (request.args)
    # Return JSON with echoed message, or 400 if it is missing
    pass
```

```python
# app/__init__.py (inside create_app)
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
```

</details>

**Check:**
```bash
curl http://127.0.0.1:5000/api/v1/info
curl "http://127.0.0.1:5000/api/v1/echo?message=hello"
curl -i http://127.0.0.1:5000/api/v1/echo
```
```python
import requests

BASE = 'http://127.0.0.1:5000/api/v1'

print(requests.get(f'{BASE}/info', timeout=5).json())

r = requests.get(f'{BASE}/echo', params={'message': 'Καλημέρα & hello'}, timeout=5)
print(r.status_code, r.url, r.json())

r = requests.get(f'{BASE}/echo', timeout=5)
print(r.status_code, r.json())   # 400
```

---

## Exercise 6: Routing, Converters & url_for()

**Goal:** Dynamic URLs with converters, and building URLs with `url_for()` in blueprints.

**Requirements:**
1. In the `main` blueprint add:
   - `/user/<username>` → `User: <username>`
   - `/post/<int:post_id>` → JSON `{"post_id": <post_id>, "type": "int"}`
   - `/projects/` (with trailing slash) → `Projects`
   - `/go/<username>` → redirect to `/user/<username>` using `url_for()`
2. Check what `/post/42`, `/post/abc`, `/post/-1`, `/projects` and `/projects/` return. Explain each status code.
3. Why do we write `'main.user_profile'` in `url_for()` and not just `'user_profile'`?
4. What happens if two view functions have the same name?

**Code skeleton:**
<details>
<summary><b>Code</b></summary>

```python
# app/main/routes.py (additions)
from flask import redirect, url_for

@bp.route('/user/<username>')
def user_profile(username):
    # TODO: Implement
    pass

@bp.route('/post/<int:post_id>')
def show_post(post_id):
    # TODO: Implement
    pass

@bp.route('/projects/')
def projects():
    return 'Projects'

@bp.route('/go/<username>')
def go_to_profile(username):
    # Endpoint name inside a blueprint: '<blueprint>.<function>'
    return redirect(url_for('main.user_profile', username=username))
```

</details>

**Check:**
```bash
curl -i http://127.0.0.1:5000/post/abc
curl -i http://127.0.0.1:5000/projects
curl -iL http://127.0.0.1:5000/go/maria
```
```python
import requests

BASE = 'http://127.0.0.1:5000'

for path in ['/user/maria', '/post/42', '/post/abc', '/post/-1', '/projects', '/projects/']:
    r = requests.get(f'{BASE}{path}', allow_redirects=False, timeout=5)
    print(f"{path:12} → {r.status_code} {r.headers.get('Location', '')}")

r = requests.get(f'{BASE}/go/maria', timeout=5)   # follows the redirect
print(r.history, r.url, r.text)
```

---

## Exercise 7: HTTP Methods

**Goal:** An endpoint that accepts different HTTP methods (preparation for the RESTful APIs of the next lab).

**Requirements:**
1. Extend `/api/v1/echo` so that it accepts **GET and POST**:
   - `GET` → as in Exercise 5 (query parameter `message`)
   - `POST` → reads a JSON body (`request.get_json()`) and returns `{"method": "POST", "received": <body>}`
2. Send `PUT` and `DELETE` to the same endpoint. What status code do you get? What does the response's `Allow` header contain?
3. Send a `POST` without a JSON body (or with `Content-Type: text/plain`). What happens? How would you handle it?
4. Rewrite the route with the shortcuts `@bp.get(...)` and `@bp.post(...)` (two separate functions). Which version do you prefer?

**Code skeleton:**
<details>
<summary><b>Code</b></summary>

```python
# app/api/routes.py
@bp.route('/echo', methods=['GET', 'POST'])
def echo():
    if request.method == 'POST':
        data = request.get_json()
        # TODO: Return {'method': 'POST', 'received': data}
        pass
    # TODO: GET behaviour from Exercise 5
```

</details>

**Check:**
```bash
curl -i -X POST http://127.0.0.1:5000/api/v1/echo \
     -H "Content-Type: application/json" -d '{"message": "hi"}'
curl -i -X PUT http://127.0.0.1:5000/api/v1/echo
```
```python
import requests

URL = 'http://127.0.0.1:5000/api/v1/echo'

r = requests.post(URL, json={'message': 'hi', 'lab': 4}, timeout=5)
print(r.status_code, r.json())

for method in ['PUT', 'DELETE']:
    r = requests.request(method, URL, timeout=5)
    print(method, r.status_code, 'Allow:', r.headers.get('Allow'))

r = requests.post(URL, data='not json', headers={'Content-Type': 'text/plain'}, timeout=5)
print('text body:', r.status_code)
```

---

## Exercise 8: Production Server & Middleware

**Goal:** Run the same application with a production WSGI server and add a WSGI middleware.

**Requirements:**
1. Stop the development server and run the application with **Waitress** (works on every operating system):
   ```bash
   waitress-serve --listen 127.0.0.1:8000 --call app:create_app
   ```
   (With just `--port 8000`, Waitress listens on `0.0.0.0`, i.e. on the whole network.)
   On macOS/Linux you can also try **Gunicorn** (`pip install gunicorn`):
   ```bash
   gunicorn --workers 2 --bind 127.0.0.1:8000 "app:create_app()"
   ```
2. Run the checks again with `BASE = 'http://127.0.0.1:8000'`. Does everything work? What is **no longer** there (debugger, auto-reload)? What is the value of the `Server` header for each server?
3. Add the `Middleware` from the slides to `create_app()`, so that it prints the method and path of every request:
   ```python
   app.wsgi_app = Middleware(app.wsgi_app)
   ```
   Do the messages appear with both the development server and Waitress? Why?
4. What does `--call` mean in Waitress, and the parentheses in Gunicorn's `"app:create_app()"`?

**Code skeleton:**
<details>
<summary><b>Code</b></summary>

```python
# app/middleware.py
class Middleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Pre-processing
        print(f"{environ['REQUEST_METHOD']} {environ['PATH_INFO']}")

        # Call the actual application
        return self.app(environ, start_response)
```

```python
# app/__init__.py (inside create_app, before return)
    from app.middleware import Middleware
    app.wsgi_app = Middleware(app.wsgi_app)
```

</details>

**Check:**
```python
import requests

BASE = 'http://127.0.0.1:8000'
for path in ['/', '/health', '/api/v1/info', '/api/v1/echo?message=prod']:
    r = requests.get(f'{BASE}{path}', timeout=5)
    print(path, r.status_code, r.headers.get('Server'))
```
