# Week 2: Advanced Web Application Development Technologies

> 🇬🇷 [Ελληνική έκδοση](README.md)

## **Exercise 1: Environment Setup**
**Goal**: Install a Python environment and the basic libraries

### Steps:
1. **Python Installation Check**:
   ```bash
   python3 --version
   pip3 --version
   ```

2. **Virtual Environment Creation**:
   ```bash
   python3 -m venv http_lab
   source http_lab/bin/activate        # macOS/Linux
   # http_lab\Scripts\activate.bat     # Windows (cmd)
   # http_lab\Scripts\Activate.ps1     # Windows (PowerShell)
   ```

3. **Package Installation**:
   ```bash
   pip install requests beautifulsoup4 pandas matplotlib
   pip list  # Verify installation
   ```

4. **Test Script** (`test_setup.py`):
   ```python
   import requests
   print("Environment setup successful!")
   print(f"Requests version: {requests.__version__}")
   ```
   Run it:
   ```bash
   python test_setup.py
   ```

**Expected result**: The message "Environment setup successful!" and the version of the requests library are printed.

---

## **Exercise 2: First HTTP Request**
**Goal**: First GET request to a public API

### Code:
```python
import json
import requests

# Simple GET request
response = requests.get('https://httpbin.org/json', timeout=10)

print("=== HTTP Response Analysis ===")
print(f"Status Code: {response.status_code}")
print(f"Content-Type: {response.headers['content-type']}")
print(f"Response Time: {response.elapsed.total_seconds()} seconds")
print(f"Response Size: {len(response.content)} bytes")

# Pretty print JSON
data = response.json()
print("\nJSON Response:")
print(json.dumps(data, indent=2))
```

### Questions:
1. What does status code 200 mean?
2. How long did the request take?
3. What type of data does the API return?

**Expected result**: Successful JSON response with metadata analysis

---

## **Exercise 3: URL Parameters**
**Goal**: Using query parameters in GET requests

Run the program below and observe the results.
+ Compare the URLs produced by the “manual” method (Method 1) with those produced by the “smart” method (Method 2).
+ Identify the difference in how special characters are encoded (e.g. &, >, spaces). What does the server receive in each case?

**Comprehension Questions**
+ What are the advantages of using the params argument instead of building the URL manually?
+ How are special characters encoded in query strings (e.g. “python & django”)?
+ How could you send lists or multiple values for the same parameter key?
+ What happens if you change base_url to an endpoint that does not accept GET parameters?

**Extension**
* Create a function make_request(base_url, params) that:
    * Accepts a base URL and a dictionary of parameters.
    * Performs the request with requests.get().
    * Returns the JSON result.

Call the function with different sets of parameters (e.g. other names, cities or filters).

<details>
<summary><b>Code</b></summary>

```python
import requests

# Test different parameter methods
base_url = 'https://httpbin.org/get'

# Method 1: Manual URL construction
response1 = requests.get(f'{base_url}?name=Γιάννης&city=Αθήνα&age=25', timeout=10)

# Method 2: Using params dictionary (preferred)
params = {
    'name': 'Μαρία',
    'city': 'Θεσσαλονίκη',
    'age': 30,
    'interests': ['programming', 'music', 'travel']
}
response2 = requests.get(base_url, params=params, timeout=10)

print("=== Method 1 Results ===")
print(f"Final URL: {response1.url}")
print(f"Args received: {response1.json()['args']}")

print("\n=== Method 2 Results ===")
print(f"Final URL: {response2.url}")
print(f"Args received: {response2.json()['args']}")

# Special characters handling
special_params = {
    'search': 'python & django',
    'filter': 'price>100',
    'sort': 'date desc'
}

# Manual construction with special characters (what goes wrong?)
manual_url = f"{base_url}?search=python & django&filter=price>100&sort=date desc"
response3 = requests.get(manual_url, timeout=10)
print("\n=== Special Characters: Manual ===")
print(f"Final URL: {response3.url}")
print(f"Args received: {response3.json()['args']}")

# Same parameters via params dictionary
response4 = requests.get(base_url, params=special_params, timeout=10)
print("\n=== Special Characters: params ===")
print(f"Encoded URL: {response4.url}")
print(f"Args received: {response4.json()['args']}")
```

</details>

---

## **Exercise 4: Headers Customization**
**Goal**: Understanding and using HTTP headers

Run the program and study the output.
+ Observe which headers were sent by the client and which ones the server returned. (httpbin.org/headers echoes the headers as it received them — you may also see some added by intermediate servers, e.g. `X-Amzn-Trace-Id`.)
+ Identify the differences between Request Headers and Response Headers.
+ Does the response change when you use a different User-Agent?

**Comprehension Questions**
+ What is the role of the User-Agent field? How can it affect a server's response?
+ What information does the Accept-Language header carry?
+ What does a header starting with X- mean (such as X-Custom-Header or X-Student-ID)?
+ What information do the response headers content-type, server, date and content-length provide?
+ What changes if you remove the custom headers from the request entirely?

<details>
<summary><b>Code</b></summary>

```python
import requests

# Custom headers example
custom_headers = {
    'User-Agent': 'HTTPLabWorkshop/1.0 (Educational Purpose)',
    'Accept': 'application/json',
    'Accept-Language': 'el-GR,en-US;q=0.9',
    'X-Custom-Header': 'LabExercise4',
    'X-Student-ID': '12345'
}

response = requests.get('https://httpbin.org/headers', headers=custom_headers, timeout=10)

print("=== Request Headers Sent (as received by the server) ===")
received_headers = response.json()['headers']
for header, value in received_headers.items():
    print(f"{header}: {value}")

print("\n=== Response Headers Received ===")
interesting_headers = ['content-type', 'server', 'date', 'content-length']
for header in interesting_headers:
    if header in response.headers:
        print(f"{header}: {response.headers[header]}")

# Browser simulation
browser_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}
browser_response = requests.get('https://httpbin.org/user-agent', headers=browser_headers, timeout=10)
print("\n=== Browser Simulation ===")
print(f"Detected User-Agent: {browser_response.json()['user-agent']}")

# Default User-Agent of the requests library
default_response = requests.get('https://httpbin.org/user-agent', timeout=10)
print(f"Default requests User-Agent: {default_response.json()['user-agent']}")
```

</details>

---

## **Exercise 5: POST Requests with JSON**
**Goal**: Sending data with POST requests

Run the program and study the output.
+ Observe how the headers change when you use json= versus data=.
+ Check how the Greek data appears on the server (UTF-8 encoding).
+ Try to deliberately “break” the JSON to see how the server handles it.

**Comprehension Questions**
+ What is the difference between requests.post(..., json=data) and requests.post(..., data=json_string)?
+ Why does requests automatically set the header Content-Type: application/json when we use json=?
+ How does the ensure_ascii=False parameter help when encoding JSON containing Greek characters?
+ What is the result of sending “invalid” JSON (with single quotes)? What do you see in the server's response? Why is no exception raised on the client?
+ How could you add error handling for cases where the server does not return valid JSON?

<details>
<summary><b>Code</b></summary>

```python
import requests
import json
from datetime import datetime

# Student data to send
student_data = {
    'name': 'Ελένη Παπαδοπούλου',
    'email': 'eleni@university.gr',
    'student_id': 'CS2021123',
    'courses': ['Data Structures', 'Web Technologies', 'Databases'],
    'semester': 6,
    'gpa': 8.5,
    'enrollment_date': datetime.now().isoformat(),
    'is_active': True
}

# Method 1: Using json parameter (automatic header setting)
print("=== Method 1: JSON Parameter ===")
response1 = requests.post('https://httpbin.org/post', json=student_data, timeout=10)
print(f"Status: {response1.status_code}")
print(f"Content-Type sent: {response1.request.headers['content-type']}")
print(f"Raw body sent: {response1.request.body}")
print(f"Data received by server: {response1.json()['json']}")

# Method 2: Manual JSON encoding
print("\n=== Method 2: Manual JSON ===")
json_string = json.dumps(student_data, ensure_ascii=False)  # Keep Greek characters as-is
headers = {'Content-Type': 'application/json; charset=utf-8'}
response2 = requests.post('https://httpbin.org/post', data=json_string, headers=headers, timeout=10)
print(f"Manual encoding successful: {response2.status_code == 200}")
print(f"Raw body sent: {json_string}")
print(f"Data received by server: {response2.json()['json']}")

# Invalid JSON: the client does not validate it - the server receives it as-is
print("\n=== Invalid JSON ===")
invalid_data = "{'invalid': 'json syntax'}"  # Single quotes = invalid JSON
response3 = requests.post('https://httpbin.org/post', data=invalid_data,
                          headers={'Content-Type': 'application/json'}, timeout=10)
result = response3.json()
print(f"Status: {response3.status_code}")
print(f"Raw data received by server: {result['data']}")
print(f"Parsed JSON on server: {result['json']}")  # None -> the server could not parse it
```

</details>

---

## **Exercise 6: Form Data POST**
**Goal**: Sending form data (application/x-www-form-urlencoded) and files (multipart/form-data)

Run the program and study the output.
+ How does the form data appear in the httpbin.org/post result?
+ How does the Content-Type change when you add files? What is the `boundary`?
+ Which fields are treated as “form fields” and which as “file uploads”?

**Comprehension Questions**
+ What is the difference between the data= and files= parameters of requests.post()?
+ Why does the Content-Type automatically change to multipart/form-data when uploading files?
+ What advantages does multipart/form-data have over application/x-www-form-urlencoded?
+ How could you send more than one file in the same request?
+ What happens if you try to send a binary file (.jpg, .zip) without specifying a MIME type?

<details>
<summary><b>Code</b></summary>

```python
import requests

# Traditional form data
form_data = {
    'username': 'student123',
    'password': 'secretpassword',
    'email': 'student@university.gr',
    'remember_me': 'on',
    'terms_accepted': 'true'
}

print("=== Form Data POST ===")
response = requests.post('https://httpbin.org/post', data=form_data, timeout=10)
print(f"Status: {response.status_code}")
print(f"Content-Type: {response.request.headers.get('content-type')}")
print(f"Raw body sent: {response.request.body}")
print(f"Form data received: {response.json()['form']}")

# File upload simulation
print("\n=== File Upload Simulation ===")
files = {
    'assignment': ('homework.txt', 'This is my homework content', 'text/plain'),
    'screenshot': ('screen.png', b'\x89PNG\r\n\x1a\n...', 'image/png')
}
additional_data = {
    'student_id': 'CS2021123',
    'course': 'Web Technologies'
}

upload_response = requests.post('https://httpbin.org/post',
                                files=files,
                                data=additional_data,
                                timeout=10)

print(f"Upload status: {upload_response.status_code}")
print(f"Files received: {list(upload_response.json()['files'].keys())}")
print(f"Form data: {upload_response.json()['form']}")

# Compare Content-Types (as actually sent by requests)
json_response = requests.post('https://httpbin.org/post', json=form_data, timeout=10)
print("\n=== Content-Type Comparison ===")
print(f"JSON POST Content-Type:   {json_response.request.headers['content-type']}")
print(f"Form POST Content-Type:   {response.request.headers['content-type']}")
print(f"File Upload Content-Type: {upload_response.request.headers['content-type']}")
```

</details>

---

## **Exercise 7: Error Handling Basics**
**Goal**: Handling HTTP errors and exceptions

Run the program and study the output.

**Comprehension Questions**
+ What is the difference between HTTPError and ConnectionError?
+ What does raise_for_status() do and why is it useful?
+ How does the timeout parameter work?
+ What happens if we remove the try/except block?
+ What kinds of exceptions does requests.exceptions.RequestException cover?

<details>
<summary><b>Code</b></summary>

```python
import requests

# Test different error scenarios
test_urls = {
    'valid': 'https://httpbin.org/json',
    'not_json': 'https://httpbin.org/html',
    'not_found': 'https://httpbin.org/status/404',
    'server_error': 'https://httpbin.org/status/500',
    'timeout_test': 'https://httpbin.org/delay/10',
    'invalid_domain': 'https://this-domain-does-not-exist-12345.com'
}

def test_url(name, url):
    print(f"\n=== Testing {name.upper()} ===")
    try:
        response = requests.get(url, timeout=3)
        print(f"📨 Status received: {response.status_code}")

        # Check for HTTP errors (4xx, 5xx)
        response.raise_for_status()
        print("✅ No HTTP errors")

        # Try to parse JSON
        try:
            data = response.json()
            print(f"✅ JSON parsed successfully: {len(data)} top-level key(s)")
        except ValueError:
            print("⚠️  Response is not valid JSON")

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"   Status Code: {e.response.status_code}")

    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Cannot reach server")

    except requests.exceptions.Timeout:
        print("❌ Timeout: Request took longer than 3 seconds")

    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")

# Test all scenarios
for name, url in test_urls.items():
    test_url(name, url)

print("\n=== Summary ===")
print("✅ = Success, ⚠️ = Warning, ❌ = Error")
```

</details>

---

## **Exercise 8: Timeout Configuration**
**Goal**: Understanding and managing timeouts

Run the program and study the output.

**Comprehension Questions**
+ What is the difference between a connect timeout and a read timeout?
+ Why is it dangerous not to set a timeout on HTTP requests?
+ How can we measure the duration of an HTTP request in Python?
+ Which exception types does requests raise when there are delays?
+ How do proper timeout settings improve a client's reliability and performance?

<details>
<summary><b>Code</b></summary>

```python
import requests
import time
from datetime import datetime

def test_timeout_scenarios():
    scenarios = [
        ('No timeout (dangerous)', None),
        ('Short timeout (3s)', 3),
        ('Long timeout (30s)', 30),
        ('Tuple timeout (connect=2, read=10)', (2, 10)),
    ]

    test_url = 'https://httpbin.org/delay/5'  # 5 second delay

    for description, timeout_value in scenarios:
        print(f"\n=== {description} ===")
        start_time = datetime.now()

        try:
            if timeout_value is None:
                print("⚠️  SKIPPING no-timeout test for safety")
                continue

            response = requests.get(test_url, timeout=timeout_value)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            print(f"✅ Success in {duration:.2f} seconds")
            print(f"   Status: {response.status_code}")

        except requests.exceptions.Timeout:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            print(f"❌ Timeout after {duration:.2f} seconds")

        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {e}")

def demonstrate_best_practices():
    print("\n=== Best Practices Demo ===")

    # Good timeout configuration
    CONNECT_TIMEOUT = 3  # 3 seconds for connection
    READ_TIMEOUT = 10    # 10 seconds for reading

    urls = [
        'https://httpbin.org/json',           # Fast response
        'https://httpbin.org/delay/2',        # Medium response
        'https://httpbin.org/delay/8',        # Slow response (still within READ_TIMEOUT)
        'https://httpbin.org/delay/12',       # Too slow (exceeds READ_TIMEOUT)
    ]

    for url in urls:
        start = time.perf_counter()
        try:
            response = requests.get(url, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
            duration = time.perf_counter() - start
            print(f"✅ {url}: {response.status_code} in {duration:.2f}s")
        except requests.exceptions.Timeout:
            duration = time.perf_counter() - start
            print(f"⏰ {url}: Timed out after {duration:.2f}s")
        except requests.exceptions.RequestException as e:
            print(f"❌ {url}: {e}")

test_timeout_scenarios()
demonstrate_best_practices()
```

</details>

---

## **Exercise 9: JSON Processing**
**Goal**: Working with JSON responses from APIs

**Develop a Python program that:**
+ Reads a user's data from the JSONPlaceholder API (/users/1).
+ Safely navigates nested JSON fields.
+ Handles JSON arrays (/users), computes sets, filters data and displays statistics.
+ Uses functions for safe access to fields that may be missing.

**Comprehension Questions**
+ What is nested JSON and how can we navigate its fields in Python?
+ What is the benefit of the safe_get function over direct access (user['company']['name'])?
+ How can we filter JSON arrays for specific values (e.g. email domains)?
+ How can we compute statistics or sets from JSON arrays (e.g. unique cities)?
+ What happens if a field is missing from the API's JSON?

<details>
<summary><b>Code</b></summary>

```python
import requests
from collections import Counter

BASE_URL = 'https://jsonplaceholder.typicode.com'

def fetch_json(path):
    response = requests.get(f'{BASE_URL}{path}', timeout=10)
    response.raise_for_status()
    return response.json()

def explore_json_api():
    print("=== JSON Placeholder API Exploration ===")

    # Fetch user data
    user = fetch_json('/users/1')

    print("=== Basic User Information ===")
    print(f"Name: {user['name']}")
    print(f"Email: {user['email']}")
    print(f"Phone: {user['phone']}")

    # Navigate nested JSON
    print("\n=== Address Information ===")
    address = user['address']
    print(f"Street: {address['street']} {address['suite']}")
    print(f"City: {address['city']}")
    print(f"Zipcode: {address['zipcode']}")

    # Deeply nested data
    geo = address['geo']
    print(f"Coordinates: {geo['lat']}, {geo['lng']}")

    # Company information
    print("\n=== Company Information ===")
    company = user['company']
    print(f"Company: {company['name']}")
    print(f"Catchphrase: {company['catchPhrase']}")

def safe_json_navigation():
    print("\n=== Safe JSON Navigation ===")

    def safe_get(data, *keys, default=None):
        """Safely navigate nested dictionaries"""
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return default
        return data

    user = fetch_json('/users/1')

    # Safe navigation examples
    company_name = safe_get(user, 'company', 'name', default='Unknown Company')
    geo_lat = safe_get(user, 'address', 'geo', 'lat', default='0')
    website = safe_get(user, 'website', default='No website')

    print(f"Company: {company_name}")
    print(f"Latitude: {geo_lat}")
    print(f"Website: {website}")

    # Handle missing data
    missing_field = safe_get(user, 'social_media', 'twitter', default='Not provided')
    print(f"Twitter: {missing_field}")

def work_with_json_arrays():
    print("\n=== Working with JSON Arrays ===")

    # Fetch all users
    users = fetch_json('/users')

    print(f"Total users: {len(users)}")

    # Process array data
    print("\n=== Users Summary ===")
    for user in users[:3]:  # First 3 users
        print(f"ID: {user['id']}, Name: {user['name']}, City: {user['address']['city']}")

    # Data analysis
    cities = [user['address']['city'] for user in users]
    unique_cities = sorted(set(cities))
    print(f"\nUnique cities: {', '.join(unique_cities)}")

    # Statistics: email top-level domains (.biz, .org, ...)
    tlds = Counter(user['email'].rsplit('.', 1)[-1].lower() for user in users)
    print(f"Email TLDs: {dict(tlds)}")

    # Filter data
    biz_users = [user['name'] for user in users if user['email'].lower().endswith('.biz')]
    print(f".biz users ({len(biz_users)}): {', '.join(biz_users)}")

explore_json_api()
safe_json_navigation()
work_with_json_arrays()
```

</details>
