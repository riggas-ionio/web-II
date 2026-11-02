# Εβδομάδα 5: Προχωρημένες Τεχνολογίες Ανάπτυξης Εφαρμογών Διαδικτύου

> 🇬🇧 [English version](README.en.md)

Σε αυτό το εργαστήριο το `myapp` του Εργαστηρίου 4 γίνεται ένα πλήρες **RESTful API** για χρήστες: CRUD, ενιαία JSON σφάλματα, logging, αποθήκευση σε **SQLite**, μια σελίδα HTML με **Jinja2**, σελιδοποίηση και **αυτόματα tests**. Στο τέλος η εφαρμογή είναι έτοιμη να μπει σε container στο Εργαστήριο 6 (Docker).

## Προετοιμασία

+ Συνεχίζουμε στον φάκελο `myapp/` του Εργαστηρίου 4 (Ασκήσεις 3–8), με το ίδιο venv:
  ```bash
  source flask_lab/bin/activate        # Windows: flask_lab\Scripts\activate
  pip install flask requests waitress pytest
  ```
+ Τρέχουμε τον server από τον φάκελο `myapp/`:
  ```bash
  cd myapp
  flask --app run run --debug
  ```
+ Όπως και στο Εργαστήριο 4: **δύο τερματικά** (server / έλεγχοι), και σε **macOS** άλλο port αν το 5000 είναι πιασμένο από τον AirPlay Receiver (`--port 5001`).
+ Στους ελέγχους με curl, το `-i` δείχνει status code και headers. Σε **Windows** προτιμήστε τους ελέγχους με Python: το quoting του JSON στο curl διαφέρει ανά shell.

<details>
<summary><b>Αφετηρία (αν δεν ολοκληρώσατε το Εργαστήριο 4)</b></summary>

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

## Άσκηση 1: RESTful Resource - Users (GET)

**Στόχος:** Τα πρώτα endpoints του resource `users`, με αποθήκευση σε λίστα στη μνήμη.

**Απαιτήσεις:**
1. Στο `app/api/routes.py` ορίστε τη λίστα `users_db` με δύο αρχικούς χρήστες.
2. Υλοποιήστε:
   - `GET /api/v1/users` → **JSON array** με όλους τους χρήστες (200), όπως τα APIs του GitHub και του JSONPlaceholder που καταναλώσαμε
   - `GET /api/v1/users/<id>` → ο χρήστης (200) ή `404` με `abort(404, description=...)`
3. Τι Content-Type έχει η απάντηση `404`; (Θα το διορθώσουμε στην Άσκηση 4.)

**Σκελετός κώδικα:**
<details>
<summary><b>Κώδικας</b></summary>

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

**Έλεγχος:**
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

## Άσκηση 2: RESTful Resource - Users (POST)

**Στόχος:** Δημιουργία χρηστών με validation.

**Απαιτήσεις:**
1. Υλοποιήστε `POST /api/v1/users`:
   - Δέχεται JSON `{"username": "...", "email": "..."}`
   - Αν λείπει κάποιο πεδίο (ή το body δεν είναι JSON) → `400 Bad Request`
   - Αν υπάρχει ήδη χρήστης με το ίδιο `username` → `409 Conflict`
   - Νέο `id` = μεγαλύτερο υπάρχον `id` + 1
   - Επιστρέφει `201 Created`, τον νέο χρήστη, και header `Location` με το URL του (`url_for`)
2. Χρησιμοποιήστε `request.get_json(silent=True)`. Τι θα γινόταν χωρίς το `silent=True`, αν ο client έστελνε `Content-Type: text/plain`; (Θυμηθείτε την Άσκηση 7 του Εργαστηρίου 4.)
3. Γιατί δεν είναι καλή ιδέα το νέο `id` να είναι `len(users_db) + 1`; (Σκεφτείτε τι γίνεται μετά από ένα `DELETE`.)

**Σκελετός κώδικα:**
<details>
<summary><b>Κώδικας</b></summary>

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

**Έλεγχος:**
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

## Άσκηση 3: RESTful Resource - Users (PUT, PATCH & DELETE)

**Στόχος:** Ολοκλήρωση των CRUD operations, με τη σωστή σημασιολογία κάθε μεθόδου.

**Απαιτήσεις:**
1. `PUT /api/v1/users/<id>` — **αντικατάσταση**: απαιτεί **και τα δύο** πεδία (αλλιώς `400`), επιστρέφει `200` και τον χρήστη.
2. `PATCH /api/v1/users/<id>` — **μερική ενημέρωση**: αλλάζει μόνο όσα πεδία στάλθηκαν, επιστρέφει `200`.
3. `DELETE /api/v1/users/<id>` — `204 No Content` (κενό body).
4. Και τα τρία: `404` αν ο χρήστης δεν υπάρχει.
5. Χρησιμοποιήστε τις συντομεύσεις `@bp.put`, `@bp.patch`, `@bp.delete`.
6. Στείλτε το ίδιο `DELETE` δύο φορές. Είναι το `DELETE` idempotent, αφού η δεύτερη φορά δίνει άλλο status code;

**Σκελετός κώδικα:**
<details>
<summary><b>Κώδικας</b></summary>

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

**Έλεγχος:**
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

## Άσκηση 4: Error Handling - JSON για όλα τα σφάλματα

**Στόχος:** Κάθε σφάλμα του API (404, 400, 405, 409, 415, 500, ...) να επιστρέφει JSON με το ίδιο σχήμα:
```json
{
  "error": "Not Found",
  "message": "User 999 not found",
  "status": 404
}
```

**Απαιτήσεις:**
1. Δημιουργήστε `app/errors.py` με μία συνάρτηση `register_error_handlers(app)`.
2. Ένας handler για **όλα** τα `HTTPException` (βλ. διαφάνειες). Χρησιμοποιήστε `e.get_response()`, ώστε να μη χαθούν headers όπως το `Allow` του `405`.
3. Καλέστε τη συνάρτηση στο `create_app()`.
4. Δοκιμάστε: URL που δεν υπάρχει, χρήστη που δεν υπάρχει, `DELETE` στο `/api/v1/users`.
5. **500:** προσθέστε προσωρινά ένα route `/api/v1/boom` που κάνει `1 / 0`.
   - Τρέξτε τον server **χωρίς** `--debug` (`flask --app run run`): τι επιστρέφει;
   - Τρέξτε τον **με** `--debug`: τι βλέπετε; Γιατί δεν καλείται ο handler σας;
   - Γιατί δεν πρέπει το μήνυμα του 500 να περιέχει το κείμενο του exception;

**Σκελετός κώδικα:**
<details>
<summary><b>Κώδικας</b></summary>

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

**Έλεγχος:**
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

## Άσκηση 5: Request Hooks - Logging & Request ID

**Στόχος:** Καταγραφή κάθε request και ένα μοναδικό ID ανά request για debugging.

**Απαιτήσεις:**
1. Δημιουργήστε `app/hooks.py` με συνάρτηση `register_hooks(app)` που ορίζει `@app.before_request` και `@app.after_request`.
2. Για κάθε request καταγράψτε (με `current_app.logger.info`, **όχι** `print`) μέθοδο, path, status code, διάρκεια σε ms και request ID:
   ```
   [2026-10-27 10:30:45,120] INFO in hooks: GET /api/v1/users -> 200 (3ms) [9f1c2a...]
   ```
3. Request ID:
   - Αν ο client στέλνει header `X-Request-ID`, χρησιμοποιήστε το. Αλλιώς δημιουργήστε νέο (`uuid.uuid4().hex`).
   - Αποθηκεύστε το στο `g.request_id` και επιστρέψτε το στο response header `X-Request-ID`.
   - Δεχτείτε το ID του client **μόνο** αν είναι έως 64 χαρακτήρες `A-Z a-z 0-9 -`. Γιατί δεν εμπιστευόμαστε ένα header; (Σκεφτείτε τι θα γινόταν στα logs με ένα ID που περιέχει `\n`.)
4. Ρυθμίστε το logging στο `create_app()` με `logging.basicConfig(...)` και `LOG_LEVEL` από το config (default `INFO`). Χωρίς αυτό, τα μηνύματα `INFO` **δεν εμφανίζονται** όταν ο server τρέχει χωρίς `--debug`. Δοκιμάστε το.
5. Γιατί κρατάμε τον χρόνο έναρξης στο `g` και όχι σε μια global μεταβλητή;

**Σκελετός κώδικα:**
<details>
<summary><b>Κώδικας</b></summary>

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

**Έλεγχος:**
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
Δείτε και τις αντίστοιχες γραμμές στο τερματικό του server.

---

## Άσκηση 6: Persistence με SQLite

**Στόχος:** Οι χρήστες να αποθηκεύονται σε βάση και όχι στη μνήμη του process.

**Απαιτήσεις:**
1. Σταματήστε και ξεκινήστε ξανά τον server. Τι έγινε με τους χρήστες που δημιουργήσατε;
2. Δημιουργήστε:
   - `app/schema.sql`: πίνακας `users` (`id`, `username` UNIQUE, `email`, `created_at`) και δύο αρχικοί χρήστες
   - `app/db.py`: `get_db()` με `g`, `close_db()`, `init_db()` και την εντολή `init-db` (βλ. διαφάνειες)
3. Στο `create_app()` καλέστε `db.init_app(app)` και αρχικοποιήστε τη βάση:
   ```bash
   flask --app run init-db
   ```
4. Ξαναγράψτε **όλα** τα routes του `users` με SQL αντί για `users_db`. Το API πρέπει να συμπεριφέρεται **ακριβώς** όπως πριν (οι έλεγχοι των Ασκήσεων 1–4 πρέπει να περνούν χωρίς αλλαγές), με ένα επιπλέον πεδίο `created_at`.
   - Το `409` τώρα προκύπτει από το `UNIQUE` της βάσης: πιάστε το `sqlite3.IntegrityError`.
5. Επανεκκινήστε τον server. Υπάρχουν τώρα οι χρήστες;
6. Γιατί γράφουμε `WHERE id = ?` και **ποτέ** `f"WHERE id = {user_id}"`; Δοκιμάστε να δημιουργήσετε χρήστη με username `x'); DROP TABLE users; --`. Τι γίνεται;
7. Προσθέστε το `*.db` στο `.gitignore`.

**Σκελετός κώδικα:**
<details>
<summary><b>Κώδικας</b></summary>

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

**Έλεγχος:**
Ξανατρέξτε τους ελέγχους των Ασκήσεων 1–4, μετά επανεκκινήστε τον server και:
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

## Άσκηση 7: Jinja2 - Σελίδα HTML με τους χρήστες

**Στόχος:** Τα ίδια δεδομένα, αυτή τη φορά ως HTML σελίδα για άνθρωπο αντί για JSON για πρόγραμμα.

**Απαιτήσεις:**
1. Δημιουργήστε `app/templates/base.html` (navigation με `url_for('main.index')` και `url_for('main.users_page')`, block `title` και `content`).
2. Δημιουργήστε `app/templates/users.html` που κάνει `extends` το `base.html` και δείχνει:
   - τον αριθμό των χρηστών (`|length`)
   - πίνακα με id, username, email (`|lower`) και ημερομηνία δημιουργίας σε μορφή `27/10/2026`
   - μήνυμα «No users yet.» αν η λίστα είναι άδεια (`{% else %}` του `for`)
3. Στο `main` blueprint προσθέστε route `/users` (function `users_page`) που διαβάζει τους χρήστες από τη βάση και κάνει `render_template`.
4. Για την ημερομηνία γράψτε **custom filter** `shortdate` (το Jinja2 δεν έχει filter `strftime`· το SQLite επιστρέφει το `created_at` ως string).
5. **XSS:** δημιουργήστε μέσω του API χρήστη με username `<script>alert('xss')</script>` και ανοίξτε το `/users` στον browser. Εκτελείται το script; Δείτε τον πηγαίο κώδικα της σελίδας. Τι θα άλλαζε με `{{ user.username|safe }}`;

**Σκελετός κώδικα:**
<details>
<summary><b>Κώδικας</b></summary>

```html
<!-- app/templates/base.html -->
<!DOCTYPE html>
<html lang="el">
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

**Έλεγχος:** Ανοίξτε το http://127.0.0.1:5000/users στον browser, και:
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

## Άσκηση 8: Pagination & Filtering

**Στόχος:** Σελιδοποίηση της λίστας με την ίδια σύμβαση που χρησιμοποιεί το GitHub API, ώστε ο client του Εργαστηρίου 3 να δουλεύει με το δικό σας API.

**Απαιτήσεις:**
1. Το `GET /api/v1/users` να δέχεται query parameters:
   - `page` (default 1), `per_page` (default 10, **μέγιστο** 100)
   - `q`: φιλτράρισμα, χρήστες που το `username` **ή** το `email` περιέχουν το κείμενο (`LIKE ?` με `%q%`)
   - `page` ή `per_page` < 1 → `400`
2. Το body παραμένει **JSON array** (μόνο οι χρήστες της σελίδας).
3. Headers:
   - `X-Total-Count`: πλήθος όλων των αποτελεσμάτων (μετά το φίλτρο)
   - `Link`: URLs για `next` και `last` (αν υπάρχει επόμενη σελίδα), `first` και `prev` (αν δεν είμαστε στην πρώτη). Πλήρη URLs με `url_for(..., _external=True)`, που κρατούν τα `per_page` και `q`.
4. Γιατί βάζουμε ανώτατο όριο στο `per_page`;

**Σκελετός κώδικα:**
<details>
<summary><b>Κώδικας</b></summary>

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

Το `where` μπαίνει στο SQL με f-string, αλλά περιέχει **μόνο** δικό μας σταθερό κείμενο. Η τιμή του χρήστη (`q`) περνά πάντα ως parameter `?`.

</details>

**Έλεγχος:** Η `fetch_all_pages()` είναι **αυτούσια** από το Εργαστήριο 3.
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

## Άσκηση 9: Automated Testing με pytest

**Στόχος:** Αντί να ξανατρέχουμε με το χέρι τους ελέγχους μετά από κάθε αλλαγή, τους γράφουμε ως tests που τρέχουν με μία εντολή, χωρίς server.

**Απαιτήσεις:**
1. Δημιουργήστε `tests/conftest.py` με τα fixtures `app` και `client` (βλ. σκελετό). Κάθε test παίρνει **νέα** βάση με τους δύο αρχικούς χρήστες.
2. Δημιουργήστε `tests/test_users.py` και γράψτε tests για:
   - `GET /users` → 200 και 2 χρήστες
   - `GET /users/999` → 404 και JSON με `status: 404`
   - `POST` → 201, header `Location`, και ο χρήστης βρίσκεται μετά με `GET`
   - `POST` χωρίς `email` → 400 · `POST` με υπάρχον username → 409
   - `PUT` με ένα μόνο πεδίο → 400 · `PATCH` αλλάζει μόνο το `email`
   - `DELETE` → 204, μετά `GET` → 404
   - Pagination: `X-Total-Count` και `rel="next"` στο header `Link`
   - Η σελίδα `/users` κάνει escape το `<script>`
3. Τρέξτε τα tests από τον φάκελο `myapp/`:
   ```bash
   python -m pytest -v
   ```
4. Αλλάξτε στον κώδικα το `201` σε `200` στο `create_user`. Ποιο test αποτυγχάνει; Τι μήνυμα δίνει το pytest; Επαναφέρετε την αλλαγή.
5. Γιατί το fixture χρησιμοποιεί προσωρινό **αρχείο** και όχι το `sqlite:///:memory:` του `TestingConfig`; (Δοκιμάστε το. Υπόδειξη: πόσες συνδέσεις ανοίγει το `get_db()`;)
6. Γιατί `python -m pytest` και όχι σκέτο `pytest`; (Δοκιμάστε και τα δύο.)

**Σκελετός κώδικα:**
<details>
<summary><b>Κώδικας</b></summary>

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

**Έλεγχος:**
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

## Άσκηση 10: Έτοιμο για Docker

**Στόχος:** Η εφαρμογή να ρυθμίζεται **μόνο** από environment variables, να δηλώνει τα dependencies της και να αναφέρει αν είναι υγιής. Αυτά θα χρειαστεί το Docker στο Εργαστήριο 6.

**Απαιτήσεις:**
1. **Config από το environment:** το `create_app(config_name=None)` να διαβάζει το `APP_CONFIG` όταν δεν δίνεται όρισμα. Έτσι ο Waitress (`--call app:create_app`, χωρίς ορίσματα) παίρνει τη σωστή ρύθμιση.
2. **Fail fast:** σε `production`, αν το `SECRET_KEY` είναι το default, το `create_app()` να σηκώνει `RuntimeError`.
3. **`/health`:** να ελέγχει και τη βάση (`SELECT 1 FROM users LIMIT 1`): `200` με `{"status": "ok", "database": "ok", ...}`, αλλιώς `503` με `"database": "unavailable"`.
4. **`requirements.txt`** με τις εκδόσεις που χρησιμοποιείτε:
   ```bash
   pip freeze | grep -i -E "^(flask|waitress)=="      # Windows: pip freeze | findstr /i "flask waitress"
   ```
   Τι διαφορά θα είχε το `pip freeze > requirements.txt`; Χρειάζεται το `pytest` ή το `requests` στον production server;
5. **`.env.example`** με όλες τις μεταβλητές που διαβάζει η εφαρμογή (χωρίς πραγματικά μυστικά), και `.env` στο `.gitignore`.
6. Τρέξτε την εφαρμογή «όπως σε production»:
   ```bash
   export APP_CONFIG=production SECRET_KEY=s3cr3t DATABASE_URL=sqlite:///prod.db
   # Windows (PowerShell): $env:APP_CONFIG="production"; $env:SECRET_KEY="s3cr3t"; $env:DATABASE_URL="sqlite:///prod.db"
   waitress-serve --listen 127.0.0.1:8000 --call app:create_app
   ```
   - Τι επιστρέφει το `/health` **πριν** το `flask --app run init-db` (με τις ίδιες μεταβλητές, σε δεύτερο τερματικό) και τι **μετά**;
   - Τι γίνεται αν παραλείψετε το `SECRET_KEY`;
7. Σκεφτείτε: στο Εργ. 6 η εφαρμογή θα τρέχει με `gunicorn --workers 4`. Τι θα γινόταν με τη λίστα `users_db` των Ασκήσεων 1–3; Γιατί ο server μέσα σε container ακούει σε `0.0.0.0` και όχι σε `127.0.0.1`;

**Σκελετός κώδικα:**
<details>
<summary><b>Κώδικας</b></summary>

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

**Έλεγχος:**
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

## Bonus A: Προστασία με API key

**Στόχος:** Οι αλλαγές δεδομένων (`POST`, `PUT`, `PATCH`, `DELETE`) να απαιτούν header `X-API-Key`· η ανάγνωση μένει δημόσια.

**Απαιτήσεις:**
1. `API_KEY` στο config από environment variable. Αν δεν έχει οριστεί, η προστασία είναι απενεργοποιημένη (π.χ. στα tests).
2. `@bp.before_request` στο `api` blueprint που επιστρέφει `401` (μέσω `abort`) όταν το κλειδί λείπει ή είναι λάθος.
3. Σύγκριση με `hmac.compare_digest`. Γιατί όχι με `==`;
4. Ισχύει ο έλεγχος στο `/health` ή στη σελίδα `/users`; Γιατί;

**Σκελετός κώδικα:**
<details>
<summary><b>Κώδικας</b></summary>

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

**Έλεγχος:** με `export API_KEY=lab5-key` πριν ξεκινήσετε τον server:
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

**Στόχος:** Το πολύ `RATE_LIMIT` requests ανά λεπτό ανά IP (default 10). Είναι η άλλη πλευρά του `429` που χειριστήκαμε ως client στο Εργαστήριο 3.

**Απαιτήσεις:**
1. Δημιουργήστε `app/ratelimit.py` με `register_rate_limit(app)` και ένα `@app.before_request`.
2. Κρατήστε για κάθε IP τις χρονοσφραγίδες των requests του τελευταίου λεπτού (`deque`), και πετάξτε τις παλαιότερες.
3. Όταν ξεπεραστεί το όριο: `abort(429, description=..., retry_after=<seconds>)`. Το header `Retry-After` το προσθέτει το Werkzeug και ο error handler της Άσκησης 4 το κρατά.
4. Μην περιορίζετε το `/health`. Γιατί; (Σκεφτείτε το `HEALTHCHECK` του Docker.)
5. Ερωτήσεις:
   - Ο server εξυπηρετεί πολλά requests ταυτόχρονα (threads). Γιατί χρειάζεται το `threading.Lock`;
   - Με `gunicorn --workers 4` (Εργ. 6), πόσα requests το λεπτό θα περνούσαν στην πράξη; Πού θα έπρεπε να κρατιέται η κατάσταση; (Υπόδειξη: Redis.)
   - Πίσω από reverse proxy ή Docker, ποια IP βλέπει το `request.remote_addr`;

**Σκελετός κώδικα:**
<details>
<summary><b>Κώδικας</b></summary>

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

**Έλεγχος:**
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
