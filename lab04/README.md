# Εβδομάδα 4: Προχωρημένες Τεχνολογίες Ανάπτυξης Εφαρμογών Διαδικτύου

> 🇬🇧 [English version](README.en.md)

Μέχρι τώρα γράφαμε **HTTP clients** (με `requests`). Σε αυτό το εργαστήριο περνάμε στην άλλη πλευρά: γράφουμε **HTTP servers** και τους ελέγχουμε με τους clients που ήδη ξέρουμε να φτιάχνουμε.

## Προετοιμασία

```bash
python3 -m venv flask_lab
source flask_lab/bin/activate        # macOS/Linux
# flask_lab\Scripts\activate.bat     # Windows (cmd)
# flask_lab\Scripts\Activate.ps1     # Windows (PowerShell)
pip install flask requests waitress
```

+ Θα χρειαστείτε **δύο τερματικά**: στο πρώτο τρέχει ο server (και το «δεσμεύει» μέχρι `Ctrl+C`), στο δεύτερο οι έλεγχοι (curl / Python). Ενεργοποιήστε το venv και στα δύο.
+ ⚠️ **macOS**: το port 5000 το χρησιμοποιεί ο _AirPlay Receiver_ (σφάλμα `403` ή "Address already in use"). Τρέξτε το Flask σε άλλο port, π.χ. `flask --app app run --debug --port 5001`, και αλλάξτε ανάλογα τα URLs των ελέγχων.
+ Στους ελέγχους με Python, το `BASE` είναι η διεύθυνση του server σας:
  ```python
  BASE = 'http://127.0.0.1:5000'
  ```

---

## Άσκηση 0: Ένας server χωρίς Flask (WSGI)

**Στόχος:** Να τρέξετε την WSGI εφαρμογή των διαφανειών μόνο με την standard library της Python και να δείτε τι κάνει το Flask για εμάς.

**Απαιτήσεις:**
1. Αποθηκεύστε τον κώδικα ως `wsgi_app.py` και τρέξτε τον: `python wsgi_app.py`
2. Ανοίξτε στον browser το http://127.0.0.1:8000/ και μετά το http://127.0.0.1:8000/hello?name=Maria. Τι εκτυπώνεται στο τερματικό του server;
3. Εντοπίστε στο `environ` τα κλειδιά `REQUEST_METHOD`, `PATH_INFO`, `QUERY_STRING` και `HTTP_USER_AGENT`. Σε τι αντιστοιχούν στο HTTP request;
4. Τροποποιήστε την `application` ώστε:
    - `/` → `Hello World!` (text/plain)
    - `/status` → JSON `{"status": "ok"}` με `Content-Type: application/json` (χρησιμοποιήστε `json.dumps(...).encode()`)
    - οτιδήποτε άλλο → `404 Not Found`
5. Ελέγξτε με τον client: τι User-Agent βλέπει ο server όταν το request έρχεται από browser, από curl και από `requests`;

**Ερωτήσεις Κατανόησης**
+ Γιατί η `application` επιστρέφει λίστα από `bytes` και όχι `str`;
+ Τι θα συμβεί αν ξεχάσετε να καλέσετε το `start_response`;
+ Ποια από τα παραπάνω (routing, JSON, headers, status codes) θα σας τα έκανε έτοιμα το Flask;

**Σκελετός κώδικα:**
<details>
<summary><b>Κώδικας</b></summary>

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

**Έλεγχος:**
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

## Άσκηση 1: Basic Flask Application Setup

**Στόχος:** Δημιουργία βασικού Flask application ως single file.

**Απαιτήσεις:**
1. Δημιουργήστε ένα `app.py` με Flask instance
2. Υλοποιήστε 3 routes:
   - `/` - Επιστρέφει "Welcome to Flask Lab"
   - `/about` - Επιστρέφει JSON με πληροφορίες για το app: name, version, description, environment
   - `/status` - Επιστρέφει JSON με `{"status": "ok"}`
3. Τρέξτε το app σε debug mode, με έναν από τους δύο τρόπους:
   - `python app.py` (χρησιμοποιεί το `app.run(debug=True)`)
   - `flask --app app run --debug`
4. Με τον server να τρέχει, αλλάξτε το μήνυμα του `/` και αποθηκεύστε. Τι παρατηρείτε στο τερματικό του server;
5. Προσθέστε επίτηδες ένα σφάλμα (π.χ. `1/0`) σε ένα route και ανοίξτε το στον browser. Τι βλέπετε; Γιατί δεν πρέπει ποτέ να τρέχει έτσι ένας δημόσιος server;

> 💡 Αν μια view function επιστρέψει `dict`, το Flask το μετατρέπει αυτόματα σε JSON (όπως και το `jsonify()`).

**Σκελετός κώδικα:**
<details>
<summary><b>Κώδικας</b></summary>

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

**Έλεγχος:**
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

## Άσκηση 2: Configuration Management

**Στόχος:** Δημιουργία configuration system με διαφορετικά environments.

**Απαιτήσεις:**
1. Δημιουργήστε `config.py` με μια βασική class `Config` και τρεις υποκλάσεις:
   - `DevelopmentConfig` (DEBUG=True, DATABASE_URI=sqlite)
   - `ProductionConfig` (DEBUG=False, DATABASE_URI από την περιβαλλοντική μεταβλητή `DATABASE_URL`)
   - `TestingConfig` (TESTING=True)
2. Κάθε config να έχει:
   - `SECRET_KEY`
   - `DATABASE_URI` (δημιουργήστε ένα fake τύπου `sqlite:///dev.db` — δεν χρησιμοποιούμε ακόμα βάση)
   - `DEBUG` (True/False)
3. Τροποποιήστε το `app.py` να φορτώνει το config που ορίζει η περιβαλλοντική μεταβλητή `APP_CONFIG` (default: `development`).
4. Τι θα συμβεί αν γράψετε `Debug = True` αντί για `DEBUG = True`;

**Σκελετός κώδικα:**
<details>
<summary><b>Κώδικας</b></summary>

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

**Έλεγχος:**
```bash
export APP_CONFIG=production          # Windows (cmd): set APP_CONFIG=production
                                      # PowerShell:    $env:APP_CONFIG="production"
python
```
```python
# Στο Python shell
from app import app
print(app.config['DEBUG'])
print(app.config['DATABASE_URI'])
```

---

## Άσκηση 3: Application Factory Pattern

**Στόχος:** Μετατροπή single-file app σε application factory.

**Απαιτήσεις:**
1. Δημιουργήστε τη δομή αρχείων:
   ```
   myapp/
   ├── app/
   │   └── __init__.py
   ├── config.py
   └── run.py
   ```
2. Στο `app/__init__.py` υλοποιήστε `create_app(config_name)` function
3. Το `create_app` να:
   - Δημιουργεί Flask instance
   - Φορτώνει configuration
   - Ορίζει (προσωρινά, μέσα στη συνάρτηση) τα routes της Άσκησης 1
   - Επιστρέφει το app
4. Το `run.py` να καλεί το `create_app()` και να τρέχει το app
5. Δοκιμάστε να δημιουργήσετε δύο apps με διαφορετικό config στο ίδιο Python shell. Γιατί αυτό είναι χρήσιμο στο testing;

> ℹ️ Παλαιότερα tutorials χρησιμοποιούν το `FLASK_ENV`. Καταργήθηκε στο Flask 2.3 και δεν έχει πλέον καμία επίδραση, γι' αυτό χρησιμοποιούμε δική μας μεταβλητή (`APP_CONFIG`).

**Σκελετός κώδικα:**
<details>
<summary><b>Κώδικας</b></summary>

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

**Έλεγχος:**
```bash
cd myapp
export APP_CONFIG=development         # Windows: set APP_CONFIG=development
python run.py
# ή, χωρίς run.py:
flask --app "app:create_app('development')" run --debug
```
```python
from app import create_app

dev = create_app('development')
test = create_app('testing')
print(dev.config['DEBUG'], test.config['TESTING'])
```

---

## Άσκηση 4: First Blueprint - Main Module

**Στόχος:** Δημιουργία πρώτου blueprint για main routes.

**Απαιτήσεις:**
1. Δημιουργήστε blueprint structure:
   ```
   app/
   ├── __init__.py
   └── main/
       ├── __init__.py
       └── routes.py
   ```
2. Στο `main/__init__.py` δημιουργήστε blueprint με όνομα 'main'
3. **Μεταφέρετε** τα routes της Άσκησης 3 από το `create_app()` στο `main/routes.py` και προσθέστε:
   - `/health` - Health check endpoint (JSON με `status` και `timestamp`)
4. Register το blueprint στο `create_app()`
5. Γιατί το `from app.main import routes` βρίσκεται στο **τέλος** του `main/__init__.py`;

**Σκελετός κώδικα:**
<details>
<summary><b>Κώδικας</b></summary>

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

**Έλεγχος:**
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

## Άσκηση 5: API Blueprint με URL Prefix

**Στόχος:** Δημιουργία API blueprint με versioned endpoints.

**Απαιτήσεις:**
1. Δημιουργήστε `app/api/` blueprint (ίδια δομή με το `main`)
2. Register με URL prefix `/api/v1`
3. Υλοποιήστε endpoints:
   - `GET /api/v1/info` - API information
   - `GET /api/v1/echo?message=hello` - Echo service
4. Όλα τα responses να είναι JSON format
5. Αν λείπει το `message`, το `/echo` να επιστρέφει `400 Bad Request` με JSON `{"error": "..."}`
6. Γιατί είναι καλή πρακτική να έχει έκδοση (`v1`) το URL ενός API;

**Σκελετός κώδικα:**
<details>
<summary><b>Κώδικας</b></summary>

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

**Έλεγχος:**
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

## Άσκηση 6: Routing, Converters & url_for()

**Στόχος:** Δυναμικά URLs με converters και δημιουργία URLs με `url_for()` σε blueprints.

**Απαιτήσεις:**
1. Στο `main` blueprint προσθέστε:
   - `/user/<username>` → `User: <username>`
   - `/post/<int:post_id>` → JSON `{"post_id": <post_id>, "type": "int"}`
   - `/projects/` (με trailing slash) → `Projects`
   - `/go/<username>` → redirect στο `/user/<username>` χρησιμοποιώντας `url_for()`
2. Ελέγξτε τι επιστρέφουν τα `/post/42`, `/post/abc`, `/post/-1`, `/projects` και `/projects/`. Εξηγήστε κάθε status code.
3. Γιατί στο `url_for()` γράφουμε `'main.user_profile'` και όχι σκέτο `'user_profile'`;
4. Τι γίνεται αν δύο view functions έχουν το ίδιο όνομα;

**Σκελετός κώδικα:**
<details>
<summary><b>Κώδικας</b></summary>

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

**Έλεγχος:**
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

## Άσκηση 7: HTTP Methods

**Στόχος:** Ένα endpoint που δέχεται διαφορετικές HTTP μεθόδους (προετοιμασία για τα RESTful APIs του επόμενου εργαστηρίου).

**Απαιτήσεις:**
1. Επεκτείνετε το `/api/v1/echo` ώστε να δέχεται **GET και POST**:
   - `GET` → όπως στην Άσκηση 5 (query parameter `message`)
   - `POST` → διαβάζει JSON body (`request.get_json()`) και επιστρέφει `{"method": "POST", "received": <body>}`
2. Στείλτε `PUT` και `DELETE` στο ίδιο endpoint. Τι status code παίρνετε; Τι περιέχει το header `Allow` της απάντησης;
3. Στείλτε `POST` χωρίς JSON body (ή με `Content-Type: text/plain`). Τι συμβαίνει; Πώς θα το χειριζόσασταν;
4. Ξαναγράψτε το route με τα shortcuts `@bp.get(...)` και `@bp.post(...)` (δύο ξεχωριστές functions). Ποια εκδοχή προτιμάτε;

**Σκελετός κώδικα:**
<details>
<summary><b>Κώδικας</b></summary>

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

**Έλεγχος:**
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

## Άσκηση 8: Production Server & Middleware

**Στόχος:** Να τρέξετε την ίδια εφαρμογή με production WSGI server και να προσθέσετε ένα WSGI middleware.

**Απαιτήσεις:**
1. Σταματήστε τον development server και τρέξτε την εφαρμογή με **Waitress** (λειτουργεί σε όλα τα λειτουργικά):
   ```bash
   waitress-serve --listen 127.0.0.1:8000 --call app:create_app
   ```
   (Με σκέτο `--port 8000` ο Waitress ακούει σε `0.0.0.0`, δηλαδή σε όλο το δίκτυο.)
   Σε macOS/Linux μπορείτε να δοκιμάσετε και **Gunicorn** (`pip install gunicorn`):
   ```bash
   gunicorn --workers 2 --bind 127.0.0.1:8000 "app:create_app()"
   ```
2. Ξανατρέξτε τους ελέγχους με `BASE = 'http://127.0.0.1:8000'`. Λειτουργούν όλα; Τι **δεν** υπάρχει πια (debugger, auto-reload); Τι τιμή έχει το header `Server` σε κάθε server;
3. Προσθέστε στο `create_app()` το `Middleware` των διαφανειών, ώστε να εκτυπώνει τη μέθοδο και το path κάθε request:
   ```python
   app.wsgi_app = Middleware(app.wsgi_app)
   ```
   Εμφανίζονται τα μηνύματα και με τον development server και με τον Waitress; Γιατί;
4. Τι σημαίνει το `--call` στο Waitress και οι παρενθέσεις στο `"app:create_app()"` του Gunicorn;

**Σκελετός κώδικα:**
<details>
<summary><b>Κώδικας</b></summary>

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

**Έλεγχος:**
```python
import requests

BASE = 'http://127.0.0.1:8000'
for path in ['/', '/health', '/api/v1/info', '/api/v1/echo?message=prod']:
    r = requests.get(f'{BASE}{path}', timeout=5)
    print(path, r.status_code, r.headers.get('Server'))
```
