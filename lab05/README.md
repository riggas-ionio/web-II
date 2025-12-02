# Εβδομάδα 5: Προχωρημένες Τεχνολογίες Ανάπτυξης Εφαρμογών Διαδικτύου


## Άσκηση 1: Basic Flask Application Setup

**Στόχος:** Δημιουργία βασικού Flask application ως single file.

## Άσκηση 1: RESTful Resource - Users (Part 1)

**Στόχος:** Υλοποίηση RESTful endpoints για Users resource με in-memory storage.

**Απαιτήσεις:**
1. Στο API blueprint προσθέστε `/users` endpoint
2. Χρησιμοποιήστε λίστα για temporary storage:
   ```python
   users_db = [
       {'id': 1, 'username': 'john', 'email': 'john@example.com'},
       {'id': 2, 'username': 'jane', 'email': 'jane@example.com'}
   ]
   ```
3. Υλοποιήστε:
   - `GET /api/v1/users` - List all users (200)
   - `GET /api/v1/users/<id>` - Get specific user (200 ή 404)

**Σκελετός κώδικα:**
<details> 

```python
# app/api/routes.py
users_db = []  # Global list για αποθήκευση

@bp.route('/users', methods=['GET'])
def get_users():
    return jsonify({
        'users': users_db,
        'count': len(users_db)
    }), 200

@bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # TODO: Find user by id
    # Return 404 if not found
    pass
```

</details> 

**Έλεγχος:**
```bash
curl http://localhost:5000/api/v1/users
curl http://localhost:5000/api/v1/users/1
curl http://localhost:5000/api/v1/users/999  # Should return 404
```

---

## Άσκηση 2: RESTful Resource - Users (Part 2: POST)

**Στόχος:** Προσθήκη POST endpoint για δημιουργία users.

**Απαιτήσεις:**
1. Υλοποιήστε `POST /api/v1/users`:
   - Accept JSON payload: `{"username": "...", "email": "..."}`
   - Validate ότι υπάρχουν και τα δύο fields
   - Generate auto-increment ID
   - Return 201 Created με το νέο user
   - Return 400 Bad Request αν λείπουν fields
2. Χρησιμοποιήστε `request.get_json()`

**Σκελετός κώδικα:**
<details> 

```python
@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    # TODO: Validate data
    if not data or 'username' not in data or 'email' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # TODO: Create new user with auto-increment ID
    # TODO: Add to users_db
    # TODO: Return 201 with created user
    pass
```
</details> 

**Έλεγχος:**
```bash
# Valid request
curl -X POST http://localhost:5000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com"}'

# Invalid request (missing email)
curl -X POST http://localhost:5000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"username":"bob"}'
```

---

## Άσκηση 3: RESTful Resource - Users (Part 3: PUT & DELETE)

**Στόχος:** Ολοκλήρωση CRUD operations.

**Απαιτήσεις:**
1. `PUT /api/v1/users/<id>` - Update user:
   - Accept partial updates (username ή/και email)
   - Return 200 με updated user
   - Return 404 αν δεν υπάρχει
2. `DELETE /api/v1/users/<id>` - Delete user:
   - Return 204 No Content on success
   - Return 404 αν δεν υπάρχει

**Σκελετός κώδικα:**
<details> 

```python
@bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    # TODO: Find user
    # TODO: Update fields from request.get_json()
    # TODO: Return updated user
    pass

@bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    # TODO: Find and remove user
    # TODO: Return 204 (no content in response body)
    pass
```
</details> 

**Έλεγχος:**
```bash
# Update
curl -X PUT http://localhost:5000/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{"email":"newemail@example.com"}'

# Delete
curl -X DELETE http://localhost:5000/api/v1/users/1
```

---

## Άσκηση 5: Error Handling - Custom Error Handlers

**Στόχος:** Δημιουργία consistent error responses.

**Απαιτήσεις:**
1. Δημιουργήστε `app/errors.py` module
2. Υλοποιήστε custom error handlers για:
   - 404 Not Found
   - 400 Bad Request
   - 500 Internal Server Error
3. Όλα τα errors να επιστρέφουν JSON format:
   ```json
   {
     "error": "Not Found",
     "message": "The requested resource was not found",
     "status": 404
   }
   ```
4. Register τους handlers στο `create_app()`

**Σκελετός κώδικα:**
<details> 

```python
# app/errors.py
from flask import jsonify

def register_error_handlers(app):
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': str(error),
            'status': 404
        }), 404
    
    @app.errorhandler(400)
    def bad_request(error):
        # TODO: Implement
        pass
    
    @app.errorhandler(500)
    def internal_error(error):
        # TODO: Implement
        pass

# app/__init__.py
def create_app(config_name='development'):
    # ... existing code ...
    
    from app.errors import register_error_handlers
    register_error_handlers(app)
    
    return app
```
</details> 

**Έλεγχος:**
```bash
curl http://localhost:5000/nonexistent
curl http://localhost:5000/api/v1/users/999
```

---

## Άσκηση 6: Request Logging Middleware

**Στόχος:** Υλοποίηση logging για όλα τα requests.

**Απαιτήσεις:**
1. Δημιουργήστε `app/middleware.py`
2. Υλοποιήστε logging που καταγράφει:
   - Request method και path
   - Timestamp
   - Response status code
   - Response time (ms)
3. Format: `[2025-01-15 10:30:45] GET /api/v1/users -> 200 (15ms)`
4. Χρησιμοποιήστε `@app.before_request` και `@app.after_request`

**Σκελετός κώδικα:**
<details> 


```python
# app/middleware.py
import time
import logging
from flask import request, g

logger = logging.getLogger(__name__)

def register_middleware(app):
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        # TODO: Calculate elapsed time
        # TODO: Log request info
        # Format: [timestamp] METHOD path -> STATUS (Xms)
        return response

# app/__init__.py
def create_app(config_name='development'):
    # ... existing code ...
    
    from app.middleware import register_middleware
    register_middleware(app)
    
    return app
```
</details> 

**Έλεγχος:**
Κάντε requests και δείτε τα logs στο console.

---

## Άσκηση 7: Request ID Tracking

**Στόχος:** Προσθήκη unique request ID σε κάθε request για debugging.

**Απαιτήσεις:**
1. Σε κάθε request:
   - Generate UUID ως request ID
   - Αποθηκεύστε το στο `g.request_id`
   - Προσθέστε το στο response header `X-Request-ID`
2. Τροποποιήστε το logging να περιλαμβάνει το request ID
3. Αν ο client στέλνει `X-Request-ID` header, χρησιμοποιήστε αυτό αντί να φτιάξετε νέο

**Σκελετός κώδικα:**
<details> 

```python
# app/middleware.py
import uuid
from flask import request, g

def register_middleware(app):
    
    @app.before_request
    def before_request():
        # Check if client sent request ID
        g.request_id = request.headers.get('X-Request-ID')
        if not g.request_id:
            g.request_id = str(uuid.uuid4())
        
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        # Add request ID to response headers
        response.headers['X-Request-ID'] = g.request_id
        
        # TODO: Update logging to include request_id
        
        return response
```
</details> 

**Έλεγχος:**
```bash
curl -v http://localhost:5000/api/v1/users
# Check for X-Request-ID in response headers

curl -v -H "X-Request-ID: my-custom-id" http://localhost:5000/api/v1/users
# Should echo back the same ID
```

---

## Άσκηση 8: Rate Limiting Middleware

**Στόχος:** Υλοποίηση simple rate limiting (in-memory).

**Απαιτήσεις:**
1. Περιορισμός: 10 requests per minute ανά IP address
2. Χρησιμοποιήστε dictionary για tracking:
   ```python
   # {ip_address: [timestamp1, timestamp2, ...]}
   ```
3. Αν ξεπεραστεί το limit:
   - Return 429 Too Many Requests
   - Header: `Retry-After: 60`
4. Clean up old timestamps (older than 1 minute)

**Σκελετός κώδικα:**
<details> 

```python
# app/middleware.py
from collections import defaultdict
from datetime import datetime, timedelta
from flask import request, jsonify

# In-memory storage: {ip: [timestamps]}
request_history = defaultdict(list)
RATE_LIMIT = 10  # requests
RATE_WINDOW = 60  # seconds

def register_middleware(app):
    
    @app.before_request
    def rate_limit():
        ip = request.remote_addr
        now = datetime.now()
        
        # TODO: Clean old timestamps
        # TODO: Check if limit exceeded
        # TODO: Add current timestamp
        # TODO: Return 429 if needed
        
        pass
```
</details> 

**Έλεγχος:**
```bash
# Στείλτε 15 requests γρήγορα
for i in {1..15}; do curl http://localhost:5000/api/v1/users; done
```
