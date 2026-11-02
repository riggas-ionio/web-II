# Week 5: Advanced Web Application Development Technologies

> 🇬🇷 [Ελληνική έκδοση](README.md)

In this lab, the `myapp` of Lab 4 becomes a complete **RESTful API** for users: CRUD, uniform JSON errors, logging, storage in **SQLite**, an HTML page with **Jinja2**, pagination and **automated tests**. By the end, the application is ready to be put into a container in Lab 6 (Docker).

## Setup

+ We continue in the `myapp/` folder of Lab 4 (Exercises 3–8), with the same venv:
  ```bash
  source flask_lab/bin/activate        # Windows: flask_lab\Scripts\activate
  pip install flask requests waitress pytest
  ```
+ We run the server from the `myapp/` folder:
  ```bash
  cd myapp
  flask --app run run --debug
  ```
+ As in Lab 4: **two terminals** (server / checks), and on **macOS** a different port if 5000 is taken by the AirPlay Receiver (`--port 5001`).
+ In the curl checks, `-i` shows the status code and headers. On **Windows** prefer the Python checks: JSON quoting in curl differs from shell to shell.

<details>
<summary><b>Starting point (if you did not finish Lab 4)</b></summary>

```
myapp/
├── app/
│   ├── __init__.py
│   ├── main/
│   │   ├── __init__.py
│   │   └── routes.py
│   └── api/
│       ├── __init__.py
│       └── routes.py
├── config.py
└── run.py
```

```python
# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'base-secret-key'
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URI = 'sqlite:///dev.db'

class ProductionConfig(Config):
    DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///prod.db'

class TestingConfig(Config):
    TESTING = True
    DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

```python
# run.py
import os
from app import create_app

config_name = os.environ.get('APP_CONFIG', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    app.run()
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

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    return app
```

```python
# app/main/__init__.py   (app/api/__init__.py: the same with 'api' and app.api)
from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes
```

```python
# app/main/routes.py
from app.main import bp

@bp.route('/')
def index():
    return 'Welcome to Flask Lab'
```

```python
# app/api/routes.py
from app.api import bp
```

</details>

---

## Exercise 1: RESTful Resource - Users (GET)

**Goal:** The first endpoints of the `users` resource, stored in an in-memory list.

**Requirements:**
1. In `app/api/routes.py` define the list `users_db` with two initial users.
2. Implement:
   - `GET /api/v1/users` → a **JSON array** with all users (200), like the GitHub and JSONPlaceholder APIs we consumed
   - `GET /api/v1/users/<id>` → the user (200) or `404` with `abort(404, description=...)`
3. What is the Content-Type of the `404` response? (We will fix it in Exercise 4.)

**Code skeleton:**
<details>
<summary><b>Code</b></summary>

```python
# app/api/routes.py
from flask import abort, jsonify, request, url_for
from app.api import bp

users_db = [
    {'id': 1, 'username': 'john', 'email': 'john@example.com'},
    {'id': 2, 'username': 'jane', 'email': 'jane@example.com'},
]

def find_user(user_id):
    return next((u for u in users_db if u['id'] == user_id), None)

@bp.route('/users', methods=['GET'])
def list_users():
    return jsonify(users_db)

@bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # TODO: Find the user with find_user()
    # abort(404, description=f'User {user_id} not found') if missing
    pass
```

</details>

**Check:**
```bash
curl http://127.0.0.1:5000/api/v1/users
curl http://127.0.0.1:5000/api/v1/users/1
curl -i http://127.0.0.1:5000/api/v1/users/999
```
```python
import requests

BASE = 'http://127.0.0.1:5000/api/v1'

r = requests.get(f'{BASE}/users', timeout=5)
print(r.status_code, r.json())

r = requests.get(f'{BASE}/users/1', timeout=5)
print(r.status_code, r.json())

r = requests.get(f'{BASE}/users/999', timeout=5)
print(r.status_code, r.headers['Content-Type'])   # 404, text/html for now
```

---

## Exercise 2: RESTful Resource - Users (POST)

**Goal:** Creating users, with validation.

**Requirements:**
1. Implement `POST /api/v1/users`:
   - Accepts JSON `{"username": "...", "email": "..."}`
   - If a field is missing (or the body is not JSON) → `400 Bad Request`
   - If a user with the same `username` already exists → `409 Conflict`
   - New `id` = largest existing `id` + 1
   - Returns `201 Created`, the new user, and a `Location` header with its URL (`url_for`)
2. Use `request.get_json(silent=True)`. What would happen without `silent=True` if the client sent `Content-Type: text/plain`? (Remember Exercise 7 of Lab 4.)
3. Why is it a bad idea for the new `id` to be `len(users_db) + 1`? (Think about what happens after a `DELETE`.)

**Code skeleton:**
<details>
<summary><b>Code</b></summary>

```python
@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json(silent=True)

    if not data or not data.get('username') or not data.get('email'):
        abort(400, description='username and email are required')

    # TODO: 409 if the username already exists

    new_id = max((u['id'] for u in users_db), default=0) + 1
    # TODO: Create the user dict and append it to users_db

    # TODO: Return the user, 201 and the Location header:
    # return user, 201, {'Location': url_for('api.get_user', user_id=new_id)}
```

</details>

**Check:**
```bash
# Valid request
curl -i -X POST http://127.0.0.1:5000/api/v1/users \
     -H "Content-Type: application/json" \
     -d '{"username":"alice","email":"alice@example.com"}'

# Invalid request (missing email)
curl -i -X POST http://127.0.0.1:5000/api/v1/users \
     -H "Content-Type: application/json" \
     -d '{"username":"bob"}'
```
```python
import requests

BASE = 'http://127.0.0.1:5000/api/v1'

r = requests.post(f'{BASE}/users', json={'username': 'alice', 'email': 'alice@example.com'}, timeout=5)
print(r.status_code, r.headers.get('Location'), r.json())   # 201

r = requests.post(f'{BASE}/users', json={'username': 'bob'}, timeout=5)
print(r.status_code)                                         # 400

r = requests.post(f'{BASE}/users', json={'username': 'alice', 'email': 'other@example.com'}, timeout=5)
print(r.status_code)                                         # 409

r = requests.post(f'{BASE}/users', data='not json', headers={'Content-Type': 'text/plain'}, timeout=5)
print(r.status_code)                                         # 400
```

---

## Exercise 3: RESTful Resource - Users (PUT, PATCH & DELETE)

**Goal:** Complete the CRUD operations, with the correct semantics for each method.

**Requirements:**
1. `PUT /api/v1/users/<id>` — **replacement**: requires **both** fields (otherwise `400`), returns `200` and the user.
2. `PATCH /api/v1/users/<id>` — **partial update**: changes only the fields that were sent, returns `200`.
3. `DELETE /api/v1/users/<id>` — `204 No Content` (empty body).
4. All three: `404` if the user does not exist.
5. Use the shortcuts `@bp.put`, `@bp.patch`, `@bp.delete`.
6. Send the same `DELETE` twice. Is `DELETE` idempotent, given that the second call returns a different status code?

**Code skeleton:**
<details>
<summary><b>Code</b></summary>

```python
@bp.put('/users/<int:user_id>')
def replace_user(user_id):
    # TODO: 404 if missing
    # TODO: 400 unless both username and email are present
    # TODO: Replace the fields, return the user
    pass

@bp.patch('/users/<int:user_id>')
def update_user(user_id):
    # TODO: 404 if missing
    # TODO: Update only the fields present in the JSON body
    pass

@bp.delete('/users/<int:user_id>')
def delete_user(user_id):
    # TODO: 404 if missing
    # TODO: Remove from users_db
    return '', 204
```

</details>

**Check:**
```bash
# Partial update
curl -i -X PATCH http://127.0.0.1:5000/api/v1/users/1 \
     -H "Content-Type: application/json" \
     -d '{"email":"newemail@example.com"}'

# Delete
curl -i -X DELETE http://127.0.0.1:5000/api/v1/users/2
```
```python
import requests

BASE = 'http://127.0.0.1:5000/api/v1'

r = requests.patch(f'{BASE}/users/1', json={'email': 'new@example.com'}, timeout=5)
print('PATCH', r.status_code, r.json())

r = requests.put(f'{BASE}/users/1', json={'email': 'only@example.com'}, timeout=5)
print('PUT (partial)', r.status_code)                       # 400

r = requests.put(f'{BASE}/users/1', json={'username': 'johnny', 'email': 'j@example.com'}, timeout=5)
print('PUT', r.status_code, r.json())

r = requests.delete(f'{BASE}/users/2', timeout=5)
print('DELETE', r.status_code, repr(r.text))                # 204 ''
print('DELETE again', requests.delete(f'{BASE}/users/2', timeout=5).status_code)
print('GET after', requests.get(f'{BASE}/users/2', timeout=5).status_code)
```

---

## Exercise 4: Error Handling - JSON for all errors

**Goal:** Every API error (404, 400, 405, 409, 415, 500, ...) returns JSON with the same shape:
```json
{
  "error": "Not Found",
  "message": "User 999 not found",
  "status": 404
}
```

**Requirements:**
1. Create `app/errors.py` with a function `register_error_handlers(app)`.
2. One handler for **all** `HTTPException`s (see slides). Use `e.get_response()`, so that headers such as the `Allow` of a `405` are not lost.
3. Call the function in `create_app()`.
4. Try: a URL that does not exist, a user that does not exist, `DELETE` on `/api/v1/users`.
5. **500:** temporarily add a route `/api/v1/boom` that does `1 / 0`.
   - Run the server **without** `--debug` (`flask --app run run`): what does it return?
   - Run it **with** `--debug`: what do you see? Why is your handler not called?
   - Why must the 500 message not contain the text of the exception?

**Code skeleton:**
<details>
<summary><b>Code</b></summary>

```python
# app/errors.py
import json
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        response = e.get_response()   # keeps headers such as Allow, Retry-After
        # TODO: response.data = JSON with error (e.name), message (e.description), status (e.code)
        # TODO: response.content_type = 'application/json'
        return response
```

```python
# app/__init__.py (inside create_app, before return)
    from app.errors import register_error_handlers
    register_error_handlers(app)
```

```python
# app/api/routes.py — temporary, remove it afterwards
@bp.route('/boom')
def boom():
    return 1 / 0
```

</details>

**Check:**
```bash
curl -i http://127.0.0.1:5000/nonexistent
curl -i http://127.0.0.1:5000/api/v1/users/999
curl -i -X DELETE http://127.0.0.1:5000/api/v1/users
curl -i http://127.0.0.1:5000/api/v1/boom
```
```python
import requests

BASE = 'http://127.0.0.1:5000'

for method, path in [('GET', '/nonexistent'), ('GET', '/api/v1/users/999'),
                     ('DELETE', '/api/v1/users'), ('GET', '/api/v1/boom')]:
    r = requests.request(method, f'{BASE}{path}', timeout=5)
    print(method, path, r.status_code, r.headers['Content-Type'], r.headers.get('Allow', ''))
    print('   ', r.json())
```

---

## Exercise 5: Request Hooks - Logging & Request ID

**Goal:** Log every request, and give each request a unique ID for debugging.

**Requirements:**
1. Create `app/hooks.py` with a function `register_hooks(app)` that defines `@app.before_request` and `@app.after_request`.
2. For every request, log (with `current_app.logger.info`, **not** `print`) the method, path, status code, duration in ms and request ID:
   ```
   [2026-10-27 10:30:45,120] INFO in hooks: GET /api/v1/users -> 200 (3ms) [9f1c2a...]
   ```
3. Request ID:
   - If the client sends an `X-Request-ID` header, use it. Otherwise create a new one (`uuid.uuid4().hex`).
   - Store it in `g.request_id` and return it in the `X-Request-ID` response header.
   - Accept the client's ID **only** if it is up to 64 characters of `A-Z a-z 0-9 -`. Why do we not trust a header? (Think about what would happen in the logs with an ID containing `\n`.)
4. Configure logging in `create_app()` with `logging.basicConfig(...)` and `LOG_LEVEL` from the config (default `INFO`). Without it, `INFO` messages are **not shown** when the server runs without `--debug`. Try it.
5. Why do we keep the start time in `g` and not in a global variable?

**Code skeleton:**
<details>
<summary><b>Code</b></summary>

```python
# app/hooks.py
import re
import time
import uuid
from flask import current_app, g, request

VALID_ID = re.compile(r'^[A-Za-z0-9-]{1,64}$')

def register_hooks(app):

    @app.before_request
    def start_request():
        g.start_time = time.perf_counter()
        # TODO: g.request_id = the client's X-Request-ID if VALID_ID matches, else uuid.uuid4().hex

    @app.after_request
    def log_request(response):
        elapsed_ms = (time.perf_counter() - g.start_time) * 1000
        # TODO: response.headers['X-Request-ID'] = ...
        # TODO: current_app.logger.info('%s %s -> %s (%.0fms) [%s]', ...)
        return response
```

```python
# config.py (in class Config)
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
```

```python
# app/__init__.py
import logging
# ...
def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    logging.basicConfig(
        level=app.config['LOG_LEVEL'],
        format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    )
    # ... blueprints, error handlers ...

    from app.hooks import register_hooks
    register_hooks(app)

    return app
```

</details>

**Check:**
```bash
curl -i http://127.0.0.1:5000/api/v1/users
curl -i -H "X-Request-ID: my-custom-id" http://127.0.0.1:5000/api/v1/users
```
```python
import requests

BASE = 'http://127.0.0.1:5000/api/v1'

r = requests.get(f'{BASE}/users', timeout=5)
print(r.headers['X-Request-ID'])                  # new ID

r = requests.get(f'{BASE}/users', headers={'X-Request-ID': 'my-custom-id'}, timeout=5)
print(r.headers['X-Request-ID'])                  # my-custom-id

r = requests.get(f'{BASE}/users', headers={'X-Request-ID': 'bad id!'}, timeout=5)
print(r.headers['X-Request-ID'])                  # rejected → new ID
```
Also look at the corresponding lines in the server terminal.

---

## Exercise 6: Persistence with SQLite

**Goal:** Users are stored in a database, not in the memory of the process.

**Requirements:**
1. Stop and restart the server. What happened to the users you created?
2. Create:
   - `app/schema.sql`: a `users` table (`id`, `username` UNIQUE, `email`, `created_at`) and two initial users
   - `app/db.py`: `get_db()` with `g`, `close_db()`, `init_db()` and the `init-db` command (see slides)
3. In `create_app()` call `db.init_app(app)` and initialise the database:
   ```bash
   flask --app run init-db
   ```
4. Rewrite **all** the `users` routes with SQL instead of `users_db`. The API must behave **exactly** as before (the checks of Exercises 1–4 must pass unchanged), with one extra field, `created_at`.
   - The `409` now comes from the database's `UNIQUE` constraint: catch `sqlite3.IntegrityError`.
5. Restart the server. Are the users still there now?
6. Why do we write `WHERE id = ?` and **never** `f"WHERE id = {user_id}"`? Try creating a user with username `x'); DROP TABLE users; --`. What happens?
7. Add `*.db` to `.gitignore`.

**Code skeleton:**
<details>
<summary><b>Code</b></summary>

```sql
-- app/schema.sql
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (username, email) VALUES
    ('john', 'john@example.com'),
    ('jane', 'jane@example.com');
```

```python
# app/db.py
import sqlite3
import click
from flask import current_app, g

def get_db():
    if 'db' not in g:
        path = current_app.config['DATABASE_URI'].removeprefix('sqlite:///')
        g.db = sqlite3.connect(path)
        g.db.row_factory = sqlite3.Row     # rows behave like dicts
    return g.db

def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))

@click.command('init-db')
def init_db_command():
    """Drop and recreate the tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
```

```python
# app/__init__.py (inside create_app)
    from app import db
    db.init_app(app)
```

```python
# app/api/routes.py
import sqlite3
from flask import abort, jsonify, request, url_for
from app.api import bp
from app.db import get_db

def find_user(user_id):
    row = get_db().execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if row is None:
        abort(404, description=f'User {user_id} not found')
    return dict(row)

@bp.get('/users')
def list_users():
    rows = get_db().execute('SELECT * FROM users ORDER BY id').fetchall()
    return jsonify([dict(row) for row in rows])

@bp.get('/users/<int:user_id>')
def get_user(user_id):
    return find_user(user_id)

@bp.post('/users')
def create_user():
    data = request.get_json(silent=True)
    if not data or not data.get('username') or not data.get('email'):
        abort(400, description='username and email are required')
    db = get_db()
    try:
        cursor = db.execute('INSERT INTO users (username, email) VALUES (?, ?)',
                            (data['username'], data['email']))
        db.commit()
    except sqlite3.IntegrityError:
        abort(409, description=f"username '{data['username']}' already exists")
    user = find_user(cursor.lastrowid)
    return user, 201, {'Location': url_for('api.get_user', user_id=user['id'])}

# TODO: PUT, PATCH, DELETE with UPDATE / DELETE statements (and db.commit())
```

</details>

**Check:**
Re-run the checks of Exercises 1–4, then restart the server and:
```python
import requests

BASE = 'http://127.0.0.1:5000/api/v1'

for user in requests.get(f'{BASE}/users', timeout=5).json():
    print(user['id'], user['username'], user['created_at'])

r = requests.post(f'{BASE}/users', json={'username': "x'); DROP TABLE users; --",
                                         'email': 'evil@example.com'}, timeout=5)
print(r.status_code, r.json()['username'])
print(len(requests.get(f'{BASE}/users', timeout=5).json()), 'users — the table is still there')
```

---

## Exercise 7: Jinja2 - An HTML page with the users

**Goal:** The same data, this time as an HTML page for a human instead of JSON for a program.

**Requirements:**
1. Create `app/templates/base.html` (navigation with `url_for('main.index')` and `url_for('main.users_page')`, blocks `title` and `content`).
2. Create `app/templates/users.html`, which `extends` `base.html` and shows:
   - the number of users (`|length`)
   - a table with id, username, email (`|lower`) and creation date in the form `27/10/2026`
   - the message "No users yet." if the list is empty (the `{% else %}` of `for`)
3. In the `main` blueprint add a route `/users` (function `users_page`) that reads the users from the database and calls `render_template`.
4. For the date, write a **custom filter** `shortdate` (Jinja2 has no `strftime` filter; SQLite returns `created_at` as a string).
5. **XSS:** create a user through the API with username `<script>alert('xss')</script>` and open `/users` in the browser. Does the script run? Look at the page source. What would change with `{{ user.username|safe }}`?

**Code skeleton:**
<details>
<summary><b>Code</b></summary>

```html
<!-- app/templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Flask Lab{% endblock %}</title>
</head>
<body>
    <nav>
        <a href="{{ url_for('main.index') }}">Home</a> |
        <a href="{{ url_for('main.users_page') }}">Users</a>
    </nav>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

```html
<!-- app/templates/users.html -->
{% extends "base.html" %}

{% block title %}Users{% endblock %}

{% block content %}
<h1>Users ({{ users|length }})</h1>
<table>
    <tr><th>ID</th><th>Username</th><th>Email</th><th>Created</th></tr>
    {% for user in users %}
    <!-- TODO: one row per user, created_at with the shortdate filter -->
    {% else %}
    <tr><td colspan="4">No users yet.</td></tr>
    {% endfor %}
</table>
{% endblock %}
```

```python
# app/main/routes.py (additions)
from datetime import datetime
from flask import render_template
from app.db import get_db

@bp.route('/users')
def users_page():
    # TODO: SELECT all users, render users.html
    pass

@bp.app_template_filter('shortdate')
def shortdate(value):
    # '2026-10-27 10:54:15' → '27/10/2026'
    return datetime.fromisoformat(value).strftime('%d/%m/%Y')
```

</details>

**Check:** Open http://127.0.0.1:5000/users in the browser, and:
```python
import requests

BASE = 'http://127.0.0.1:5000'

requests.post(f'{BASE}/api/v1/users',
              json={'username': "<script>alert('xss')</script>", 'email': 'XSS@Example.com'}, timeout=5)

r = requests.get(f'{BASE}/users', timeout=5)
print(r.status_code, r.headers['Content-Type'])
print('<script>' in r.text, '&lt;script&gt;' in r.text)     # False True
```

---

## Exercise 8: Pagination & Filtering

**Goal:** Paginate the list with the same convention as the GitHub API, so that the client from Lab 3 works with your own API.

**Requirements:**
1. `GET /api/v1/users` accepts query parameters:
   - `page` (default 1), `per_page` (default 10, **maximum** 100)
   - `q`: filtering, users whose `username` **or** `email` contains the text (`LIKE ?` with `%q%`)
   - `page` or `per_page` < 1 → `400`
2. The body remains a **JSON array** (only the users of the page).
3. Headers:
   - `X-Total-Count`: number of all results (after the filter)
   - `Link`: URLs for `next` and `last` (if there is a next page), `first` and `prev` (if we are not on the first one). Full URLs with `url_for(..., _external=True)` that keep `per_page` and `q`.
4. Why do we put an upper limit on `per_page`?

**Code skeleton:**
<details>
<summary><b>Code</b></summary>

```python
# app/api/routes.py
def page_link(page, per_page, q, rel):
    url = url_for('api.list_users', page=page, per_page=per_page, q=q or None, _external=True)
    return f'<{url}>; rel="{rel}"'

@bp.get('/users')
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    q = request.args.get('q', '').strip()
    if page < 1 or per_page < 1:
        abort(400, description='page and per_page must be positive integers')

    where, args = '', []
    if q:
        where = 'WHERE username LIKE ? OR email LIKE ?'
        args = [f'%{q}%', f'%{q}%']

    db = get_db()
    total = db.execute(f'SELECT COUNT(*) FROM users {where}', args).fetchone()[0]
    rows = db.execute(f'SELECT * FROM users {where} ORDER BY id LIMIT ? OFFSET ?',
                      args + [per_page, (page - 1) * per_page]).fetchall()

    response = jsonify([dict(r) for r in rows])
    response.headers['X-Total-Count'] = total
    last = max(1, -(-total // per_page))          # ceil division
    links = []
    # TODO: next & last if page < last, first & prev if page > 1 (use page_link)
    if links:
        response.headers['Link'] = ', '.join(links)
    return response
```

`where` is put into the SQL with an f-string, but it contains **only** our own fixed text. The user's value (`q`) is always passed as a `?` parameter.

</details>

**Check:** `fetch_all_pages()` is taken **unchanged** from Lab 3.
```python
import requests

BASE = 'http://127.0.0.1:5000/api/v1'

for i in range(1, 11):
    requests.post(f'{BASE}/users', json={'username': f'student{i}', 'email': f'student{i}@ionio.gr'}, timeout=5)

def fetch_all_pages(url, params=None, max_pages=5):
    items = []
    pages = 0

    while url and pages < max_pages:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        items.extend(response.json())
        pages += 1
        print(f"Page {pages}: {response.url}")

        url = response.links.get('next', {}).get('url')
        params = None

    return items

users = fetch_all_pages(f'{BASE}/users', params={'per_page': 4})
print(f"Total users: {len(users)}")

r = requests.get(f'{BASE}/users', params={'q': 'student1', 'per_page': 1}, timeout=5)
print(r.headers['X-Total-Count'], r.json())
print(r.links)

print(requests.get(f'{BASE}/users', params={'page': 0}, timeout=5).status_code)    # 400
print(requests.get(f'{BASE}/users', params={'page': 99}, timeout=5).json())        # []
```

---

## Exercise 9: Automated Testing with pytest

**Goal:** Instead of re-running the checks by hand after every change, we write them as tests that run with a single command, without a server.

**Requirements:**
1. Create `tests/conftest.py` with the fixtures `app` and `client` (see skeleton). Every test gets a **new** database with the two initial users.
2. Create `tests/test_users.py` and write tests for:
   - `GET /users` → 200 and 2 users
   - `GET /users/999` → 404 and JSON with `status: 404`
   - `POST` → 201, a `Location` header, and the user can then be found with `GET`
   - `POST` without `email` → 400 · `POST` with an existing username → 409
   - `PUT` with a single field → 400 · `PATCH` changes only the `email`
   - `DELETE` → 204, then `GET` → 404
   - Pagination: `X-Total-Count` and `rel="next"` in the `Link` header
   - The `/users` page escapes `<script>`
3. Run the tests from the `myapp/` folder:
   ```bash
   python -m pytest -v
   ```
4. In the code, change `201` to `200` in `create_user`. Which test fails? What message does pytest give? Undo the change.
5. Why does the fixture use a temporary **file** and not the `sqlite:///:memory:` of `TestingConfig`? (Try it. Hint: how many connections does `get_db()` open?)
6. Why `python -m pytest` and not plain `pytest`? (Try both.)

**Code skeleton:**
<details>
<summary><b>Code</b></summary>

```
myapp/
├── app/
├── tests/
│   ├── conftest.py
│   └── test_users.py
├── config.py
└── run.py
```

```python
# tests/conftest.py
import pytest
from app import create_app
from app.db import init_db

@pytest.fixture
def app(tmp_path):
    app = create_app('testing')
    # A file, not :memory: — every request opens a new connection
    app.config['DATABASE_URI'] = f'sqlite:///{tmp_path / "test.db"}'
    with app.app_context():
        init_db()
    return app

@pytest.fixture
def client(app):
    return app.test_client()
```

```python
# tests/test_users.py
def test_list_users(client):
    response = client.get('/api/v1/users')
    assert response.status_code == 200
    assert len(response.get_json()) == 2

def test_get_missing_user_returns_json_404(client):
    response = client.get('/api/v1/users/999')
    assert response.status_code == 404
    assert response.get_json()['status'] == 404

def test_create_user(client):
    response = client.post('/api/v1/users',
                           json={'username': 'alice', 'email': 'alice@example.com'})
    assert response.status_code == 201
    assert response.headers['Location'] == '/api/v1/users/3'
    assert client.get('/api/v1/users/3').get_json()['username'] == 'alice'

# TODO: the remaining tests from the list above
```

</details>

**Check:**
```bash
python -m pytest -v
```
```
tests/test_users.py::test_list_users PASSED
tests/test_users.py::test_get_missing_user_returns_json_404 PASSED
tests/test_users.py::test_create_user PASSED
...
```

---

## Exercise 10: Docker-ready

**Goal:** The application is configured **only** through environment variables, declares its dependencies and reports whether it is healthy. Docker will need all of this in Lab 6.

**Requirements:**
1. **Config from the environment:** `create_app(config_name=None)` reads `APP_CONFIG` when no argument is given. This way Waitress (`--call app:create_app`, without arguments) gets the right configuration.
2. **Fail fast:** in `production`, if `SECRET_KEY` is the default one, `create_app()` raises `RuntimeError`.
3. **`/health`:** also checks the database (`SELECT 1 FROM users LIMIT 1`): `200` with `{"status": "ok", "database": "ok", ...}`, otherwise `503` with `"database": "unavailable"`.
4. **`requirements.txt`** with the versions you use:
   ```bash
   pip freeze | grep -i -E "^(flask|waitress)=="      # Windows: pip freeze | findstr /i "flask waitress"
   ```
   What would be different with `pip freeze > requirements.txt`? Does the production server need `pytest` or `requests`?
5. **`.env.example`** with all the variables the application reads (without real secrets), and `.env` in `.gitignore`.
6. Run the application "as in production":
   ```bash
   export APP_CONFIG=production SECRET_KEY=s3cr3t DATABASE_URL=sqlite:///prod.db
   # Windows (PowerShell): $env:APP_CONFIG="production"; $env:SECRET_KEY="s3cr3t"; $env:DATABASE_URL="sqlite:///prod.db"
   waitress-serve --listen 127.0.0.1:8000 --call app:create_app
   ```
   - What does `/health` return **before** `flask --app run init-db` (with the same variables, in a second terminal) and what **after**?
   - What happens if you leave out `SECRET_KEY`?
7. Think: in Lab 6 the application will run with `gunicorn --workers 4`. What would happen to the `users_db` list of Exercises 1–3? Why does the server inside a container listen on `0.0.0.0` and not on `127.0.0.1`?

**Code skeleton:**
<details>
<summary><b>Code</b></summary>

```python
# app/__init__.py
import logging
import os
from flask import Flask
from config import config

def create_app(config_name=None):
    config_name = config_name or os.environ.get('APP_CONFIG', 'default')
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # TODO: RuntimeError in production with the default SECRET_KEY

    # ... logging, db, blueprints, error handlers, hooks (as before) ...
    return app
```

```python
# app/main/routes.py
import sqlite3
from datetime import datetime, timezone

@bp.route('/health')
def health():
    try:
        get_db().execute('SELECT 1 FROM users LIMIT 1')
        database = 'ok'
    except sqlite3.Error:
        database = 'unavailable'
    # TODO: return status, database, timestamp; 200 or 503
```

```txt
# requirements.txt
Flask==3.1.3
waitress==3.0.2
```

```bash
# .env.example
APP_CONFIG=production
SECRET_KEY=change-me
DATABASE_URL=sqlite:///prod.db
LOG_LEVEL=INFO
```

</details>

**Check:**
```python
import requests

BASE = 'http://127.0.0.1:8000'

r = requests.get(f'{BASE}/health', timeout=5)
print(r.status_code, r.json(), r.headers.get('Server'))   # 503 before init-db, 200 after

r = requests.get(f'{BASE}/api/v1/users', timeout=5)
print(r.status_code, r.json())                            # 500 before init-db (no table yet)
```
```bash
APP_CONFIG=production python -c "from app import create_app; create_app()"
# RuntimeError: Set the SECRET_KEY environment variable in production
```

---

## Bonus A: Protection with an API key

**Goal:** Data changes (`POST`, `PUT`, `PATCH`, `DELETE`) require an `X-API-Key` header; reading stays public.

**Requirements:**
1. `API_KEY` in the config, from an environment variable. If it is not set, the protection is disabled (e.g. in the tests).
2. An `@bp.before_request` on the `api` blueprint that returns `401` (through `abort`) when the key is missing or wrong.
3. Compare with `hmac.compare_digest`. Why not with `==`?
4. Does the check apply to `/health` or to the `/users` page? Why?

**Code skeleton:**
<details>
<summary><b>Code</b></summary>

```python
# config.py (in class Config)
    API_KEY = os.environ.get('API_KEY')          # None = no protection
```

```python
# app/api/routes.py
import hmac
from flask import current_app

@bp.before_request
def require_api_key():
    if request.method in ('GET', 'HEAD', 'OPTIONS'):
        return                                   # reading is public
    expected = current_app.config.get('API_KEY')
    if not expected:
        return                                   # protection disabled
    # TODO: compare the X-API-Key header with hmac.compare_digest, abort(401, ...) if different
```

</details>

**Check:** with `export API_KEY=lab5-key` before you start the server:
```python
import requests

URL = 'http://127.0.0.1:5000/api/v1/users'
new = {'username': 'maria', 'email': 'maria@ionio.gr'}

print(requests.post(URL, json=new, timeout=5).status_code)                                   # 401
print(requests.post(URL, json=new, headers={'X-API-Key': 'wrong'}, timeout=5).status_code)   # 401
print(requests.post(URL, json=new, headers={'X-API-Key': 'lab5-key'}, timeout=5).status_code) # 201
print(requests.get(URL, timeout=5).status_code)                                              # 200
```

---

## Bonus B: Rate Limiting

**Goal:** At most `RATE_LIMIT` requests per minute per IP (default 10). This is the other side of the `429` we handled as a client in Lab 3.

**Requirements:**
1. Create `app/ratelimit.py` with `register_rate_limit(app)` and an `@app.before_request`.
2. For each IP, keep the timestamps of the requests of the last minute (`deque`), and drop the older ones.
3. When the limit is exceeded: `abort(429, description=..., retry_after=<seconds>)`. Werkzeug adds the `Retry-After` header, and the error handler of Exercise 4 keeps it.
4. Do not limit `/health`. Why? (Think about Docker's `HEALTHCHECK`.)
5. Questions:
   - The server handles many requests at the same time (threads). Why is `threading.Lock` needed?
   - With `gunicorn --workers 4` (Lab 6), how many requests per minute would actually get through? Where should the state be kept? (Hint: Redis.)
   - Behind a reverse proxy or Docker, which IP does `request.remote_addr` see?

**Code skeleton:**
<details>
<summary><b>Code</b></summary>

```python
# app/ratelimit.py
import threading
import time
from collections import defaultdict, deque
from flask import abort, current_app, request

history = defaultdict(deque)     # {ip: deque([timestamp, ...])}
lock = threading.Lock()          # the server is multi-threaded
WINDOW = 60                      # seconds

def register_rate_limit(app):

    @app.before_request
    def rate_limit():
        if request.path == '/health':
            return
        ip = request.remote_addr
        now = time.monotonic()
        with lock:
            calls = history[ip]
            # TODO: popleft() the timestamps older than WINDOW
            # TODO: if len(calls) >= current_app.config['RATE_LIMIT']:
            #           abort(429, description='Too many requests', retry_after=...)
            calls.append(now)
```

```python
# config.py (in class Config / TestingConfig)
    RATE_LIMIT = int(os.environ.get('RATE_LIMIT', 10))
    # TestingConfig: RATE_LIMIT = 1000, otherwise the tests hit the limit
```

</details>

**Check:**
```bash
for i in $(seq 1 15); do curl -s -o /dev/null -w "%{http_code} " http://127.0.0.1:5000/api/v1/users; done; echo
```
```python
import requests

URL = 'http://127.0.0.1:5000/api/v1/users'

responses = [requests.get(URL, timeout=5) for _ in range(15)]
print([r.status_code for r in responses])
print(responses[-1].headers.get('Retry-After'), responses[-1].json())
print(requests.get('http://127.0.0.1:5000/health', timeout=5).status_code)   # 200
```
