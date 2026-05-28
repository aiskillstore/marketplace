# LabArchives Authentication Guide

## Prerequisites

### 1. Enterprise License

API access requires an enterprise LabArchives license. Contact your LabArchives administrator or email sales@labarchives.com to:
- Confirm your institution has enterprise access
- Request API access be enabled for your account
- Obtain institution-level API credentials

### 2. API Credentials

You need two sets of credentials:

#### Institution API Credentials (provided by LabArchives administrator)
- **Access Key ID**: Institution-level identifier
- **Access Password**: Institution-level secret key

#### User Authentication Credentials (self-configured)
- **Email**: Your LabArchives account email (e.g., researcher@university.edu)
- **External Applications Password**: Configured in your LabArchives account settings

## Setting Up External Applications Password

The external applications password is different from your regular LabArchives login password. It provides API access without exposing your main credentials.

**Steps to create an external applications password:**

1. Log in to your LabArchives account at mynotebook.labarchives.com (or your institution's dedicated URL)
2. Navigate to **Account Settings** (click your name in the top right)
3. Select the **Security & Privacy** tab
4. Find the **External Applications** section
5. Click **Generate New Password** or **Reset Password**
6. Copy and securely save this password (it will not be displayed again)
7. Use this password for all API authentication

**Security tip:** Treat this password like an API token. If compromised, regenerate it immediately from account settings.

## Configuration File Setup

Create a `config.yaml` file to securely store your credentials:

```yaml
# Regional API endpoint
api_url: https://api.labarchives.com/api

# Institution credentials (from administrator)
access_key_id: YOUR_ACCESS_KEY_ID_HERE
access_password: YOUR_ACCESS_PASSWORD_HERE

# User credentials (for user-specific operations)
user_email: researcher@university.edu
user_external_password: YOUR_EXTERNAL_APP_PASSWORD_HERE
```

**Alternative: Environment Variables**

For enhanced security, you can use environment variables instead of a configuration file:

```bash
export LABARCHIVES_API_URL="https://api.labarchives.com/api"
export LABARCHIVES_ACCESS_KEY_ID="your_key_id"
export LABARCHIVES_ACCESS_PASSWORD="your_access_password"
export LABARCHIVES_USER_EMAIL="researcher@university.edu"
export LABARCHIVES_USER_PASSWORD="your_external_app_password"
```

## Regional Endpoints

Please select the correct regional API endpoint based on your institution:

| Region | Endpoint | Applicable URL |
|--------|----------|--------------------------------|
| US/International | `https://api.labarchives.com/api` | `mynotebook.labarchives.com` |
| Australia | `https://auapi.labarchives.com/api` | `aunotebook.labarchives.com` |
| UK | `https://ukapi.labarchives.com/api` | `uknotebook.labarchives.com` |

Using the wrong regional endpoint will result in authentication failures even with correct credentials.

## Authentication Flow

### Option 1: Using labarchives-py Python Wrapper

```python
from labarchivespy.client import Client
import yaml

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize client with institution credentials
client = Client(
    config['api_url'],
    config['access_key_id'],
    config['access_password']
)

# Authenticate as specific user to get UID
login_params = {
    'login_or_email': config['user_email'],
    'password': config['user_external_password']
}
response = client.make_call('users', 'user_access_info', params=login_params)

# Parse response to extract UID
import xml.etree.ElementTree as ET
uid = ET.fromstring(response.content)[0].text
print(f"Authenticated as user ID: {uid}")
```

### Option 2: Using Python requests for Direct HTTP Requests

```python
import requests
import yaml

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Build API call
url = f"{config['api_url']}/users/user_access_info"
params = {
    'access_key_id': config['access_key_id'],
    'access_password': config['access_password'],
    'login_or_email': config['user_email'],
    'password': config['user_external_password']
}

# Make authentication request
response = requests.get(url, params=params)

if response.status_code == 200:
    print("Authentication successful!")
    print(response.content.decode('utf-8'))
else:
    print(f"Authentication failed: {response.status_code}")
    print(response.content.decode('utf-8'))
```

### Option 3: Using R Language

```r
library(httr)
library(xml2)

# Configuration
api_url <- "https://api.labarchives.com/api"
access_key_id <- "YOUR_ACCESS_KEY_ID"
access_password <- "YOUR_ACCESS_PASSWORD"
user_email <- "researcher@university.edu"
user_external_password <- "YOUR_EXTERNAL_APP_PASSWORD"

# Make authentication request
response <- GET(
    paste0(api_url, "/users/user_access_info"),
    query = list(
        access_key_id = access_key_id,
        access_password = access_password,
        login_or_email = user_email,
        password = user_external_password
    )
)

# Parse response
if (status_code(response) == 200) {
    content <- content(response, as = "text", encoding = "UTF-8")
    xml_data <- read_xml(content)
    uid <- xml_text(xml_find_first(xml_data, "//uid"))
    print(paste("Authenticated as user ID:", uid))
} else {
    print(paste("Authentication failed:", status_code(response)))
}
```

## OAuth Authentication (New Integration Projects)

LabArchives now uses OAuth 2.0 for new third-party integrations. Traditional API key authentication (as described above) will continue to work for direct API access.

**OAuth Flow (for app developers):**

1. Register your application with LabArchives
2. Obtain client ID and client secret
3. Implement OAuth 2.0 authorization code flow
4. Use authorization code to exchange for access token
5. Use access token for API requests

Contact LabArchives developer support for OAuth integration documentation.

## Authentication Troubleshooting

### 401 Unauthorized Error

**Possible causes and solutions:**

1. **Incorrect access_key_id or access_password**
   - Verify credentials with your LabArchives administrator
   - Check for typos or extra spaces in configuration file

2. **Incorrect external applications password**
   - Confirm you are using the external applications password, not regular login password
   - Regenerate external applications password in account settings

3. **API access not enabled**
   - Contact your LabArchives administrator to enable API access for your account
   - Confirm your institution has an enterprise license

4. **Wrong regional endpoint**
   - Confirm your api_url matches your institution's LabArchives instance
   - Check you are using the correct .com, .auapi, or .ukapi domain

### 403 Forbidden Error

**Possible causes and solutions:**

1. **Insufficient permissions**
   - Confirm your account role has necessary permissions
   - Check if you have access to specific notebooks (nbid)

2. **Account deactivated or expired**
   - Contact your LabArchives administrator to check account status

### Network and Connection Issues

**Firewall/Proxy Configuration:**

If your institution uses a firewall or proxy:

```python
import requests

# Configure proxy
proxies = {
    'http': 'http://proxy.university.edu:8080',
    'https': 'http://proxy.university.edu:8080'
}

# Make request through proxy
response = requests.get(url, params=params, proxies=proxies)
```

**SSL Certificate Verification:**

For self-signed certificates (not recommended for production):

```python
# Disable SSL verification (testing only)
response = requests.get(url, params=params, verify=False)
```

## Security Best Practices

1. **Never commit credentials to version control**
   - Add `config.yaml` to `.gitignore`
   - Use environment variables or secret management systems

2. **Rotate credentials regularly**
   - Change external applications password every 90 days
   - Regenerate API keys annually

3. **Use least privilege principle**
   - Request only necessary API permissions
   - Create separate API credentials for different applications

4. **Monitor API usage**
   - Review API access logs regularly
   - Set up alerts for unusual activity

5. **Secure storage**
   - Encrypt configuration files at rest
   - Use system keychain or secret management tools (e.g., AWS Secrets Manager, Azure Key Vault)

## Testing Authentication

Use the following script to verify your authentication setup:

```python
#!/usr/bin/env python3
"""Test LabArchives API authentication"""

from labarchivespy.client import Client
import yaml
import sys

def test_authentication():
    try:
        # Load configuration
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)

        print("Configuration loaded successfully")
        print(f"API URL: {config['api_url']}")

        # Initialize client
        client = Client(
            config['api_url'],
            config['access_key_id'],
            config['access_password']
        )
        print("Client initialized")

        # Test authentication
        login_params = {
            'login_or_email': config['user_email'],
            'password': config['user_external_password']
        }
        response = client.make_call('users', 'user_access_info', params=login_params)

        if response.status_code == 200:
            print("✅ Authentication successful!")

            # Extract UID
            import xml.etree.ElementTree as ET
            uid = ET.fromstring(response.content)[0].text
            print(f"User ID: {uid}")

            # Get user information
            user_response = client.make_call('users', 'user_info_via_id', params={'uid': uid})
            print("✅ User information retrieved successfully")

            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(response.content.decode('utf-8'))
            return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_authentication()
    sys.exit(0 if success else 1)
```

Run this script to confirm all configuration is correct:

```bash
python3 test_auth.py
```

## Getting Help

If authentication continues to fail after troubleshooting:

1. Contact your institutional LabArchives administrator
2. Email LabArchives support team: support@labarchives.com
3. Please include in your email:
   - Your institution name
   - Your LabArchives account email
   - Error message and response codes
   - Regional endpoint you are using
   - Programming language and library versions
