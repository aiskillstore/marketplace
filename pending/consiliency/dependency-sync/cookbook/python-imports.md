# Python Import Mapping Cookbook

Map Python import statements to correct PyPI package names.

## Standard Library Exclusions

These imports are part of Python's standard library and should NOT be installed:

```
os, sys, re, json, pathlib, typing, collections, itertools, functools,
datetime, time, math, random, copy, io, subprocess, shutil, tempfile,
contextlib, dataclasses, enum, abc, inspect, importlib, asyncio,
unittest, logging, argparse, configparser, csv, sqlite3, hashlib,
secrets, base64, uuid, urllib, http, html, xml, email, mimetypes,
socket, ssl, select, threading, multiprocessing, concurrent, queue,
struct, codecs, string, textwrap, difflib, pprint, reprlib, traceback,
warnings, weakref, types, operator, heapq, bisect, array, decimal,
fractions, statistics, zlib, gzip, bz2, lzma, zipfile, tarfile,
pickle, shelve, dbm, platform, ctypes, signal, locale, gettext
```

## Import-to-Package Mappings

| Import Name | PyPI Package | Notes |
|-------------|--------------|-------|
| `PIL` | `pillow` | Python Imaging Library fork |
| `cv2` | `opencv-python` | OpenCV bindings |
| `yaml` | `pyyaml` | YAML parser |
| `sklearn` | `scikit-learn` | Machine learning |
| `bs4` | `beautifulsoup4` | HTML/XML parsing |
| `dateutil` | `python-dateutil` | Date utilities |
| `dotenv` | `python-dotenv` | Environment variables |
| `jwt` | `pyjwt` | JSON Web Tokens |
| `magic` | `python-magic` | File type detection |
| `serial` | `pyserial` | Serial port access |
| `usb` | `pyusb` | USB device access |
| `gi` | `pygobject` | GObject introspection |
| `cairo` | `pycairo` | Cairo graphics |
| `Crypto` | `pycryptodome` | Cryptography (legacy) |
| `cryptography` | `cryptography` | Cryptography (modern) |
| `nacl` | `pynacl` | NaCl bindings |
| `google.cloud` | `google-cloud-*` | GCP libraries (detect specific) |
| `boto3` | `boto3` | AWS SDK |
| `azure` | `azure-*` | Azure SDK (detect specific) |

## Framework-Specific Mappings

### Web Frameworks

| Import | Package | Category |
|--------|---------|----------|
| `fastapi` | `fastapi` | Backend |
| `flask` | `flask` | Backend |
| `django` | `django` | Backend |
| `starlette` | `starlette` | Backend |
| `uvicorn` | `uvicorn` | ASGI server |
| `gunicorn` | `gunicorn` | WSGI server |
| `hypercorn` | `hypercorn` | ASGI server |

### Database

| Import | Package | Category |
|--------|---------|----------|
| `asyncpg` | `asyncpg` | PostgreSQL async |
| `psycopg2` | `psycopg2-binary` | PostgreSQL sync |
| `psycopg` | `psycopg[binary]` | PostgreSQL 3.x |
| `sqlalchemy` | `sqlalchemy` | ORM |
| `alembic` | `alembic` | Migrations |
| `pymongo` | `pymongo` | MongoDB |
| `motor` | `motor` | MongoDB async |
| `redis` | `redis` | Redis sync |
| `aioredis` | `redis` | Redis async (now in redis pkg) |
| `prisma` | `prisma` | Prisma client |

### Testing

| Import | Package | Type |
|--------|---------|------|
| `pytest` | `pytest` | dev |
| `pytest_asyncio` | `pytest-asyncio` | dev |
| `pytest_cov` | `pytest-cov` | dev |
| `hypothesis` | `hypothesis` | dev |
| `faker` | `faker` | dev |
| `factory_boy` | `factory-boy` | dev |
| `responses` | `responses` | dev |
| `httpx` | `httpx` | dev (if used for testing) |
| `respx` | `respx` | dev |

### Data Science

| Import | Package | Notes |
|--------|---------|-------|
| `numpy` | `numpy` | |
| `np` (alias) | `numpy` | Common alias |
| `pandas` | `pandas` | |
| `pd` (alias) | `pandas` | Common alias |
| `matplotlib` | `matplotlib` | |
| `plt` (alias) | `matplotlib` | pyplot alias |
| `seaborn` | `seaborn` | |
| `sns` (alias) | `seaborn` | Common alias |
| `scipy` | `scipy` | |
| `torch` | `torch` | PyTorch |
| `tensorflow` | `tensorflow` | |
| `tf` (alias) | `tensorflow` | Common alias |

## Detection Algorithm

```python
def map_import_to_package(import_name: str) -> str | None:
    """Map Python import to PyPI package name."""

    # Skip standard library
    if import_name in STDLIB:
        return None

    # Check known mappings
    if import_name in MAPPINGS:
        return MAPPINGS[import_name]

    # Handle submodule imports (e.g., google.cloud.storage)
    root = import_name.split('.')[0]
    if root in MAPPINGS:
        return MAPPINGS[root]

    # Default: assume import name == package name
    # (works for most packages: requests, httpx, pydantic, etc.)
    return import_name
```

## Package Manager Commands

### UV (Recommended)

```bash
# Add production dependency
uv add <package>

# Add development dependency
uv add --dev <package>

# Add with version constraint
uv add "<package>>=1.0.0"

# Add multiple packages
uv add package1 package2 package3
```

### Poetry

```bash
# Add production dependency
poetry add <package>

# Add development dependency
poetry add --group dev <package>
```

### Pip (requirements.txt)

```bash
# Install and freeze
pip install <package>
pip freeze > requirements.txt

# Or append manually
echo "<package>>=1.0.0" >> requirements.txt
```
