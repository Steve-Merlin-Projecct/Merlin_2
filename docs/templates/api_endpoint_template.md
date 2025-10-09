---
title: 'API Endpoint: [Endpoint Name]'
created: '2025-10-06'
updated: '2025-10-06'
author: Steve-Merlin-Projecct
type: template
status: active
tags:
- endpoint
- template
---

# API Endpoint: [Endpoint Name]

---
tags: [api, endpoint, reference]
audience: [developers, integrators]
last_updated: YYYY-MM-DD
next_review: YYYY-MM-DD
owner: [team_name]
status: [active, deprecated, beta]
version: [api_version]
---

## Endpoint Information
- **URL**: `[METHOD] /api/v1/endpoint/{id}`
- **Description**: Brief description of endpoint functionality
- **Version**: API version this endpoint was introduced
- **Authentication Required**: Yes/No

## Request

### HTTP Method
`[GET | POST | PUT | DELETE | PATCH]`

### URL Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Unique identifier for the resource |
| `param2` | string | No | Optional parameter description |

### Query Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 10 | Number of items to return (max 100) |
| `offset` | integer | No | 0 | Number of items to skip |
| `sort` | string | No | "created_at" | Sort field (created_at, updated_at, name) |
| `order` | string | No | "desc" | Sort order (asc, desc) |

### Headers
| Header | Required | Description |
|---------|----------|-------------|
| `Authorization` | Yes | Bearer token for authentication |
| `Content-Type` | Yes* | application/json (*required for POST/PUT) |
| `X-API-Version` | No | API version to use (defaults to latest) |

### Request Body
**Content Type**: `application/json`

```json
{
  "field1": "string",
  "field2": 123,
  "field3": {
    "nested_field": "value"
  },
  "field4": ["array", "of", "strings"]
}
```

#### Field Descriptions
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `field1` | string | Yes | max 255 chars | Description of field1 |
| `field2` | integer | Yes | min 1, max 1000 | Description of field2 |
| `field3.nested_field` | string | No | - | Description of nested field |
| `field4` | array[string] | No | max 10 items | Array description |

## Response

### Success Response
**HTTP Status**: `200 OK` (or `201 Created` for POST)

```json
{
  "status": "success",
  "data": {
    "id": 123,
    "field1": "value",
    "field2": 456,
    "created_at": "2025-08-07T10:30:00Z",
    "updated_at": "2025-08-07T10:30:00Z"
  },
  "meta": {
    "total": 1,
    "page": 1,
    "per_page": 10
  }
}
```

### Error Responses

#### 400 Bad Request
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "field1",
        "message": "field1 is required"
      }
    ]
  }
}
```

#### 401 Unauthorized
```json
{
  "status": "error",
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required"
  }
}
```

#### 403 Forbidden
```json
{
  "status": "error",
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "Insufficient permissions to access this resource"
  }
}
```

#### 404 Not Found
```json
{
  "status": "error",
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested resource was not found"
  }
}
```

#### 429 Too Many Requests
```json
{
  "status": "error",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 60 seconds."
  },
  "retry_after": 60
}
```

### Response Field Descriptions
| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Request status (success, error) |
| `data` | object | Response data (only present on success) |
| `meta` | object | Metadata about the response (pagination info, etc.) |
| `error` | object | Error details (only present on error) |

## Rate Limiting
- **Limit**: 100 requests per minute per API key
- **Headers**: Rate limit info in response headers
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

## Examples

### cURL Example
```bash
# GET request
curl -X GET \
  'https://api.example.com/api/v1/endpoint/123?limit=10&sort=name' \
  -H 'Authorization: Bearer your_token_here' \
  -H 'Content-Type: application/json'

# POST request
curl -X POST \
  'https://api.example.com/api/v1/endpoint' \
  -H 'Authorization: Bearer your_token_here' \
  -H 'Content-Type: application/json' \
  -d '{
    "field1": "example value",
    "field2": 123
  }'
```

### JavaScript Example
```javascript
// GET request
const response = await fetch('/api/v1/endpoint/123?limit=10', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  }
});
const data = await response.json();

// POST request
const response = await fetch('/api/v1/endpoint', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    field1: 'example value',
    field2: 123
  })
});
```

### Python Example
```python
import requests

# GET request
response = requests.get(
    'https://api.example.com/api/v1/endpoint/123',
    headers={'Authorization': f'Bearer {token}'},
    params={'limit': 10, 'sort': 'name'}
)
data = response.json()

# POST request
response = requests.post(
    'https://api.example.com/api/v1/endpoint',
    headers={'Authorization': f'Bearer {token}'},
    json={'field1': 'example value', 'field2': 123}
)
```

## Testing
- **Test Environment**: https://test-api.example.com
- **Test Authentication**: Use test API keys
- **Sample Data**: Available test data for this endpoint
- **Test Cases**: Link to automated test suite

## Changelog
- **v1.2**: Added field4 array parameter (2025-08-07)
- **v1.1**: Added pagination support (2025-07-15)
- **v1.0**: Initial release (2025-06-01)

## Related Endpoints
- [GET /api/v1/related-endpoint](./related-endpoint.md)
- [POST /api/v1/another-endpoint](./another-endpoint.md)

## Security Notes
- This endpoint processes sensitive data
- All requests are logged for security auditing
- Data is encrypted in transit and at rest