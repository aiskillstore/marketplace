# Advanced Configuration Topics

## Secrets Encryption

### Encryption Implementation

For highly sensitive environments, encrypt secrets at rest:

```python
# In your app
from scripts.env_helper import encrypt_secrets, decrypt_secrets

# Encrypt secrets file
encrypt_secrets('secrets.json', 'secrets.encrypted', 'your-encryption-password')

# Decrypt at runtime
secrets = decrypt_secrets('secrets.encrypted', 'your-encryption-password')
```

See `scripts/env_helper.py` for the complete encryption utilities implementation.

### Encryption Best Practices

1. **Key Management**
   - Store encryption passwords in secure key management systems
   - Rotate encryption keys regularly
   - Use different keys for different environments

2. **Storage**
   - Keep encrypted files in version control
   - Store decryption keys outside the codebase
   - Use environment variables for decryption keys

3. **Access Control**
   - Limit who can decrypt production secrets
   - Log all decryption attempts
   - Use time-limited access tokens

## Secret Rotation

### API Key Rotation Process

```python
def rotate_api_key(old_key: str, new_key: str):
    """
    Rotate API key gracefully.

    1. Add new key to environment
    2. Update all services to use new key
    3. Verify new key works
    4. Remove old key
    """
    # Load current config
    env_file = Path('.env')
    content = env_file.read_text()

    # Replace old key with new
    updated = content.replace(old_key, new_key)

    # Backup old config
    backup = Path('.env.backup')
    backup.write_text(content)

    # Write new config
    env_file.write_text(updated)

    print("✓ API key rotated. Backup saved to .env.backup")
```

### Rotation Checklist

- [ ] Generate new API key from provider
- [ ] Update .env file with new key
- [ ] Restart application with new key
- [ ] Verify new key works correctly
- [ ] Revoke old key at provider
- [ ] Remove backup file after verification
- [ ] Update team documentation

## Environment Variable Auditing

### Security Audit Function

```python
def audit_environment():
    """Audit environment variables for security issues."""
    issues = []

    # Check for default/example values
    dangerous_patterns = [
        'xxx',
        'example',
        'test123',
        'password',
        'changeme',
    ]

    for key, value in os.environ.items():
        if any(pattern in value.lower() for pattern in dangerous_patterns):
            issues.append(f"⚠ {key} appears to have a default/test value")

    # Check for required keys in production
    if os.getenv('APP_ENV') == 'production':
        required = ['SECRET_KEY', 'DATABASE_URL']
        for key in required:
            if not os.getenv(key):
                issues.append(f"❌ Required key {key} not set in production")

    if issues:
        print("Security Issues Found:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✓ No security issues detected")
```

### Regular Audit Schedule

Run security audits:
- Before every production deployment
- Weekly in staging environments
- After any configuration changes
- During security reviews

### Audit Checklist

- [ ] No default/example values in use
- [ ] All required variables set for environment
- [ ] No secrets in environment variable names
- [ ] Proper access controls on .env files
- [ ] No secrets logged or printed
- [ ] Backup configurations secured
- [ ] Team members have proper access levels

## Multi-Tenant Configuration

### Per-Tenant Settings

```python
class TenantConfig(Config):
    """Multi-tenant configuration support."""

    def __init__(self, tenant_id: str, env: str = None):
        self.tenant_id = tenant_id
        super().__init__(env)

    def _load_env_file(self):
        """Load tenant-specific configuration."""
        # Load base environment config
        super()._load_env_file()

        # Load tenant-specific overrides
        tenant_file = Path(f'.env.{self.env}.{self.tenant_id}')
        if tenant_file.exists():
            load_dotenv(tenant_file, override=True)
            print(f"✓ Loaded tenant config from {tenant_file}")

    @property
    def database_url(self) -> str:
        """Tenant-specific database URL."""
        return os.getenv(
            f'{self.tenant_id.upper()}_DATABASE_URL',
            os.getenv('DATABASE_URL')
        )


# Usage
config = TenantConfig(tenant_id='acme-corp', env='production')
```

### Tenant Isolation Patterns

1. **Database per Tenant**
   ```bash
   # .env.production.acme-corp
   ACME_CORP_DATABASE_URL=postgresql://host/acme_corp_db
   ```

2. **API Keys per Tenant**
   ```bash
   # .env.production.widget-inc
   WIDGET_INC_API_KEY=sk-xxx
   ```

3. **Feature Flags per Tenant**
   ```bash
   # .env.production.startup-xyz
   STARTUP_XYZ_ENABLE_BETA_FEATURES=true
   ```

## Configuration Versioning

### Versioned Config Pattern

```python
class VersionedConfig(Config):
    """Configuration with version tracking."""

    CONFIG_VERSION = "2.0.0"

    def __init__(self, env: str = None):
        super().__init__(env)
        self._check_version_compatibility()

    def _check_version_compatibility(self):
        """Verify config version matches application version."""
        env_version = os.getenv('CONFIG_VERSION', '1.0.0')

        if env_version != self.CONFIG_VERSION:
            print(f"⚠ Config version mismatch: expected {self.CONFIG_VERSION}, got {env_version}")
            print("  Consider updating .env file to latest version")

    @classmethod
    def migrate_from_v1(cls, old_config_path: Path):
        """Migrate configuration from version 1.x to 2.x."""
        old_content = old_config_path.read_text()
        new_content = old_content.replace(
            'OLD_VAR_NAME',
            'NEW_VAR_NAME'
        )
        # Add new required variables
        new_content += "\nCONFIG_VERSION=2.0.0\n"
        new_config_path = old_config_path.with_suffix('.env.v2')
        new_config_path.write_text(new_content)
        print(f"✓ Migrated config to {new_config_path}")
```

## Dynamic Configuration Reloading

### Hot Reload Support

```python
import signal
import threading
import time

class ReloadableConfig(Config):
    """Configuration that can be reloaded without restart."""

    def __init__(self, env: str = None, watch: bool = False):
        super().__init__(env)
        if watch:
            self._start_watcher()

    def _start_watcher(self):
        """Watch .env file for changes and reload."""
        def watch_loop():
            last_mtime = Path('.env').stat().st_mtime
            while True:
                time.sleep(5)  # Check every 5 seconds
                current_mtime = Path('.env').stat().st_mtime
                if current_mtime != last_mtime:
                    print("ℹ .env file changed, reloading...")
                    self._load_env_file()
                    last_mtime = current_mtime

        watcher_thread = threading.Thread(target=watch_loop, daemon=True)
        watcher_thread.start()

    def reload(self):
        """Manually reload configuration."""
        self._load_env_file()
        self._validate_required()
        print("✓ Configuration reloaded")


# Usage
config = ReloadableConfig(watch=True)

# Or manual reload
# config.reload()
```

## Configuration Templates

### Template Generation

```python
def generate_env_template(config_class: type, output_file: str = '.env.template'):
    """Generate .env.template from Config class properties."""
    template_lines = [
        "# Environment Configuration Template",
        f"# Generated from {config_class.__name__}",
        "",
    ]

    # Extract properties from config class
    for name, prop in vars(config_class).items():
        if isinstance(prop, property):
            env_var = name.upper()
            template_lines.append(f"{env_var}=")

    template_content = "\n".join(template_lines)
    Path(output_file).write_text(template_content)
    print(f"✓ Template written to {output_file}")
```

## Docker Integration

### Docker Compose with Env Files

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    env_file:
      - .env
      - .env.${APP_ENV:-development}
    environment:
      - APP_ENV=${APP_ENV:-development}
```

### Multi-Stage Docker Builds

```dockerfile
# Dockerfile
FROM python:3.11-slim as base

# Install UV
RUN pip install uv

# Development stage
FROM base as development
ENV APP_ENV=development
COPY .env.development /app/.env
WORKDIR /app
RUN uv sync

# Production stage
FROM base as production
ENV APP_ENV=production
# Don't copy .env files - use runtime env vars
WORKDIR /app
RUN uv sync --no-dev
```

### Runtime Environment Injection

```bash
# Run with environment variables
docker run -e APP_ENV=production \
           -e DATABASE_URL=$PROD_DB_URL \
           -e ANTHROPIC_API_KEY=$PROD_API_KEY \
           myapp:latest

# Or use env file
docker run --env-file .env.production myapp:latest
```

## Cloud Platform Integration

### AWS Secrets Manager

```python
import boto3
from botocore.exceptions import ClientError

def load_from_aws_secrets(secret_name: str, region: str = 'us-east-1') -> dict:
    """Load secrets from AWS Secrets Manager."""
    client = boto3.client('secretsmanager', region_name=region)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except ClientError as e:
        print(f"Error loading secret: {e}")
        return {}
```

### Google Cloud Secret Manager

```python
from google.cloud import secretmanager

def load_from_gcp_secrets(project_id: str, secret_id: str) -> str:
    """Load secret from Google Cloud Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode('UTF-8')
```

### Azure Key Vault

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def load_from_azure_keyvault(vault_url: str, secret_name: str) -> str:
    """Load secret from Azure Key Vault."""
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)

    secret = client.get_secret(secret_name)
    return secret.value
```
