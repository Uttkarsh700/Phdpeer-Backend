# API Guidelines

## REST API Conventions

### Endpoints
- Use plural nouns for resources: `/api/v1/users`, `/api/v1/timelines`
- Use HTTP methods appropriately:
  - GET: Retrieve resources
  - POST: Create resources
  - PUT/PATCH: Update resources
  - DELETE: Delete resources

### Response Format
```json
{
  "success": true,
  "data": {},
  "message": "Success message",
  "errors": []
}
```

### Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

### Authentication
- JWT tokens in Authorization header
- Format: `Authorization: Bearer <token>`

## Documentation
API documentation is automatically generated at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`

---
*This document will be expanded as API standards are established.*
