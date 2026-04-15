# eSIM Access API Reference

## Base URL

```
https://api.esimaccess.com/api/v1/open
```

## Authentication

All endpoints are POST. Every request requires HMAC-SHA256 signed headers.

### Required Headers

| Header | Value |
|--------|-------|
| Content-Type | application/json |
| RT-AccessCode | Your API access code |
| RT-Timestamp | Unix timestamp in milliseconds (`Date.now()`) |
| RT-RequestID | Unique UUID per request (`crypto.randomUUID()`) |
| RT-Signature | HMAC-SHA256 signature (lowercase hex) |

### Signature Algorithm

The accessCode serves as both the API identifier and the HMAC signing key.

```
signatureString = timestamp + requestId + accessCode + requestBody
signature = HMAC-SHA256(signatureString, accessCode).toLowerCase()
```

### Node.js Implementation

```javascript
import crypto from 'crypto';

function generateHeaders(accessCode, body) {
  const timestamp = Date.now().toString();
  const requestId = crypto.randomUUID();
  const signStr = timestamp + requestId + accessCode + body;
  const signature = crypto
    .createHmac('sha256', accessCode)
    .update(signStr)
    .digest('hex')
    .toLowerCase();

  return {
    'Content-Type': 'application/json',
    'RT-AccessCode': accessCode,
    'RT-Timestamp': timestamp,
    'RT-RequestID': requestId,
    'RT-Signature': signature,
  };
}
```

### Python Implementation

```python
import hashlib, hmac, json, time, uuid, requests

def generate_headers(access_code, body):
    timestamp = str(int(time.time() * 1000))
    request_id = str(uuid.uuid4())
    sign_str = timestamp + request_id + access_code + body
    signature = hmac.new(
        access_code.encode(), sign_str.encode(), hashlib.sha256
    ).hexdigest().lower()

    return {
        "Content-Type": "application/json",
        "RT-AccessCode": access_code,
        "RT-Timestamp": timestamp,
        "RT-RequestID": request_id,
        "RT-Signature": signature,
    }

def api_call(access_code, endpoint, body=None):
    if body is None:
        body = {}
    body_str = json.dumps(body)
    url = f"https://api.esimaccess.com/api/v1/open{endpoint}"
    headers = generate_headers(access_code, body_str)
    response = requests.post(url, headers=headers, data=body_str)
    return response.json()

# Example: check balance
result = api_call("YOUR_ACCESS_CODE", "/balance/query")
print(f"Balance: ${result['obj']['balance'] / 10000:.2f} USD")
```

---

## Data Formats

### Prices

API prices are multiplied by 10,000. Divide to get USD.

```
18000 in API  = $1.80 USD
150000000     = $15,000.00 USD
```

### Volumes

Data volumes are in bytes.

```
1073741824 bytes = 1 GB
104857600 bytes  = 100 MB
```

---

## Endpoints

### POST /balance/query

Check account balance.

**Request:** `{}`

**Response:**
```json
{
  "success": true,
  "errorCode": "0",
  "errorMsg": null,
  "obj": { "balance": 2230180 }
}
```

Balance is in API price format (divide by 10,000 for USD).

---

### POST /package/list

List available eSIM packages. All filter fields are optional (use empty string to skip).

**Request:**
```json
{
  "locationCode": "US",
  "type": "",
  "slug": "",
  "packageCode": "",
  "iccid": ""
}
```

- `locationCode`: Country code filter (e.g., "US", "JP", "TH")
- `iccid`: Pass an ICCID to find compatible top-up packages
- All fields empty = return all packages

**Response:**
```json
{
  "success": true,
  "obj": {
    "packageList": [
      {
        "packageCode": "US_5_30",
        "slug": "us_5_30",
        "name": "United States 5GB 30Days",
        "price": 88000,
        "retailPrice": 120000,
        "currencyCode": "USD",
        "volume": 5368709120,
        "duration": 30,
        "durationUnit": "DAY",
        "location": "US",
        "speed": "5G/LTE",
        "supportTopUpType": 2,
        "activeType": 1,
        "locationNetworkList": [...]
      }
    ]
  }
}
```

Key fields:
- `supportTopUpType`: 2 = supports top-ups
- `activeType`: 1 = standard activation

---

### POST /esim/order

Create a new eSIM order.

**Request:**
```json
{
  "transactionId": "unique_transaction_id_123",
  "packageInfoList": [
    {
      "packageCode": "US_5_30",
      "count": 1,
      "periodNum": 7
    }
  ]
}
```

- `transactionId`: Must be unique per order (prevents duplicates)
- `periodNum`: Required only for daily plans (number of days)

**Response:**
```json
{
  "success": true,
  "obj": {
    "orderNo": "B26041021130002",
    "transactionId": "unique_transaction_id_123"
  }
}
```

After creating an order, poll `/esim/query` with the `orderNo` to get the ICCID (typically available within 3-10 seconds).

---

### POST /esim/query

Query eSIM details by order number or ICCID.

**Request:**
```json
{
  "orderNo": "B26041021130002",
  "iccid": "",
  "pager": { "pageNum": 1, "pageSize": 20 }
}
```

Can query by `orderNo` or `iccid` (use one, leave other empty).

**Response:**
```json
{
  "success": true,
  "obj": {
    "esimList": [
      {
        "esimTranNo": "26041021130002",
        "orderNo": "B26041021130002",
        "transactionId": "unique_transaction_id_123",
        "imsi": "454031073362981",
        "iccid": "89852240810733629810",
        "smsStatus": 0,
        "msisdn": "",
        "ac": "",
        "qrCodeUrl": "https://p.qrsim.net/xxx.png",
        "shortUrl": "https://p.qrsim.net/xxx",
        "smdpStatus": "RELEASED",
        "eid": "",
        "activeType": 1,
        "dataType": 0,
        "activateTime": null,
        "expiredTime": "2026-10-07T21:13:01+0000",
        "totalVolume": 5368709120,
        "totalDuration": 30,
        "durationUnit": "DAY",
        "orderUsage": 0,
        "esimStatus": "GOT_RESOURCE",
        "packageList": [
          {
            "packageName": "United States 5GB 30Days",
            "packageCode": "US_5_30",
            "slug": "us_5_30",
            "duration": 30,
            "volume": 5368709120,
            "locationCode": "US",
            "createTime": "2026-04-10T21:13:01+0000"
          }
        ]
      }
    ],
    "pager": { "pageSize": 20, "pageNum": 1, "total": 1 }
  }
}
```

---

### POST /esim/topup

Apply a top-up package to an existing eSIM.

**Request:**
```json
{
  "esimTranNo": "26041021130002",
  "iccid": "",
  "packageCode": "US_5_30",
  "transactionId": "topup_unique_id_456"
}
```

- Use `esimTranNo` (not ICCID) to identify the eSIM
- `iccid` should be empty string
- No dedicated webhook for top-ups; verify success via API response

---

### POST /esim/cancel

Cancel an unused eSIM. Only works if eSIM status is RELEASED/GOT_RESOURCE (not yet activated). Provides automatic balance refund.

**Request:**
```json
{ "esimTranNo": "26041021130002" }
```

---

### POST /esim/revoke

Permanently revoke an eSIM profile. Works on activated eSIMs. No refund. Use as fallback when cancel fails.

**Request:**
```json
{ "esimTranNo": "26041021130002" }
```

---

### POST /esim/suspend

Temporarily suspend an eSIM profile. Only works on activated eSIMs.

**Request:**
```json
{ "esimTranNo": "26041021130002" }
```

---

### POST /esim/unsuspend

Re-enable a suspended eSIM profile.

**Request:**
```json
{ "esimTranNo": "26041021130002" }
```

---

### POST /esim/usage/query

Query data usage for eSIMs.

**Request:**
```json
{ "esimTranNoList": ["26041021130002"] }
```

Note: Requires `esimTranNoList` (array), not ICCID.

---

### POST /esim/sendSms

Send SMS to an eSIM profile (if supported by the plan).

**Request:**
```json
{
  "iccid": "89852240810733629810",
  "message": "Your message here"
}
```

Note: Field is `message`, not `content`. Only works on activated eSIMs.

---

### POST /webhook/save

Configure a webhook URL for receiving notifications.

**Request:**
```json
{ "webhookUrl": "https://example.com/webhooks" }
```

---

### POST /webhook/query

Query current webhook configuration.

**Request:** `{}`

**Response:**
```json
{
  "success": true,
  "obj": { "webhook": "https://example.com/webhooks" }
}
```

---

## eSIM Status States

Two fields determine eSIM status: `smdpStatus` (installation) and `esimStatus` (usage).

| State | smdpStatus | esimStatus | orderUsage | eid |
|-------|-----------|------------|------------|-----|
| New | RELEASED | GOT_RESOURCE | 0 | empty |
| Onboard | ENABLED | IN_USE / GOT_RESOURCE | 0 | present |
| In Use | ENABLED / DISABLED | IN_USE | > 0 | present |
| Depleted | ENABLED / DISABLED | USED_UP | > 0 | present |
| Deleted | DELETED | * | > 0 | present |

---

## Webhook Notification Types

| Type | Trigger | Notes |
|------|---------|-------|
| ORDER_STATUS | eSIM provisioned | Must query API for ICCID (not in payload) |
| ESIM_STATUS | Device enable/disable | Contains smdpStatus + esimStatus |
| SMDP_EVENT | Installation lifecycle | DOWNLOAD, INSTALLATION, ENABLED |
| DATA_USAGE | Usage threshold reached | 1-3 hour delay, not real-time |
| VALIDITY_USAGE | 1 day until expiry | Cannot top up after expiry |
| CHECK_HEALTH | Webhook setup verification | One-time on initial setup |

Webhook sender IPs (whitelist): `3.1.131.226`, `54.254.74.88`, `18.136.190.97`, `18.136.60.197`, `18.136.19.137`

---

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200002 | Status doesn't support action | eSIM not in correct state for operation |
| 200007 | Balance insufficient | Add funds to account |
| 310402 | Duplicate transactionId | Order already exists |
| 400001 | Invalid parameters | Check request format |
| 401001 | Authentication failed | Verify credentials and signature |
| 000105 | Validation error | Check required fields in request body |
