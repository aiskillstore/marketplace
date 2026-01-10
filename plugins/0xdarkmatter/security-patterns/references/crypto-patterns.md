# Cryptography Patterns

Secure cryptographic implementations.

## Symmetric Encryption

### AES-GCM (Recommended)

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def encrypt(plaintext: bytes, key: bytes) -> bytes:
    """Encrypt data with AES-GCM."""
    # Generate random 96-bit nonce
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)
    # Prepend nonce to ciphertext
    return nonce + ciphertext

def decrypt(data: bytes, key: bytes) -> bytes:
    """Decrypt AES-GCM encrypted data."""
    nonce = data[:12]
    ciphertext = data[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, associated_data=None)

# Generate a secure key
key = AESGCM.generate_key(bit_length=256)
```

### Fernet (Simple, Safe)

```python
from cryptography.fernet import Fernet

# Generate key
key = Fernet.generate_key()

# Encrypt
f = Fernet(key)
token = f.encrypt(b"secret message")

# Decrypt
plaintext = f.decrypt(token)
```

## Key Derivation

### PBKDF2

```python
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os

def derive_key(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """Derive encryption key from password."""
    if salt is None:
        salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,  # OWASP 2023 recommendation
    )
    key = kdf.derive(password.encode())
    return key, salt
```

### Argon2 for Key Derivation

```python
from argon2.low_level import hash_secret_raw, Type

def derive_key_argon2(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """Derive key using Argon2id."""
    if salt is None:
        salt = os.urandom(16)

    key = hash_secret_raw(
        secret=password.encode(),
        salt=salt,
        time_cost=3,
        memory_cost=65536,
        parallelism=4,
        hash_len=32,
        type=Type.ID,
    )
    return key, salt
```

## Hashing

### SHA-256 (Data Integrity)

```python
import hashlib

def hash_data(data: bytes) -> str:
    """Hash data for integrity checking."""
    return hashlib.sha256(data).hexdigest()

def verify_integrity(data: bytes, expected_hash: str) -> bool:
    """Verify data hasn't been modified."""
    return hashlib.sha256(data).hexdigest() == expected_hash
```

### HMAC (Message Authentication)

```python
import hmac
import hashlib

def create_signature(message: bytes, key: bytes) -> str:
    """Create HMAC signature."""
    return hmac.new(key, message, hashlib.sha256).hexdigest()

def verify_signature(message: bytes, signature: str, key: bytes) -> bool:
    """Verify HMAC signature (timing-safe)."""
    expected = hmac.new(key, message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

## Digital Signatures

### RSA Signatures

```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

# Generate key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096,
)
public_key = private_key.public_key()

def sign(message: bytes, private_key) -> bytes:
    """Sign message with RSA."""
    return private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

def verify(message: bytes, signature: bytes, public_key) -> bool:
    """Verify RSA signature."""
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except:
        return False
```

### Ed25519 (Modern Alternative)

```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

# Generate keys
private_key = Ed25519PrivateKey.generate()
public_key = private_key.public_key()

# Sign
signature = private_key.sign(message)

# Verify
try:
    public_key.verify(signature, message)
    print("Valid signature")
except:
    print("Invalid signature")
```

## Secure Random

```python
import secrets
import os

# Cryptographically secure random bytes
random_bytes = os.urandom(32)

# Secure token generation
token = secrets.token_hex(32)      # 64 hex chars
token = secrets.token_urlsafe(32)  # URL-safe base64
token = secrets.token_bytes(32)    # Raw bytes

# Secure random integer
pin = secrets.randbelow(1000000)   # 0-999999

# Secure random choice
selected = secrets.choice(options)
```

## Key Storage

### Environment Variables

```python
import os

# Load key from environment
key = os.environ.get('ENCRYPTION_KEY')
if not key:
    raise RuntimeError("ENCRYPTION_KEY not set")
key_bytes = bytes.fromhex(key)
```

### Key Management Service (AWS KMS)

```python
import boto3

kms = boto3.client('kms')

def encrypt_with_kms(plaintext: bytes, key_id: str) -> bytes:
    """Encrypt using AWS KMS."""
    response = kms.encrypt(
        KeyId=key_id,
        Plaintext=plaintext,
    )
    return response['CiphertextBlob']

def decrypt_with_kms(ciphertext: bytes) -> bytes:
    """Decrypt using AWS KMS."""
    response = kms.decrypt(CiphertextBlob=ciphertext)
    return response['Plaintext']
```

## Common Mistakes

### DON'T: Use ECB Mode

```python
# WRONG - ECB reveals patterns
cipher = Cipher(algorithms.AES(key), modes.ECB())

# CORRECT - Use GCM or CBC with HMAC
cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
```

### DON'T: Reuse Nonces/IVs

```python
# WRONG - Static IV
iv = b'1234567890123456'

# CORRECT - Random IV each time
iv = os.urandom(16)
```

### DON'T: Roll Your Own Crypto

```python
# WRONG - Custom encryption
def encrypt(data, key):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

# CORRECT - Use established libraries
from cryptography.fernet import Fernet
```

### DON'T: Use MD5 or SHA1 for Security

```python
# WRONG - Weak hash
import hashlib
hash = hashlib.md5(password.encode())

# CORRECT - Use bcrypt for passwords
import bcrypt
hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

## Quick Reference

| Purpose | Algorithm | Library |
|---------|-----------|---------|
| Password hashing | bcrypt, Argon2 | `bcrypt`, `argon2-cffi` |
| Symmetric encryption | AES-256-GCM | `cryptography` |
| Key derivation | PBKDF2, Argon2 | `cryptography`, `argon2` |
| Data integrity | SHA-256 | `hashlib` |
| Message auth | HMAC-SHA256 | `hmac` |
| Digital signatures | Ed25519, RSA-PSS | `cryptography` |
| Random bytes | CSPRNG | `secrets`, `os.urandom` |
