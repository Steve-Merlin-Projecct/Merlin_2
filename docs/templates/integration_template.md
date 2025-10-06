# Integration: [Service Name]

---
tags: [integration, external, api]
audience: [developers, ops]
last_updated: YYYY-MM-DD
next_review: YYYY-MM-DD
owner: [team_name]
status: [active, deprecated]
service_type: [external, internal]
---

## Overview
Brief description of the integration and its purpose in the system.

## Service Information
- **Service Name**: [External service name]
- **Service Type**: [REST API, GraphQL, SDK, etc.]
- **Documentation**: [Link to external documentation]
- **Support**: [Contact information or support channels]

## Authentication
- **Method**: [API Key, OAuth 2.0, JWT, etc.]
- **Configuration**: How authentication is configured
- **Credentials Storage**: Where credentials are stored (environment variables, etc.)

```bash
# Environment variables required
SERVICE_API_KEY=your_api_key_here
SERVICE_BASE_URL=https://api.service.com
```

## API Endpoints Used

### Endpoint 1: [Operation Name]
- **URL**: `GET /api/endpoint`
- **Purpose**: What this endpoint does
- **Request Format**:
  ```json
  {
    "parameter1": "value",
    "parameter2": "value"
  }
  ```
- **Response Format**:
  ```json
  {
    "result": "data",
    "status": "success"
  }
  ```

### Endpoint 2: [Operation Name]
- **URL**: `POST /api/endpoint`
- **Purpose**: What this endpoint does
- **Rate Limits**: Any rate limiting information

## Implementation Details

### Configuration
```python
# Configuration example
SERVICE_CONFIG = {
    'api_key': os.getenv('SERVICE_API_KEY'),
    'base_url': os.getenv('SERVICE_BASE_URL'),
    'timeout': 30,
    'retries': 3
}
```

### Error Handling
- **Common Errors**: List of typical error responses
- **Retry Logic**: How failures are handled
- **Fallback Behavior**: What happens when service is unavailable

### Code Example
```python
# Basic usage example
from integrations.service_client import ServiceClient

client = ServiceClient(config=SERVICE_CONFIG)
result = client.fetch_data(parameters)
```

## Data Flow
Describe how data flows between your system and the external service.

1. **Input**: What data is sent to the service
2. **Processing**: How the service processes the data
3. **Output**: What data is returned
4. **Storage**: How returned data is stored/used

## Monitoring & Alerts
- **Health Checks**: How service availability is monitored
- **Metrics**: Key metrics tracked (response time, success rate, etc.)
- **Alerts**: When alerts are triggered
- **Dashboards**: Links to monitoring dashboards

## Testing
- **Test Endpoints**: Any sandbox/test endpoints available
- **Test Data**: Sample test data
- **Mock Implementation**: How to mock for local development

## Troubleshooting

### Common Issues
1. **Issue**: Description of problem
   - **Cause**: Why it happens
   - **Solution**: How to fix it

2. **Issue**: Another common problem
   - **Cause**: Root cause
   - **Solution**: Resolution steps

### Debugging
```bash
# Useful debugging commands
curl -H "Authorization: Bearer $TOKEN" https://api.service.com/health
```

## Dependencies
- Required libraries/packages
- Minimum service version requirements
- Infrastructure dependencies

## Security Considerations
- Data privacy requirements
- Encryption in transit/at rest
- Access control requirements
- Compliance requirements (GDPR, etc.)

## Change Management
- How to handle API version updates
- Backward compatibility considerations
- Migration procedures for breaking changes

## Related Documentation
- [Link to internal API documentation]
- [Link to service's official documentation]
- [Link to troubleshooting guides]