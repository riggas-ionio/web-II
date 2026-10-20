# Εβδομάδα 3: Προχωρημένες Τεχνολογίες Ανάπτυξης Εφαρμογών Διαδικτύου

> 🇬🇧 [English version](README.en.md)

> ⚠️ **GitHub API rate limit**: χωρίς authentication το GitHub επιτρέπει **60 αιτήματα/ώρα ανά IP**. Στο εργαστήριο πολλοί υπολογιστές βγαίνουν στο Internet από την ίδια IP, οπότε το όριο εξαντλείται γρήγορα (`403`). Αν συμβεί αυτό, δείτε την [Άσκηση 6](#άσκηση-6-authentication) για χρήση token (5000 αιτήματα/ώρα).

## **Άσκηση 1: Χρήση GitHub API**
**Στόχος**: Εργασία με πραγματικό API (GitHub)

1. Μελετήστε τη συνάρτηση `explore_github_api()`:
    + Εντοπίστε ποιο endpoint χρησιμοποιεί (https://api.github.com/repos/python/cpython).
    + Εκτελέστε το πρόγραμμα και καταγράψτε:
        + Το όνομα και τη γλώσσα του repository
        + Τον αριθμό αστεριών (stars) και forks
        + Την ημερομηνία τελευταίας ενημέρωσης (updated_at)
    + Δοκιμάστε να αλλάξετε το repository π.χ. σε: https://api.github.com/repos/pallets/flask και συγκρίνετε τα αποτελέσματα.

2. Μελετήστε πώς η συνάρτηση `get_user_repositories()` χρησιμοποιεί query parameters (sort, direction, per_page).
    + Αλλάξτε το username από 'octocat' σε δικό σας GitHub username.
    + Δοκιμάστε να αυξήσετε το per_page από 5 σε 10.
    + Πόσα repositories επιστρέφονται τώρα; Η απάντηση είναι πάντα JSON array — τι αλλάζει;

3. Το GitHub API περιορίζει τα αιτήματα (60 ανά ώρα χωρίς authentication).
    + Εκτελέστε τη συνάρτηση `handle_rate_limits()` και παρατηρήστε:
        + Το όριο (limit),
        + Τα υπόλοιπα αιτήματα (remaining),
        + Και πότε επαναφέρεται (reset).
    + Εντοπίστε τα headers X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset.
    + Τι θα συμβεί αν το remaining φτάσει στο 0;
    + Πώς μετατρέπεται το timestamp reset σε αναγνώσιμη ημερομηνία; (δείτε το `datetime.fromtimestamp()`)

4. Η συνάρτηση `search_repositories()` χρησιμοποιεί το endpoint /search/repositories με σύνθετο ερώτημα.
    + Παρατηρήστε το πεδίο 'q' μέσα στα params (π.χ. 'language:python machine learning').
    + Τι σημαίνει η σύνταξη language:python μέσα στο query;
    + Εκτελέστε τη συνάρτηση και παρατηρήστε τα top 3 αποτελέσματα.
    + Τροποποιήστε το query για να αναζητήσετε:
        + language:javascript web framework
        + language:rust compiler
    + Παρακολουθήστε πώς αλλάζουν τα αποτελέσματα (τίτλοι, αστέρια, γλώσσα).
    + Γιατί ο κώδικας ελέγχει αν το `description` είναι `None` πριν το «κόψει» στους 100 χαρακτήρες;

5. Προσθέστε logging (π.χ. logger.info()) αντί για print (δείτε και την [Άσκηση 7](#άσκηση-7-retry-logic-και-logging)).
6. Αποθηκεύστε τα αποτελέσματα σε αρχείο JSON.
7. Δημιουργήστε μια νέα συνάρτηση get_contributors(repo) που εμφανίζει τους 5 πρώτους contributors ενός repo (endpoint: `/repos/{owner}/{repo}/contributors`).

<details>
<summary><b>Κώδικας</b></summary>

```python
import requests
import json
from datetime import datetime

def explore_github_api():
    """Explore GitHub's public API without authentication"""

    print("=== GitHub API Exploration ===")

    # Get repository information
    repo_url = 'https://api.github.com/repos/python/cpython'
    response = requests.get(repo_url, timeout=10)

    if response.status_code == 200:
        repo = response.json()

        print("=== Repository Information ===")
        print(f"Name: {repo['name']}")
        print(f"Full Name: {repo['full_name']}")
        print(f"Description: {repo['description']}")
        print(f"Language: {repo['language']}")
        print(f"Stars: {repo['stargazers_count']:,}")
        print(f"Forks: {repo['forks_count']:,}")
        print(f"Open Issues: {repo['open_issues_count']:,}")
        print(f"Created: {repo['created_at']}")
        print(f"Last Updated: {repo['updated_at']}")
    else:
        print(f"Error: {response.status_code}")

def get_user_repositories():
    """Get public repositories for a user"""

    print("\n=== User Repositories ===")

    username = 'octocat'  # GitHub's mascot account
    url = f'https://api.github.com/users/{username}/repos'

    params = {
        'sort': 'updated',
        'direction': 'desc',
        'per_page': 5  # Limit to 5 repos
    }

    response = requests.get(url, params=params, timeout=10)

    if response.status_code == 200:
        repos = response.json()

        print(f"Recent repositories for {username}:")
        for repo in repos:
            print(f"  📁 {repo['name']}")
            print(f"     Language: {repo['language'] or 'Not specified'}")
            print(f"     Stars: {repo['stargazers_count']}")
            print(f"     Updated: {repo['updated_at']}")
            print()
    else:
        print(f"Error fetching repositories: {response.status_code}")

def handle_rate_limits():
    """Demonstrate rate limiting handling"""

    print("=== Rate Limiting Information ===")

    # Check current rate limit status (this call does not count against the limit)
    response = requests.get('https://api.github.com/rate_limit', timeout=10)

    if response.status_code == 200:
        rate_limit = response.json()
        core = rate_limit['resources']['core']

        print(f"Rate Limit: {core['limit']} requests per hour")
        print(f"Remaining: {core['remaining']}")
        reset_time = datetime.fromtimestamp(core['reset'])
        print(f"Resets at: {reset_time}")

        # Check if we're close to the limit
        if core['remaining'] < 10:
            print("⚠️  Warning: Approaching rate limit!")
        else:
            print("✅ Rate limit OK")

    # Show headers from any API response
    test_response = requests.get('https://api.github.com/users/octocat', timeout=10)
    print("\n=== Rate Limit Headers ===")
    rate_headers = {
        'X-RateLimit-Limit': test_response.headers.get('X-RateLimit-Limit'),
        'X-RateLimit-Remaining': test_response.headers.get('X-RateLimit-Remaining'),
        'X-RateLimit-Reset': test_response.headers.get('X-RateLimit-Reset')
    }

    for header, value in rate_headers.items():
        if value:
            print(f"{header}: {value}")

def search_repositories():
    """Search GitHub repositories"""

    print("\n=== Repository Search ===")

    search_url = 'https://api.github.com/search/repositories'
    params = {
        'q': 'language:python machine learning',
        'sort': 'stars',
        'order': 'desc',
        'per_page': 3
    }

    response = requests.get(search_url, params=params, timeout=10)

    if response.status_code == 200:
        results = response.json()

        print(f"Total found: {results['total_count']:,} repositories")
        print(f"Showing top {len(results['items'])} results:")

        for repo in results['items']:
            description = repo['description'] or 'No description'
            print(f"\n🌟 {repo['full_name']}")
            print(f"   Description: {description[:100]}...")
            print(f"   Stars: {repo['stargazers_count']:,}")
            print(f"   Language: {repo['language']}")
            print(f"   URL: {repo['html_url']}")
    else:
        print(f"Search failed: {response.status_code}")

# Run all functions
explore_github_api()
get_user_repositories()
handle_rate_limits()
search_repositories()
```

</details>

---

## **Άσκηση 2: Σελιδοποίηση**
**Στόχος**: Κατανόηση του γιατί τα APIs επιστρέφουν τα δεδομένα τμηματικά (σε σελίδες) και ποιοι είναι οι βασικοί τύποι σελιδοποίησης.

1. Σελιδοποίηση με αριθμό σελίδας (page-based)
    + Εκτελέστε τη συνάρτηση `simple_pagination_example()`.
    + Παρατηρήστε πώς γίνεται κάθε αίτημα προς το endpoint:
    https://jsonplaceholder.typicode.com/posts?_page=1&_limit=20
    + Σημειώστε:
        + Πόσες σελίδες λαμβάνονται συνολικά.
        + Τι συμβαίνει όταν δεν υπάρχουν άλλα δεδομένα (`if not posts:`).
        + Τι δείχνει το header `X-Total-Count` που εκτυπώνεται;
    + Αυξήστε το page_size από 20 σε 50 και δείτε πώς αλλάζει το αποτέλεσμα.

2. Σελιδοποίηση με Link Headers
    + Μελετήστε τη συνάρτηση `parse_link_header()`.
    + Τι μορφή έχει το header Link;
    + Πώς απομονώνονται οι παράμετροι rel="next" και rel="last";
    + Εκτελέστε τη συνάρτηση `github_pagination_example()`.
    + Παρατηρήστε πόσες σελίδες επιστρέφονται (μέχρι 3 για λόγους demo).
    + Εντοπίστε το URL της επόμενης σελίδας (Next page URL:).
    + Συγκρίνετε το αποτέλεσμα της `parse_link_header()` με το `response.links`, που παρέχει έτοιμο η βιβλιοθήκη requests.
    + Δοκιμάστε να αυξήσετε το per_page από 5 σε 10.

3. Cursor-based σελιδοποίηση
    + Ανοίξτε στον browser το https://api.github.com/users?per_page=3&page=2 και μετά το https://api.github.com/users?per_page=3&page=1. Τι παρατηρείτε;
    + Δείτε το header `Link` της απάντησης: ποια παράμετρος χρησιμοποιείται αντί για `page`;
    + Γιατί ένας βρόχος που απλά αυξάνει το `page` δεν θα τελείωνε ποτέ σε αυτό το endpoint;

<details>
<summary><b>Κώδικας</b></summary>

```python
import requests
import time

def simple_pagination_example():
    """Handle simple page-based pagination"""

    print("=== Simple Pagination (JSONPlaceholder) ===")

    base_url = 'https://jsonplaceholder.typicode.com/posts'
    all_posts = []
    page = 1
    page_size = 20

    while True:
        params = {
            '_page': page,
            '_limit': page_size
        }

        response = requests.get(base_url, params=params, timeout=10)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            break

        posts = response.json()

        if not posts:  # Empty page means we're done
            break

        all_posts.extend(posts)
        print(f"Page {page}: Retrieved {len(posts)} posts "
              f"(X-Total-Count: {response.headers.get('X-Total-Count')})")

        # Check if we got fewer than page_size (last page)
        if len(posts) < page_size:
            break

        page += 1
        time.sleep(0.1)  # Be nice to the API

    print(f"Total posts retrieved: {len(all_posts)}")

def github_pagination_example():
    """Handle GitHub-style Link header pagination"""

    print("\n=== GitHub Pagination (Link Headers) ===")

    def parse_link_header(link_header):
        """Parse GitHub-style Link header"""
        links = {}
        if not link_header:
            return links

        for link in link_header.split(','):
            url, rel = link.strip().split(';')
            url = url.strip('<>')
            rel = rel.strip().split('=')[1].strip('"')
            links[rel] = url
        return links

    url = 'https://api.github.com/users/octocat/repos'
    params = {'per_page': 5}  # Small page size for demo
    all_repos = []
    page_count = 0

    while url and page_count < 3:  # Limit to 3 pages for demo
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            break

        repos = response.json()
        all_repos.extend(repos)
        page_count += 1

        print(f"Page {page_count}: {len(repos)} repositories")

        # Parse Link header for next page
        link_header = response.headers.get('Link')
        print(f"Link header: {link_header}")
        links = parse_link_header(link_header)
        print(f"parse_link_header(): {links}")
        print(f"response.links:      {response.links}")

        url = links.get('next')  # URL for next page
        params = None  # params are included in the next URL

        if url:
            print(f"Next page URL: {url}")
        else:
            print("No more pages")
            break

    print(f"Total repositories: {len(all_repos)}")

simple_pagination_example()
github_pagination_example()
```

</details>

---

## **Άσκηση 3: File Upload & Download**
**Στόχος**: File Upload & Download μέσω HTTP

1. Δημιουργία Δοκιμαστικών Αρχείων (`create_sample_files`)
    + Εκτελέστε το πρόγραμμα και δείτε ποιο path εκτυπώνεται («Sample files created in:»).
    + Ανοίξτε τα αρχεία στον editor σας και εξετάστε το περιεχόμενο.
    + Ελέγξτε πώς χρησιμοποιούνται Path, tempfile.mkdtemp() και write_text() / write_bytes().

2. Ανέβασμα Ενός Αρχείου (`single_file_upload`)
    + Εκτελέστε τη συνάρτηση και παρατηρήστε την εκτύπωση “Upload status: 200”.
    + Εξετάστε τη διαφορά μεταξύ:
        + Απλού upload (files = {'file': f})
        + Upload με προσαρμοσμένο όνομα αρχείου, content-type και metadata.
    + Παρατηρήστε στο αποτέλεσμα result['files'] και result['form'] τι στάλθηκε.

3. Ανέβασμα Πολλαπλών Αρχείων (`multiple_file_upload`)
    + Εκτελέστε τη συνάρτηση multiple_file_upload().
    + Παρατηρήστε το λεξικό files_data — κάθε αρχείο είναι πεδίο του multipart request.
    + Πώς επιλέγεται ο τύπος MIME κάθε αρχείου; (δείτε το `mimetypes.guess_type()`)
    + Δείτε στην εκτύπωση πόσα αρχεία στάλθηκαν και τα ονόματά τους.
    + Εντοπίστε πώς προστίθενται επιπλέον δεδομένα (form_data).

4. Κατέβασμα Μικρού Αρχείου (`download_small_file`)
    + Εκτελέστε τη συνάρτηση download_small_file().
    + Ελέγξτε το αρχείο downloaded_post.json που δημιουργείται.
    + Παρατηρήστε το μέγεθος και περιεχόμενο του αρχείου.
    + Εντοπίστε πώς μετατρέπεται η απάντηση response.text σε Python dict. Ποια συντόμευση προσφέρει το requests για το ίδιο;

5. Μεγάλα Αρχεία με Streaming (`download_large_file_streaming`)
    + Εκτελέστε τη συνάρτηση και δείτε την προοδευτική εκτύπωση “Downloaded: X bytes”.
    + Ελέγξτε το τελικό αρχείο streamed_file.dat.
    + Δοκιμάστε να αλλάξετε το chunk_size (π.χ. σε 512 ή 1024) και παρατηρήστε τη διαφορά.

6. Download με Progress Bar (`download_with_progress`)
    + Εκτελέστε τη συνάρτηση και παρακολουθήστε το ποσοστό ολοκλήρωσης.
    + Παρατηρήστε πώς χρησιμοποιείται το content-length header για τον υπολογισμό του progress.
    + Αλλάξτε το URL ώστε να κατεβάζει μεγαλύτερο αρχείο (π.χ. https://httpbin.org/bytes/20480).

7. Καθαρισμός Αρχείων (`cleanup_files`)
    + Η συνάρτηση εκτελείται στο τέλος, μετά τις λήψεις.
    + Επιβεβαιώστε ότι τα αρχεία και ο προσωρινός φάκελος έχουν διαγραφεί.
    + Σημειώστε πώς το Path.unlink(missing_ok=True) διαχειρίζεται μη υπάρχοντα αρχεία και τι κάνει το shutil.rmtree().

<details>
<summary><b>Κώδικας</b></summary>

```python
import requests
import json
import mimetypes
import shutil
import tempfile
from pathlib import Path

def create_sample_files():
    """Create sample files for testing"""

    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())

    # Text file
    text_file = temp_dir / 'sample.txt'
    text_file.write_text('This is a sample text file for HTTP upload testing.\nLine 2 content.')

    # JSON file
    json_file = temp_dir / 'data.json'
    sample_data = {
        'name': 'Test Data',
        'values': [1, 2, 3, 4, 5],
        'metadata': {'created': '2024-01-15', 'type': 'demo'}
    }
    json_file.write_text(json.dumps(sample_data, indent=2))

    # Binary file (fake image)
    binary_file = temp_dir / 'sample.dat'
    binary_file.write_bytes(b'\x89PNG\r\n\x1a\n' + b'fake image data' * 100)

    print(f"Sample files created in: {temp_dir}")
    return temp_dir, [text_file, json_file, binary_file]

def single_file_upload(files):
    """Upload a single file"""

    print("\n=== Single File Upload ===")

    text_file = files[0]

    # Method 1: Simple file upload
    with open(text_file, 'rb') as f:
        files_data = {'file': f}
        response = requests.post('https://httpbin.org/post', files=files_data, timeout=10)

    print(f"Upload status: {response.status_code}")
    result = response.json()
    print(f"Filename received: {list(result['files'].keys())}")

    # Method 2: File upload with custom filename and content-type
    with open(text_file, 'rb') as f:
        files_data = {
            'document': ('my_document.txt', f, 'text/plain')
        }
        additional_data = {
            'description': 'Sample document upload',
            'category': 'test'
        }
        response = requests.post('https://httpbin.org/post',
                                 files=files_data,
                                 data=additional_data,
                                 timeout=10)

    print("\n=== Upload with Metadata ===")
    result = response.json()
    print(f"Files: {list(result['files'].keys())}")
    print(f"Form data: {result['form']}")

def multiple_file_upload(files):
    """Upload multiple files"""

    print("\n=== Multiple File Upload ===")

    # Prepare multiple files
    files_data = {}
    for i, file_path in enumerate(files):
        mime_type = mimetypes.guess_type(file_path.name)[0] or 'application/octet-stream'
        files_data[f'file_{i}'] = (file_path.name, file_path.read_bytes(), mime_type)
        print(f"  {file_path.name}: {mime_type}")

    # Additional form data
    form_data = {
        'upload_type': 'batch',
        'user_id': '12345',
        'timestamp': '2024-01-15T10:30:00Z'
    }

    response = requests.post('https://httpbin.org/post',
                             files=files_data,
                             data=form_data,
                             timeout=10)

    print(f"Batch upload status: {response.status_code}")
    result = response.json()
    print(f"Files uploaded: {len(result['files'])}")
    print(f"File names: {list(result['files'].keys())}")
    print(f"Form data: {result['form']}")

def download_small_file():
    """Download a small file"""

    print("\n=== Small File Download ===")

    # Download JSON data
    response = requests.get('https://jsonplaceholder.typicode.com/posts/1', timeout=10)

    if response.status_code == 200:
        # Save to file
        download_path = Path('downloaded_post.json')
        download_path.write_text(response.text, encoding='utf-8')

        print(f"✅ Downloaded to: {download_path}")
        print(f"File size: {download_path.stat().st_size} bytes")

        # Verify content
        data = json.loads(response.text)
        print(f"Post title: {data['title']}")
    else:
        print(f"Download failed: {response.status_code}")

def download_large_file_streaming():
    """Download large file with streaming"""

    print("\n=== Streaming Download ===")

    # httpbin "drips" 1024 bytes slowly over 2 seconds
    url = 'https://httpbin.org/drip?duration=2&numbytes=1024'

    with requests.get(url, stream=True, timeout=10) as response:
        if response.status_code != 200:
            print(f"Streaming download failed: {response.status_code}")
            return

        download_path = Path('streamed_file.dat')
        total_size = 0

        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=256):
                if chunk:  # Filter out keep-alive chunks
                    f.write(chunk)
                    total_size += len(chunk)
                    print(f"Downloaded: {total_size} bytes", end='\r')

    print(f"\n✅ Streaming download complete: {total_size} bytes")

    # Verify file
    actual_size = download_path.stat().st_size
    print(f"File on disk: {actual_size} bytes")

def download_with_progress():
    """Download with progress tracking"""

    print("\n=== Download with Progress ===")

    def download_with_progress_bar(url, filename):
        with requests.get(url, stream=True, timeout=10) as response:
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))

            downloaded = 0
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"Progress: {progress:.1f}% ({downloaded}/{total_size} bytes)", end='\r')
                        else:
                            print(f"Downloaded: {downloaded} bytes", end='\r')

        print(f"\n✅ Download complete: {filename}")
        return downloaded

    # Download example file
    url = 'https://httpbin.org/bytes/5120'  # 5KB file
    downloaded_bytes = download_with_progress_bar(url, 'progress_download.dat')
    print(f"Total downloaded: {downloaded_bytes} bytes")

def cleanup_files(temp_dir):
    """Clean up created files"""

    print("\n=== Cleanup ===")
    files_to_remove = [
        'downloaded_post.json',
        'streamed_file.dat',
        'progress_download.dat'
    ]

    for filename in files_to_remove:
        try:
            Path(filename).unlink(missing_ok=True)
            print(f"🗑️  Cleaned up: {filename}")
        except Exception as e:
            print(f"Could not remove {filename}: {e}")

    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"🗑️  Removed temp folder: {temp_dir}")

# Run all examples
temp_dir, sample_files = create_sample_files()
single_file_upload(sample_files)
multiple_file_upload(sample_files)
download_small_file()
download_large_file_streaming()
download_with_progress()
cleanup_files(temp_dir)
```

</details>

---

## **Άσκηση 4: Weather API**
**Στόχος**: Επικοινωνία με εξωτερικό REST API (OpenWeatherMap) με χρήση API key.

1. Ρύθμιση και Εισαγωγή στο API
    + Το script χρησιμοποιεί το OpenWeatherMap API:
    https://openweathermap.org/api
    + Για να το χρησιμοποιήσετε:
        + Δημιουργήστε έναν δωρεάν λογαριασμό.
        + Πάρτε το API key από το dashboard (_ένα νέο key μπορεί να χρειαστεί έως και 1-2 ώρες για να ενεργοποιηθεί· μέχρι τότε θα παίρνετε `401`_).
        + Ορίστε το ως περιβαλλοντική μεταβλητή:
            + macOS/Linux: `export WEATHER_API_KEY=your_api_key_here`
            + Windows (cmd): `set WEATHER_API_KEY=your_api_key_here`
            + Windows (PowerShell): `$env:WEATHER_API_KEY="your_api_key_here"`
        + Αποθηκεύστε τον κώδικα ως `weather_api_demo.py` και εκτελέστε τον **στο ίδιο τερματικό**:
          `python weather_api_demo.py`
2. Μελετήστε και κατανοήστε την κλάση WeatherAPI:
    + Γιατί χρησιμοποιείται requests.Session() αντί για requests.get() κάθε φορά;
    + Γιατί το timeout περνιέται σε κάθε `self.session.get(...)`; (Υπόδειξη: το `requests.Session` _δεν_ έχει ρύθμιση timeout για όλα τα αιτήματα.)
    + Τι περιλαμβάνει το dictionary params που αποστέλλεται στο API; Πώς στέλνεται το API key;
    + Ποια είναι η διαφορά μεταξύ raise_for_status() και χειρισμού response.status_code;

3. Συγκρίνετε τις `demo_weather_api` και `demo_without_api_key`
    + Εκτελέστε τον κώδικα με και χωρίς API KEY.
    + Δοκιμάστε και με λάθος API key: τι μήνυμα εμφανίζεται;

4. Αποθήκευση Δεδομένων (`save_weather_data`)
    + Εκτελέστε τη συνάρτηση με ενεργό API key.
    + Παρατηρήστε τα δύο αρχεία που δημιουργούνται:
        `weather_data_YYYYMMDD_HHMMSS.json`
        `weather_summary_YYYYMMDD_HHMMSS.csv`
    + Εξετάστε το περιεχόμενο των αρχείων — ποια δεδομένα περιλαμβάνονται;
    + Γιατί χρησιμοποιείται το module `csv` αντί να γράφουμε τις γραμμές με f-strings; (Τι θα γινόταν αν το description περιείχε κόμμα;)

5. Error Handling και Rate Limits
    + Πώς μπορείτε να προσθέσετε αυτόματο retry μετά από 429; (δείτε την [Άσκηση 7](#άσκηση-7-retry-logic-και-logging))

<details>
<summary><b>Κώδικας</b></summary>

```python
import requests
import os
import csv
import json
from datetime import datetime

class WeatherAPI:
    def __init__(self, api_key=None, timeout=10):
        self.api_key = api_key or os.getenv('WEATHER_API_KEY')
        if not self.api_key:
            raise ValueError("Weather API key is required")

        self.base_url = 'https://api.openweathermap.org/data/2.5'
        self.session = requests.Session()
        self.timeout = timeout  # Session has no global timeout: pass it on every request

    def _make_request(self, endpoint, params=None):
        """Make authenticated request to weather API"""
        params = dict(params or {})  # Copy, so we don't modify the caller's dict

        params['appid'] = self.api_key
        params['units'] = 'metric'  # Celsius

        url = f"{self.base_url}/{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise Exception("Invalid API key") from e
            elif response.status_code == 404:
                raise Exception("City not found") from e
            elif response.status_code == 429:
                raise Exception("API rate limit exceeded") from e
            else:
                raise Exception(f"API error: {response.status_code}") from e

        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}") from e

    def _parse_current(self, data):
        """Extract the fields we need from a 'weather' response"""
        return {
            'city': data['name'],
            'country': data['sys']['country'],
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'description': data['weather'][0]['description'],
            'wind_speed': data['wind']['speed'],
            'visibility': data.get('visibility', 0) / 1000,  # km
            'timestamp': datetime.fromtimestamp(data['dt'])
        }

    def get_current_weather(self, city):
        """Get current weather for a city"""
        data = self._make_request('weather', {'q': city})
        return self._parse_current(data)

    def get_coordinates_weather(self, lat, lon):
        """Get weather by coordinates"""
        data = self._make_request('weather', {'lat': lat, 'lon': lon})
        return self._parse_current(data)

    def get_5_day_forecast(self, city):
        """Get 5-day weather forecast"""
        data = self._make_request('forecast', {'q': city})

        forecast = []
        for item in data['list']:
            forecast.append({
                'datetime': datetime.fromtimestamp(item['dt']),
                'temperature': item['main']['temp'],
                'description': item['weather'][0]['description'],
                'humidity': item['main']['humidity'],
                'wind_speed': item['wind']['speed']
            })

        return {
            'city': data['city']['name'],
            'country': data['city']['country'],
            'forecast': forecast
        }

def demo_weather_api():
    """Demonstrate weather API usage"""

    print("=== Weather API Demo ===")

    # Check for API key
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        print("⚠️  No API key found. Using mock data.")
        demo_without_api_key()
        return

    try:
        weather = WeatherAPI(api_key)

        # Test cities
        cities = ['Athens', 'London', 'Tokyo', 'New York']

        for city in cities:
            try:
                print(f"\n--- {city} Weather ---")
                current = weather.get_current_weather(city)

                print(f"🌍 {current['city']}, {current['country']}")
                print(f"🌡️  Temperature: {current['temperature']:.1f}°C")
                print(f"🌡️  Feels like: {current['feels_like']:.1f}°C")
                print(f"☁️  Conditions: {current['description'].title()}")
                print(f"💧 Humidity: {current['humidity']}%")
                print(f"🌪️  Wind: {current['wind_speed']:.1f} m/s")
                print(f"👁️  Visibility: {current['visibility']:.1f} km")
                print(f"🕒 Updated: {current['timestamp'].strftime('%Y-%m-%d %H:%M')}")

            except Exception as e:
                print(f"❌ Error fetching weather for {city}: {e}")

        # Weather by coordinates (Corfu)
        print("\n--- Weather by coordinates (39.62, 19.92) ---")
        try:
            current = weather.get_coordinates_weather(39.62, 19.92)
            print(f"🌍 {current['city']}: {current['temperature']:.1f}°C, {current['description']}")
        except Exception as e:
            print(f"❌ Error: {e}")

        # Get forecast for Athens
        print("\n=== 5-Day Forecast for Athens ===")
        try:
            forecast_data = weather.get_5_day_forecast('Athens')

            # Group by date
            daily_forecasts = {}
            for item in forecast_data['forecast']:
                date_key = item['datetime'].date()
                if date_key not in daily_forecasts:
                    daily_forecasts[date_key] = []
                daily_forecasts[date_key].append(item)

            # Show daily summary
            for date, forecasts in list(daily_forecasts.items())[:5]:
                temps = [f['temperature'] for f in forecasts]
                avg_temp = sum(temps) / len(temps)
                descriptions = [f['description'] for f in forecasts]
                most_common_desc = max(set(descriptions), key=descriptions.count)

                print(f"📅 {date.strftime('%A, %B %d')}")
                print(f"   🌡️  Avg: {avg_temp:.1f}°C (Range: {min(temps):.1f}-{max(temps):.1f}°C)")
                print(f"   ☁️  {most_common_desc.title()}")
                print()

        except Exception as e:
            print(f"❌ Forecast error: {e}")

    except Exception as e:
        print(f"❌ Weather API initialization failed: {e}")

def demo_without_api_key():
    """Demo with mock data when API key is not available"""

    print("=== Mock Weather Data Demo ===")

    mock_weather = {
        'Athens': {
            'city': 'Athens',
            'country': 'GR',
            'temperature': 22.5,
            'feels_like': 24.1,
            'humidity': 68,
            'description': 'partly cloudy',
            'wind_speed': 3.2,
            'visibility': 10.0
        },
        'London': {
            'city': 'London',
            'country': 'GB',
            'temperature': 15.2,
            'feels_like': 13.8,
            'humidity': 82,
            'description': 'overcast clouds',
            'wind_speed': 4.1,
            'visibility': 8.5
        }
    }

    for city, data in mock_weather.items():
        print(f"\n--- {city} Weather (Mock) ---")
        print(f"🌍 {data['city']}, {data['country']}")
        print(f"🌡️  Temperature: {data['temperature']}°C")
        print(f"🌡️  Feels like: {data['feels_like']}°C")
        print(f"☁️  Conditions: {data['description'].title()}")
        print(f"💧 Humidity: {data['humidity']}%")
        print(f"🌪️  Wind: {data['wind_speed']} m/s")

def save_weather_data():
    """Save weather data to files"""

    print("\n=== Save Weather Data ===")

    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        print("⚠️  API key required for data saving demo")
        return

    try:
        weather = WeatherAPI(api_key)

        # Collect data for multiple cities
        cities = ['Athens', 'Thessaloniki', 'Patras']
        all_weather_data = {}

        for city in cities:
            try:
                current = weather.get_current_weather(city)
                all_weather_data[city] = current
                print(f"✅ Collected data for {city}")
            except Exception as e:
                print(f"❌ Failed to collect data for {city}: {e}")

        if not all_weather_data:
            print("⚠️  No data collected - nothing to save")
            return

        # Same timestamp for both files
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save to JSON file
        filename = f"weather_data_{stamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_weather_data, f, indent=2, default=str, ensure_ascii=False)

        print(f"💾 Weather data saved to: {filename}")

        # Create CSV summary (the csv module handles commas/quotes in values)
        csv_filename = f"weather_summary_{stamp}.csv"
        with open(csv_filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['City', 'Country', 'Temperature', 'Humidity', 'Description', 'Wind Speed'])
            for data in all_weather_data.values():
                writer.writerow([data['city'], data['country'], data['temperature'],
                                 data['humidity'], data['description'], data['wind_speed']])

        print(f"📊 CSV summary saved to: {csv_filename}")

    except Exception as e:
        print(f"❌ Error saving weather data: {e}")

# Run demonstrations
demo_weather_api()
save_weather_data()

print("\n=== Setup Instructions ===")
print("1. Visit: https://openweathermap.org/api")
print("2. Sign up for free account")
print("3. Get API key from dashboard")
print("4. Set environment variable:")
print("   export WEATHER_API_KEY=your_key_here")
print("5. Re-run this script")
```

</details>

---

## **Άσκηση 5: CRUD Operations**
**Στόχος**: Χρήση όλων των HTTP μεθόδων (POST, GET, PUT, PATCH, DELETE) σε ένα RESTful API.

Χρησιμοποιούμε το [JSONPlaceholder](https://jsonplaceholder.typicode.com/), ένα δωρεάν *mock API* που δέχεται όλες τις μεθόδους **χωρίς να αποθηκεύει πραγματικά τις αλλαγές**.

1. Εκτελέστε το πρόγραμμα και καταγράψτε τον status code κάθε λειτουργίας. Συμφωνούν με τον πίνακα CRUD των διαφανειών; Ποια διαφορά εντοπίζετε στο `DELETE`;
2. Τι `id` παίρνει το νέο post; Τι γίνεται αν δημιουργήσετε δεύτερο;
3. Συγκρίνετε το αποτέλεσμα του `PUT` με του `PATCH`: ποια πεδία επιστρέφει το καθένα;
4. Μετά το `PUT`, το πρόγραμμα ξαναδιαβάζει το post με `GET`. Γιατί ο τίτλος δεν έχει αλλάξει;
5. Δοκιμάστε nested resources και φίλτρα:
    + `GET /posts/1/comments` — τα σχόλια του post 1
    + `GET /posts?userId=1` — τα posts του χρήστη 1 (με `params=`)
6. Τι επιστρέφει ένα `GET /posts/9999`; Πώς θα το χειριζόσασταν;

<details>
<summary><b>Κώδικας</b></summary>

```python
import requests

BASE_URL = 'https://jsonplaceholder.typicode.com'

def show(label, response):
    print(f"\n=== {label}: {response.request.method} {response.url} → {response.status_code} ===")
    print(response.json())

# CREATE (POST)
new_post = {
    'title': 'My New Post',
    'body': 'This is the content of my post',
    'userId': 1
}
response = requests.post(f'{BASE_URL}/posts', json=new_post, timeout=10)
show('CREATE', response)

# READ (GET)
response = requests.get(f'{BASE_URL}/posts/1', timeout=10)
show('READ', response)
post = response.json()

# UPDATE (PUT) - send the whole resource
post['title'] = 'Updated Title'
response = requests.put(f'{BASE_URL}/posts/1', json=post, timeout=10)
show('UPDATE', response)

# Read again: has it really changed?
response = requests.get(f'{BASE_URL}/posts/1', timeout=10)
print(f"\nTitle after PUT: {response.json()['title']}")

# PARTIAL UPDATE (PATCH) - send only the changed fields
response = requests.patch(f'{BASE_URL}/posts/1', json={'title': 'Patched Title'}, timeout=10)
show('PARTIAL UPDATE', response)

# DELETE
response = requests.delete(f'{BASE_URL}/posts/1', timeout=10)
show('DELETE', response)

# Nested resources & filters
response = requests.get(f'{BASE_URL}/posts/1/comments', timeout=10)
print(f"\nComments on post 1: {len(response.json())}")

response = requests.get(f'{BASE_URL}/posts', params={'userId': 1}, timeout=10)
print(f"Posts by user 1: {len(response.json())}")

# Resource that does not exist
response = requests.get(f'{BASE_URL}/posts/9999', timeout=10)
print(f"GET /posts/9999 → {response.status_code} {response.json()}")
```

</details>

---

## **Άσκηση 6: Authentication**
**Στόχος**: Χρήση των τριών τρόπων πιστοποίησης των διαφανειών: API Key, Basic Auth και Bearer Token.

1. **API Key**
    + Στην [Άσκηση 4](#άσκηση-4-weather-api) το API key στέλνεται ως query parameter (`appid`). Εκτυπώστε το `response.url`: τι κίνδυνο βλέπετε;
    + Στο πρόγραμμα εδώ, το key στέλνεται σε header (`X-API-Key`). Πού εμφανίζεται στην απάντηση του httpbin;
    + Γιατί διαβάζουμε το key από περιβαλλοντική μεταβλητή και δεν το γράφουμε στον κώδικα;

2. **Basic Auth** (`https://httpbin.org/basic-auth/user/passwd`)
    + Εκτελέστε με σωστά και με λάθος credentials. Ποιοι status codes επιστρέφονται;
    + Εκτυπώνεται το header `Authorization` που στάλθηκε. Αποκωδικοποιήστε το με `base64.b64decode()`. Τι συμπεραίνετε για την ασφάλεια χωρίς HTTPS;

3. **Bearer Token** (`https://httpbin.org/bearer`)
    + Εκτελέστε με και χωρίς token. Τι επιστρέφει ο server σε κάθε περίπτωση;
    + **Προαιρετικά — GitHub token**: δημιουργήστε ένα Personal Access Token (GitHub → Settings → Developer settings → Personal access tokens → Fine-grained, χωρίς επιπλέον δικαιώματα), ορίστε το ως `GITHUB_TOKEN` και ξανατρέξτε. Πώς αλλάζει το `X-RateLimit-Limit`; Τι επιστρέφει το `/user`;
    + ⚠️ Ποτέ μην ανεβάζετε token σε GitHub repository.

<details>
<summary><b>Κώδικας</b></summary>

```python
import base64
import os
import requests

print("=== 1. API Key in header ===")
api_key = os.getenv('MY_API_KEY', 'demo-key-123')  # Never hard-code real keys
response = requests.get('https://httpbin.org/headers',
                        headers={'X-API-Key': api_key}, timeout=10)
print(f"Server saw X-Api-Key: {response.json()['headers'].get('X-Api-Key')}")

print("\n=== 2. Basic Auth ===")
url = 'https://httpbin.org/basic-auth/user/passwd'

response = requests.get(url, auth=('user', 'passwd'), timeout=10)
print(f"Correct credentials: {response.status_code} {response.json()}")

auth_header = response.request.headers['Authorization']
print(f"Authorization header sent: {auth_header}")
encoded = auth_header.split()[1]
print(f"Decoded: {base64.b64decode(encoded).decode()}")

response = requests.get(url, auth=('user', 'wrong'), timeout=10)
print(f"Wrong credentials: {response.status_code}")

print("\n=== 3. Bearer Token (httpbin) ===")
response = requests.get('https://httpbin.org/bearer',
                        headers={'Authorization': 'Bearer my-test-token'}, timeout=10)
print(f"With token: {response.status_code} {response.json()}")

response = requests.get('https://httpbin.org/bearer', timeout=10)
print(f"Without token: {response.status_code}")

print("\n=== 3b. Bearer Token (GitHub, optional) ===")
token = os.getenv('GITHUB_TOKEN')
headers = {'Authorization': f'Bearer {token}'} if token else {}

response = requests.get('https://api.github.com/rate_limit', headers=headers, timeout=10)
core = response.json()['resources']['core']
print(f"Authenticated: {bool(token)} → limit {core['limit']}/hour, remaining {core['remaining']}")

if token:
    response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
    print(f"/user → {response.status_code}, login: {response.json().get('login')}")
else:
    print("Set GITHUB_TOKEN to try an authenticated request.")
```

</details>

---

## **Άσκηση 7: Retry Logic και Logging**
**Στόχος**: Ένας «ανθεκτικός» client που επαναλαμβάνει αιτήματα σε προσωρινά σφάλματα και καταγράφει τι συμβαίνει με το module `logging`.

1. Εκτελέστε το πρόγραμμα και παρακολουθήστε την έξοδο στο τερματικό και στο αρχείο `requests.log`.
2. Για κάθε URL του `test_urls` σημειώστε: πόσες προσπάθειες έγιναν και γιατί;
    + `/status/503` και `/status/429`: ποιος χρόνος αναμονής χρησιμοποιείται; Το httpbin δεν στέλνει `Retry-After` — τι κάνει τότε ο κώδικας;
    + `/status/404`: γιατί _δεν_ γίνεται retry;
    + `/delay/5` με `timeout=2`: ποια εξαίρεση προκαλείται;
3. Αλλάξτε το `level=logging.INFO` σε `logging.DEBUG`. Τι επιπλέον μηνύματα εμφανίζονται; (Προσέξτε και τα μηνύματα του `urllib3`.)
4. Γιατί η αναμονή διπλασιάζεται σε κάθε προσπάθεια (exponential backoff); Τι θα γινόταν αν χιλιάδες clients ξαναδοκίμαζαν όλοι αμέσως;
5. Το `Retry-After` μπορεί να είναι και ημερομηνία (π.χ. `Wed, 21 Oct 2026 07:28:00 GMT`). Τι θα συμβεί στο `int(...)`; Πώς θα το διορθώνατε;
6. Χρησιμοποιήστε τη συνάρτηση `api_call_with_retry()` στην [Άσκηση 1](#άσκηση-1-χρήση-github-api) αντί για το απλό `requests.get()`.

<details>
<summary><b>Κώδικας</b></summary>

```python
import logging
import time
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.FileHandler('requests.log', encoding='utf-8'), logging.StreamHandler()]
)
logger = logging.getLogger('lab03')

RETRYABLE = {429, 500, 502, 503, 504}

def api_call_with_retry(url, max_retries=3, timeout=10):
    for attempt in range(max_retries + 1):
        logger.info(f"GET {url} (attempt {attempt + 1}/{max_retries + 1})")
        try:
            response = requests.get(url, timeout=timeout)
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            if attempt == max_retries:
                logger.error(f"Giving up: {type(e).__name__}")
                raise
            wait = 2 ** attempt  # Exponential backoff: 1, 2, 4, ...
            logger.warning(f"{type(e).__name__}, retrying in {wait}s")
            time.sleep(wait)
            continue

        logger.debug(f"Response headers: {dict(response.headers)}")

        if response.status_code in RETRYABLE and attempt < max_retries:
            wait = int(response.headers.get('Retry-After', 2 ** attempt))
            logger.warning(f"Status {response.status_code}, retrying in {wait}s")
            time.sleep(wait)
            continue

        response.raise_for_status()  # Non-retryable 4xx/5xx, or retries exhausted
        logger.info(f"Status {response.status_code} in {response.elapsed.total_seconds():.2f}s")
        return response

test_urls = [
    ('https://httpbin.org/json', 10),
    ('https://httpbin.org/status/503', 10),
    ('https://httpbin.org/status/429', 10),
    ('https://httpbin.org/status/404', 10),
    ('https://httpbin.org/delay/5', 2),
]

for url, timeout in test_urls:
    logger.info("-" * 50)
    try:
        api_call_with_retry(url, max_retries=2, timeout=timeout)
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed: {e}")
```

</details>
